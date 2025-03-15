import asyncio
import itertools
import os
from pathlib import Path
import time
import re
import shutil
import subprocess
import threading
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread, QFileSystemWatcher, QTimer,QProcessEnvironment
import psutil
import glob

import qasync
from utils import start_process
from _data import DIRECTORY, UserConfig, configs, settings, Settings, GOODBYE_DPI_PATH, ZAPRET_PATH, GOODCHECK_PATH, DEBUG_PATH, DEBUG
from .chkPresetUtils import GGC_SERVER, Options, ServerAvailabilityChecker
from .process import Process
ENGINE = {
    "GoodbyeDPI":"gdpi",
    "Zapret":"zapret"
}

CHECKLISTS = ["default - all", "default - googlevideo", "default - miscellaneous", "empty", "twitter"]

goodbyeDPI_strategies = [
    "[basic functionality test]",
    "[IPv4] - [e1 + e2 + e4] - [LONG]",
    "[IPv4] - [e1 + e2 + e4] - [SHORT]",
    "[IPv4] - [e1] - [LONG]",
    "[IPv4] - [e1] - [SHORT]",
    "[IPv4] - [e2] - [LONG]",
    "[IPv4] - [e2] - [SHORT]",
    "[IPv4] - [e4] - [LONG]",
    "[IPv4] - [e4] - [SHORT]",
    "[IPv6] - [e1 + e2 + e4] - [LONG]",
    "[IPv6] - [e1 + e2 + e4] - [SHORT]",
    "[IPv6] - [e1] - [LONG]",
    "[IPv6] - [e1] - [SHORT]",
    "[IPv6] - [e2] - [LONG]",
    "[IPv6] - [e2] - [SHORT]",
    "[IPv6] - [e4] - [LONG]",
    "[IPv6] - [e4] - [SHORT]",
    ]
zapret_strategies = [
    "[IPv4] - [TCP] - [No wssize, NO syndata]",
    "[IPv4] - [UDP]",
    "[IPv6] - [UDP]",
]

byedpi_strategies = [
    "[TCP] - [IPv4]"
]

def parse_all_data(text: str) -> tuple:
    '''
    Used for convert GoodCheck results to tuple.
    Example output:
    ```
    tuple[dict[str, list], list]
    ```
    '''
    pattern = r"RESULTS BY URL.*?\n(.*?)\n-.*?RESULTS BY STRATEGY.*?-\n(.*?)\n-.*?INFORMATION"
    blocks = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if not blocks:
        return {}, []

    website_section, strategy_section = blocks[0]
    
    urls_pattern = r'(URLs with NO successes:\n(.*?)\n)?(URLs with successes:\n(.*?))?\Z'
    urls_blocks = re.findall(urls_pattern, website_section, re.DOTALL | re.IGNORECASE)
    
    if not urls_blocks:
        return {}, []

    urls_failure = []
    urls_success = []
    if urls_blocks[0][1] != '':
        urls_failure_blocks = urls_blocks[0][1].strip().split("\n")
        for url in urls_failure_blocks:
            url_parts = url.split("|")
            if len(url_parts) >= 2:
                urls_failure.append({
                    'url': url_parts[0].strip(),
                    'ip': url_parts[1].replace('IP:', '').strip()
                })
    if urls_blocks[0][3] != '':
        urls_success_blocks = urls_blocks[0][3].strip().split("\n")
        for url in urls_success_blocks:
            url_parts = url.split("|")
            if len(url_parts) >= 3:
                _strategy = url_parts[2].replace('Best strategy:', '')
                strategy = _strategy.replace('[', '').replace(']', '').strip()
                urls_success.append({
                    'url': url_parts[0].strip(),
                    'ip': url_parts[1].replace('IP:', '').strip(),
                    'best': strategy
                })
    
    urls = {
        'failure': urls_failure,
        'success': urls_success
    }
    
    strategies_pattern = r'Strategies with (\d*/\d*) successes:\n(.*?)\n\s'
    strategies_blocks = re.findall(strategies_pattern, strategy_section+'\n', re.DOTALL | re.IGNORECASE)
    
    strategies = []
    for block in strategies_blocks:
        success_count, all_count = block[0].split("/")
        strategy_list = block[1].replace('[', '').replace(']', '').strip().split("\n")
        strategies.append({
            'success': int(success_count),
            'all': int(all_count),
            'strategies': strategy_list,
        })
    
    strategies = sorted(strategies, key=lambda x: x['success'], reverse=True)
    return urls, strategies

def chk_preset_configure_options(config:UserConfig):
    options = Options(
        tcp_port=config.get_value('tcp_port'),
        tcp_timeout=config.get_value('tcp_timeout'),
        udp_port=config.get_value('udp_port'),
        udp_timeout=config.get_value('udp_timeout'),
        ggc_count=config.get_value('ggc_count'),
        ggc_timeout=config.get_value('ggc_timeout'),
        immediate_output=True,
    )
    return options

CHKPRESET_CONFIG_EXAMPLE = {
    "tcp_hosts": 0,
    "tcp_port": 443,
    "tcp_timeout": 300,
    "udp_hosts": "",
    "udp_port": 443,
    "udp_timeout": 300,
    "ggc_hosts": "",
    "ggc_count": 1,
    "ggc_timeout": 300,
    "FakeSNI": "fonts.google.com",
    "FakeHexStreamTCP": "",
    "FakeHexStreamUDP": "",
    "FakeHexBytesTCP": "",
    "FakeHexBytesUDP": "",
    "PayloadTCP": "Payloads\\default_tcp.bin",
    "PayloadUDP": "Payloads\\default_udp.bin",
    "strategy": 0
}

def reload_chk_preset_config(config:UserConfig|None) -> UserConfig:
    config_path = Path(DEBUG_PATH+DIRECTORY, 'data', 'settings', 'chkpreset.json')
    if config:
        config.reload_config()
        return config
    if not os.path.exists(config_path):
        os.makedirs(config_path.parent, exist_ok=True)
        with open(config_path, "w") as f:
            f.write("{}")
            
        config = UserConfig(config_path)
        for i, item in enumerate(CHKPRESET_CONFIG_EXAMPLE.items()):
            key, value = item
            config.set_value(key, value)
        
    else:
        config = UserConfig(config_path)
        
    return config

class GoodCheckHelper(QObject):
    output_signal = Signal(str)
    process_finished_signal = Signal()
    started = Signal()
    process_stopped_signal = Signal()
    consoleCloseRequest = Signal()
    current_strategy_check_changed = Signal(int, int)

    def __init__(self, process:Process):
        super().__init__()
        self.settings = Settings(GOODCHECK_PATH + "/config.ini", space_around_delimiters=False)
        self._process = process
        self.process = None
        self.log_watcher = QFileSystemWatcher()
        self.log_file_path = None
        self.last_log_size = 0
        self.log_monitor_timer = QTimer()
        self.log_monitor_timer.setInterval(100) 
        self.log_monitor_timer.timeout.connect(self.read_new_log_content)
        self.output = ""
        self.sitelist = None
        self.parsed_data = None
        self.strategy_list = None
        
        self.chk_preset = None
        self.config = reload_chk_preset_config(None)
        
    def parse_data(self):
        if (self.parsed_data is None or self.parsed_data == ({}, [])) and self.output:
            self.parsed_data = parse_all_data(self.output)
        return self.parsed_data if self.parsed_data else ({}, [])
    
    @Slot(result=bool)
    def is_data_ready(self):
        _empty = ({}, [])
        return True if self.parse_data() != _empty else False
    
    @Slot(result=str)
    def get_check_engine_name(self):
        _engine = configs['goodcheck'].get_value("engine")
        return 'goodbyeDPI' if _engine == 'GoodbyeDPI' else _engine
        
    @Slot(result='QVariantList')
    def get_sitelist(self):
        if self.sitelist is None:
            self.sitelist = self.parse_data()[0]
        return [self.sitelist]
    
    @Slot(result='QVariantList')
    def get_strategy_list(self):
        if self.strategy_list is None:
            self.strategy_list = self.parse_data()[1]
        return self.strategy_list
        
    @Slot()
    def close_console(self):
        self.consoleCloseRequest.emit()
        
    @Slot(result=str)
    def get_output(self):
        return self.output
    
    @Slot(str, str)
    def set_chk_preset_value(self, key, value):
        self.config.set_value(key, value)
        
    @Slot(str, int)
    def set_chk_preset_int_value(self, key, value):
        self.config.set_value(key, value)
    
    @Slot(str, result=str)
    def get_chk_preset_value(self, key):
        return self.config.get_value(key)
    
    @Slot(str, result=int)
    def get_chk_preset_int_value(self, key):
        return self.config.get_value(key)

    @Slot(int)
    def open_goodcheck_file(self, file):
        os.startfile(DEBUG_PATH + f"{GOODCHECK_PATH}/CheckLists/{CHECKLISTS[file] + '.txt'}")
        
    @Slot(str, str, str)
    def set_value(self, group, key, value):
        print(key)
        self.settings.change_setting(group, key, value)
        self.settings.save_settings()

    @Slot(str, str, result=str)
    def get_value(self, group, key):
        return self.settings.get_value(group, key)

    @Slot(str, str, result=bool)
    def get_bool(self, group, key):
        return True if self.settings.get_value(group, key) == "true" else False
    
    @Slot(result=bool)
    def is_chk_preset_alive(self):
        return self.thread is QThread and self.thread.isRunning()
    
    @Slot(result=bool)
    def is_process_alive(self):
        return True if self.process else False

    @Slot(str)
    def start(self, engine:str):
        self.output = ""
        self.sitelist = None
        self.parsed_data = None
        self.strategy_list = None
        
        if engine.lower() in ['zapret', 'goodbyedpi']:
            self.settings.change_setting("GoodbyeDPI", "GoodbyeDPIFolder", "..\\\\goodbyeDPI")
            self.settings.change_setting("GoodbyeDPI", "GoodbyeDPIExecutableName", "gdpi.exe")
            self.settings.change_setting("GoodbyeDPI", "GoodbyeDPIServiceNames", "goodbyedpi")
            self.settings.change_setting("Zapret", "ZapretFolder", "..\\\\zapret")
            self.settings.change_setting("ByeDPI", "ByeDPIFolder", "..\\\\byedpi")
            
            if os.path.exists(DIRECTORY+"data/goodbyeDPI/x86_64/goodbyedpi.exe"):
                shutil.copy(DIRECTORY+"data/goodbyeDPI/x86_64/goodbyedpi.exe", DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe")

            self.settings.save_settings()
            configs['goodcheck'].reload_config()

            log_pattern = os.path.join(GOODCHECK_PATH+"/Logs", "logfile_GoodCheckGoGo_*.log")
            for log_file in glob.glob(log_pattern):
                try:
                    os.remove(log_file)
                except Exception as e:
                    print(f"Error while trying to delete {log_file}: {e}")

            if self.process is None:
                arguments = ['-q', 
                            '-f', ENGINE[configs['goodcheck'].get_value("engine")],
                            '-m', configs['goodcheck'].get_value("curl").lower(),
                            '-c', CHECKLISTS[configs['goodcheck'].get_value("check_list")] + ".txt",
                            '-s', (goodbyeDPI_strategies[configs['goodcheck'].get_value("strategies")] if \
                                configs['goodcheck'].get_value("engine") == 'GoodbyeDPI'\
                                else zapret_strategies[configs['goodcheck'].get_value("strategies")]) + ".txt",
                            '-p', str(configs['goodcheck'].get_value("p")),
                            ]
                print(arguments)
                self.process = start_process(*arguments, execut="goodcheckgogo.exe", path=DEBUG_PATH+GOODCHECK_PATH+"/goodcheckgogo.exe",\
                                            cwd=DEBUG_PATH+GOODCHECK_PATH)

                self.started.emit()
                QTimer.singleShot(1000, self.find_new_log_file)

            else:
                pass
        else:
            # NOT WORK
            strategy_file = Path(
                GOODCHECK_PATH,
                'StrategiesGoGo',
                'ByeDPI',
                byedpi_strategies[self.config.get_value('strategy')]+'.txt'
                )
            
            if self.thread is QThread and self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
            
            self.thread = QThread()
            self.worker = ChkPresetWorker(self._process)
            self.worker.setup(strategy_file)
            
            self.worker.reload_config()
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.start)
            self.worker.output.connect(self.handle_output_signal_added)
            self.worker.error_happens.connect(self.handle_error_happens)
            self.worker.finished.connect(self.handle_chk_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            self.thread.start()
    
    def handle_output_signal_added(self, output):
        self.output += output + '\n'
        self.output_signal.emit(output + '\n')
        
    def handle_error_happens(self, text, errorcode):
        self.handle_output_signal_added(f'[ERROR] {errorcode}:{text}')
        self.handle_output_signal_added('Exiting with an error...')
        self.sitelist = None
        self.parsed_data = None
        self.strategy_list = None
        self._process.stop_process()
        self.thread.terminate()
        self.thread.wait()
        self.thread = None
        
    def handle_chk_finished(self):
        if self.worker.exitcode != 0:
            self.handle_error_happens(
                f'Exit code is {self.worker.exitcode}.',
                'ERR_CHK_PRESET_UNKNOWN'
            )
    @Slot()
    def force_error(self):
        self.handle_error_happens(
            'Process ended with error. Check out pseudoconsole',
            'ERR_FORCE'
        )

    def find_new_log_file(self):
        log_pattern = os.path.join(GOODCHECK_PATH+"/Logs", "logfile_GoodCheckGoGo_*.log")
        log_files = glob.glob(log_pattern)
        if log_files:
            self.log_file_path = log_files[0]
            self.last_log_size = 0
            self.log_monitor_timer.start()
        else:
            QTimer.singleShot(1000, self.find_new_log_file)

    @Slot()
    def read_new_log_content(self):
        if self.log_file_path and os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'r', encoding='utf-8') as log_file:
                log_file.seek(self.last_log_size)
                new_content = log_file.read()
                self.last_log_size = log_file.tell()
                if new_content:
                    self.output += new_content
                    if "Exiting with an error..." in new_content:
                        self.log_monitor_timer.stop()
                        self.process.terminate()
                        self.process.kill()
                        self.process = None
                        self.sitelist = None
                        self.parsed_data = None
                        self.strategy_list = None
                    elif "All Done" in new_content:
                        self.handle_finished()
                        
                    pattern = r', strategy (\d/\d):'
                    blocks = re.findall(pattern, self.output, re.DOTALL | re.IGNORECASE)
                    if blocks:
                        current_strategy_check = int(blocks[-1].split("/")[0])
                        print(blocks[-1])
                        all_strategy_check = int(blocks[-1].split("/")[1])
                        self.current_strategy_check_changed.emit(
                            current_strategy_check, all_strategy_check
                            )
                    
                    self.output_signal.emit(new_content)
        else:
            self.log_monitor_timer.stop()

    @Slot()
    def stop_process(self):
        if self.thread is QThread and self.thread.isRunning():
            self._process.stop_process()
            self.thread.terminate()
            self.thread.wait()
            self.thread = None
            
        if self.process is not None:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['pid'] == self.process.pid:
                    try:
                        proc.terminate()
                        self.process = None
                    except psutil.NoSuchProcess:
                        pass
                if proc.info['name'] in ['gdpi.exe', 'winws.exe']:
                    try:
                        proc.terminate()
                    except psutil.NoSuchProcess:
                        pass
            self.process = None
            self.process_stopped_signal.emit()
            self.log_monitor_timer.stop()
            if os.path.exists(DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe"):
                os.remove(DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe")
        else:
            if os.path.exists(DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe"):
                os.remove(DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe")
            self.process_stopped_signal.emit()
        self.process_finished_signal.emit()

    @Slot()
    def handle_finished(self):
        self.parse_data()
        self.process_finished_signal.emit()
        self.process = None
        self.log_monitor_timer.stop()
        if os.path.exists(DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe"):
            os.remove(DIRECTORY+"data/goodbyeDPI/x86_64/gdpi.exe")
           
class ChkConnectionWorker(QObject):
    result_signal = Signal(object)
    error_happens = Signal(str, str)
    work_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.config = reload_chk_preset_config(None)
        self.task = None
        self.loop = None
        
    def reload_config(self):
        self.config = reload_chk_preset_config(self.config)

    def start(self):
        options = chk_preset_configure_options(self.config)
        
        tcp_hosts_file = Path(
            GOODCHECK_PATH,
            'CheckLists',
            CHECKLISTS[self.config.get_value('tcp_hosts')]+'.txt'
        )
        
        if not os.path.exists(tcp_hosts_file):
            self.error_happens.emit(
                f'File not found: {tcp_hosts_file}. Continuation is impossible.',
                'ERR_CONNECTION_WORKER_FILE_NOT_EXIST'
            )
            return
        tcp_hosts = []
        if self.config.get_value('AutomaticGoogleCacheTest'):
            ggc_hosts = [GGC_SERVER]
        else:
            ggc_hosts = []
        
        with open(tcp_hosts_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('/'): 
                    continue
                site = line.strip()
                if site and site.endswith('.googlevideo.com'):
                    ggc_hosts.append(str(site))
                elif site:
                    tcp_hosts.append(str(site))
        
        self.checker = ServerAvailabilityChecker(
            tcp_hosts,
            self.config.get_value('udp_hosts').split(';'),
            ggc_hosts,
            options=options,
        )
        self.loop = qasync.QEventLoop(self)
        asyncio.set_event_loop(self.loop)
        self.task = self.loop.create_task(self.run_checks())
        self.loop.run_until_complete(self.task)
        
    async def run_checks(self):
        print("start")
        async for result in self.checker.run_checks():
            print(result)
            self.result_signal.emit(result)
        self.work_finished.emit()
        print('end')
        return True
        
    def stop(self):
        if self.task:
            self.task.cancel()
            self.loop.stop() 
            self.task = None
            self.loop = None
        
def substitute_placeholders(text: str, substitutions: dict) -> str:
    for placeholder, value in substitutions.items():
        text = text.replace(placeholder, value)
    return text

def parse_key_line(line: str) -> list:
    if line.startswith("#KEY#"):
        line = line[len("#KEY#"):]
    line = line.strip()
    
    alternatives = []
    if line.startswith("empty;"):
        alternatives.append("")
        line = line[len("empty;"):].strip()
    elif line == "empty":
        return [""]

    tokens = line.split(";")
    for token in tokens:
        token = token.strip()
        if token == "empty":
            alternatives.append("")
        elif token: 
            if "&" in token:
                parts = [part.strip() for part in token.split("&") if part.strip()]
                merged = " ".join(parts)
                alternatives.append(merged)
            else:
                alternatives.append(token)
    return alternatives

def extract_group_lines(content: str) -> list:
    groups = []
    current_group = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#KEY#"):
            current_group.append(line)
        elif line == "#ENDGROUP#":
            if current_group:
                groups.append(current_group)
                current_group = []
    return groups

def generate_combinations(content: str, substitutions: dict) -> list:
    groups_lines = extract_group_lines(content)
    all_groups_combinations = []
    
    for group in groups_lines:
        slots = []
        for line in group:
            alternatives = parse_key_line(line)
            if not alternatives:
                alternatives = [""]
            slots.append(alternatives)
        group_combinations = []
        for combination in itertools.product(*slots):
            combo_str = " ".join(filter(None, combination)).strip()
            combo_substituted = substitute_placeholders(combo_str, substitutions)
            group_combinations.append(combo_substituted)
        all_groups_combinations.append(group_combinations)
    
    return all_groups_combinations

def is_file_goodcheck_compatible(_file):
    with open(_file, 'r', encoding='utf-8') as file:
        for line in file:
            if '#KEY#' in line or '#PROTO' in line:
                file.close()
                return True
    file.close()
    return False

def is_ip(text):
    if ":" in text:
        return True
    pattern = r'\d*\.\d*\.\d*\.\d*'
    blocks = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    if blocks:
        return True
    return False

class ChkPresetWorker(QObject):
    error_happens = Signal(str, str)
    output = Signal(str)
    finished = Signal()
    start_timer_signal = Signal()
    
    def __init__(self, process:Process):
        super().__init__()
        self.process = process
        self.qthread = None
        self.worker = None
        self.config = None
        self._output = ''
        self.reload_config()
        self.strategies_list:list[str] = []
        self.chk_result_strategy = []
        self.chk_preresult_group = []
        self.later_output = ''
        
        self.exitcode = -1
        
    def reload_config(self):
        self.config = reload_chk_preset_config(self.config)
        
    def setup(self, strategies_file):
        self.reload_config()
        self._output = ''
        self._output += f'[SETUP] Setup via {strategies_file}\n'
        if not os.path.exists(Path(strategies_file)):
            self.error_happens.emit(
                f'File {strategies_file} not exist. Continuation is impossible.', 
                'ERR_CHK_PRESET_FILE_NOT_EXIST'
                )
            self._output += f'[ERROR] File {strategies_file} not exist.\n'
            return
        
        self.strategies_list = []
        is_goodcheck_file = is_file_goodcheck_compatible(strategies_file)
        
        self._output += (
            f'[SETUP] File {strategies_file} is '
            f'{"goodcheck-like" if is_goodcheck_file else "old-like"}\n'
            )
        
        substitutions = {
            "FAKESNI": self.config.get_value('FakeSNI'),
            "FAKEHEXSTREAMTCP": self.config.get_value('FakeHexStreamTCP'),
            "FAKEHEXSTREAMUDP": self.config.get_value('FakeHexStreamUDP'),
            "FAKEHEXBYTESTCP": self.config.get_value('FakeHexBytesTCP'),
            "FAKEHEXBYTESUDP": self.config.get_value('FakeHexBytesUDP'),
            "PAYLOADTCP": self.config.get_value('PayloadTCP'),
            "PAYLOADUDP": self.config.get_value('PayloadUDP')
        }
        try:
            with open(strategies_file, 'r', encoding='utf-8') as file:
                if is_goodcheck_file:
                    all_combinations = generate_combinations(file.read(), substitutions)
                    for group_index, group in enumerate(all_combinations, start=1):
                        self._output += f"[SETUP] STARTGROUP {group_index}:\n"
                        for i, combo in enumerate(group, start=1):
                            self._output += f'[SETUP] Formed strategy {i}/{len(group)} [{combo}]\n'
                            self.strategies_list.append(combo)
                        self._output += f"[SETUP] ENDGROUP {group_index}\n"
                    file.close()
                else:    
                    for line in file:
                        strategy = line.strip()
                        if strategy:
                            self.strategies_list.append(strategy)
            
            file.close()
        except IOError:
            self.error_happens.emit(
                f'File {strategies_file} is damaged or program has no access.'
                'Continuation is impossible.', 
                'ERR_CHK_PRESET_IO'
                )
        
    def start(self, engine='byedpi'):
        self.output.emit(self._output)
        self._output = ''
        if self.process.is_process_alive():
            self.process.stop_process()
            self.process.stop_service()
            
        self.current_strategy_index = 0 
        self.start_next_strategy(engine)
    
    def start_next_strategy(self, engine):
        if self.process.is_process_alive():
            self.process.stop_process()
            _time = time.time()
            while self.process.is_process_alive():
                print('Waiting for process...')
                if time.time() - _time >= 20000:
                    self.error_happens.emit(
                        f'Cannot kill process.', 
                        'ERR_CHK_PRESET_PROCESS_TIMEOUT'
                        )
                    return
                        
        
        if self.current_strategy_index < len(self.strategies_list):
            strategy = self.strategies_list[self.current_strategy_index]
            self.output.emit(
                f'[INFO] Cheking strategy '
                f'{self.current_strategy_index}/{len(self.strategies_list)}: [{strategy}]'
                )
            print('test1')
            self.process.start_process_manually(engine, strategy)
            print('test2')
            print('test3', self.qthread.isRunning() if self.qthread is QThread else 'Non')
            self.start_chk_connection()
            
        else:
            self.output.emit("[INFO] All strategies have been processed.")
            self.exitcode = 0
            self.finished.emit()

        
    def start_chk_connection(self):
        print(11)
        self.qthread = QThread()
        print(12)
        self.worker = ChkConnectionWorker()
        print(13)
        self.worker.reload_config()
        self.worker.moveToThread(self.qthread)
        
        self.qthread.started.connect(self.worker.start)
        self.worker.error_happens.connect(self.error_happens)
        self.worker.result_signal.connect(self.handle_result)
        self.worker.work_finished.connect(self.handle_finished)
        self.worker.work_finished.connect(self.qthread.quit)
        self.worker.work_finished.connect(self.worker.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)
        print(14)
        
        self.qthread.start()
    
    def force_terminate_worker(self):
        if self.worker:
            self.worker.stop()
        self.qthread.terminate()
        self.qthread.wait()
        self.start_next_strategy('byedpi')
            
    def handle_finished(self):
        _all = len(self.chk_preresult_group)
        success = 0
        current_strategy = self.strategies_list[self.current_strategy_index]
        self.output.emit(self.later_output)
        self.later_output = ''

        for i, sitegroup in enumerate(self.chk_preresult_group):
            if sitegroup['successful']:
                success += 1
                
        existing_entry = next(
            (entry for entry in self.chk_result_strategy if entry['success'] == success),
            None
            )
            
        if existing_entry:
            existing_entry['strategies'].append(current_strategy)
        else:
            self.chk_result_strategy.append({
                'success': success,
                'all': _all,
                'strategies': [current_strategy],
            })
        
        self.chk_preresult_group = []
        
        self.current_strategy_index += 1 
        self.output.emit(f'[INFO] Strategy result is {success}/{_all}')

        self.output.emit('[INFO] Waiting for worker...')
        
        self.force_terminate_worker()          
    
    def handle_result(self, result:dict[str, str|bool]):  
        state = 'SUCCESS' if result['state'] else 'FAILURE'
        addr = ('https://'if not is_ip(result["addr"]) else '') +result["addr"]
        self.later_output += f'[TYPE: {result["type"].upper()}] {state}\t{addr}'
        
        if len(self.later_output.split('\n')) >= 5:
            self.output.emit(self.later_output)
            self.later_output = ''
        else:
            self.later_output += '\n'
        
        self.chk_preresult_group.append({
            'addr':result["addr"],
            'successful':result['state'],
            'type':result['type']
        })
        