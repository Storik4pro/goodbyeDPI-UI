import glob
import os
from pathlib import Path
import re
import subprocess
import sys
import win32api
import time
import winreg
from PySide6.QtCore import QObject, Slot, QTimer
from PySide6.QtCore import QProcess, Signal, QThread
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from utils import GoodbyedpiProcess, change_setting, check_proxifyre_install, get_locale, get_preset_parameters, error_sound, save_proxy_settings, start_process, stop_servise, get_parameter_mappings
from _data import DEBUG_PATH, DIRECTORY, EXECUTABLES, configs, settings, text, CONFIG_PATH, PARAMETER_MAPPING, VALUE_PARAMETERS, S_PARAMETER_MAPPING, S_VALUE_PARAMETERS

supported_proxy_engines = ['byedpi', 'spoofdpi']
proxy_mode_redflags = ['', 'manual']

def set_prefered_addr(engine, current_string, addr, port):
    result = []
    skip_next = False
    for token in current_string:
        if skip_next:
            skip_next = False
            continue
        if token in ('--ip', '-i', '--port', '-p', '-addr'):
            skip_next = True
            continue
        result.append(token)
    
    ip_n = "--ip" if engine == 'byedpi' else "-addr"
    
    result.extend([ip_n, addr, "--port", port])
    
    return result

def build_command_from_config(engine_name, parameter_mapping, value_parameters):
    command = []
    configs[engine_name].reload_config()
    params = configs[engine_name].data
    if parameter_mapping:
        for ini_param, cmd_param in parameter_mapping.items():
            if ini_param in params:
                value = configs[engine_name].get_value(ini_param)
                if value:
                    value_key = f"{ini_param}_value"
                    if ini_param in value_parameters and value_key in params:
                        param_value = params[value_key]
                        if isinstance(param_value, str):
                            param_value = param_value.strip()
                        if param_value:
                            command.append(cmd_param)
                            command.append(param_value)
                    else:
                        command.append(cmd_param)
    if value_parameters:
        for ini_param, cmd_param in value_parameters.items():
            if ini_param in params:
                value = configs[engine_name].get_value(ini_param)
                value_key = f"{ini_param}_value"
                if value and value_key in params:
                    param_value = params[value_key]
                    if isinstance(param_value, str):
                        param_value = param_value.strip()
                    if param_value or param_value == 0:
                        command.append(cmd_param)
                        command.append(str(param_value))

    if engine_name == 'goodbyedpi':
        if 'blacklist_value' in params:
            blacklist_value = params['blacklist_value']
            if isinstance(blacklist_value, str):
                blacklist_value = blacklist_value.strip()
            if blacklist_value:
                blacklist_files = blacklist_value.split(",")
                for filePath in blacklist_files:
                    command.append('--blacklist')
                    command.append(str(filePath).strip('"'))

    if 'custom_parameters' in params:
        custom_params = params['custom_parameters']
        if custom_params:
            custom_params_list = [param.strip() for param in custom_params.split(' ') if param.strip()]
            command.extend(custom_params_list)

    return command

def check_args(preset, engine=None):
    engine = engine.lower() if engine else settings.settings['GLOBAL']['engine'].lower()
    cfg = settings.settings['CONFIG'].get(f'{engine}_config_path', '')
    if cfg != "" and os.path.exists(cfg) and configs[engine].configfile != cfg:
        configs[engine].configfile = cfg
    elif cfg == "" or not os.path.exists(cfg):
        configs[engine].configfile = CONFIG_PATH + f"/{engine}/user.json"
    configs[engine].reload_config()

    
    if engine == 'goodbyedpi':
        advanced_mode_setting = settings.settings.getboolean('GLOBAL', 'use_advanced_mode')
        if advanced_mode_setting and preset != -1:
            advanced_mode_setting = False
    else:
        advanced_mode_setting = settings.settings.getboolean(engine.upper(), 'use_advanced_mode')
        
    if advanced_mode_setting or engine == 'spoofdpi':
        parameter_mapping, value_parameters = get_parameter_mappings(engine)
        command = build_command_from_config(engine, parameter_mapping, value_parameters)

    else:
        preset = int(settings.settings[engine.upper()].get('preset', -1)) if preset == -1 else preset
        command = get_preset_parameters(preset, engine)

        if engine == 'goodbyedpi':
            if settings.settings['GLOBAL'].get('change_dns') == 'True':
                dns_prompt = [
                    VALUE_PARAMETERS['dns'], settings.settings['GOODBYEDPI']['dns_value'],
                    VALUE_PARAMETERS['dns_port'], settings.settings['GOODBYEDPI']['dns_port_value'],
                    VALUE_PARAMETERS['dnsv6'], settings.settings['GOODBYEDPI']['dnsv6_value'],
                    VALUE_PARAMETERS['dnsv6_port'], settings.settings['GOODBYEDPI']['dnsv6_port_value']
                ]
                command.extend(dns_prompt)
            if settings.settings['GOODBYEDPI'].get('use_blacklist') == 'True':
                command.extend(['--blacklist', '..//russia-blacklist.txt'])
            if settings.settings['GOODBYEDPI'].get('use_blacklist_custom') == 'True':
                command.extend(['--blacklist', '..//custom_blacklist.txt'])
        
    if engine in supported_proxy_engines:
        addr = settings.settings['PROXY']['proxy_addr']
        port = settings.settings['PROXY']['proxy_port']
        command = set_prefered_addr(engine, command, addr, port)
        
    return command
    
def get_preset_name(engine, presetId):
    _additional = None
    additional = ""
    if engine == 'goodbyeDPI':
        if presetId == 9:
            _additional = "default"
        elif presetId == 10:
            _additional = "recommended"
        elif presetId == 11:
            _additional = "alt"
        
        if _additional:
            additional = f" ({get_locale(_additional)})" 
            
        return f"{presetId}. "+ get_locale(f"preset_{presetId}") + additional
    elif engine == 'zapret':
        if presetId == 3:
            _additional = "recommended"
        elif presetId == 4:
            _additional = "alt"
        
        if _additional:
            additional = f" ({get_locale(_additional)})" 
        
        return f"{presetId}. "+ get_locale(f"qpreset_{presetId}") + additional
    
    elif engine == 'byedpi':
        return f"{presetId}. "+ "("+get_locale(f"default") + ")"
    
def get_engine_preset(engine:str):
    if engine == 'goodbyeDPI':
        advanced_mode_setting = settings.settings.getboolean('GLOBAL', 'use_advanced_mode')
    else:
        advanced_mode_setting = settings.settings.getboolean(engine.upper(), 'use_advanced_mode')
    
    cfg = settings.settings.get('CONFIG', f'{engine.lower()}_config_path')
    if cfg != "" and os.path.exists(cfg) and advanced_mode_setting:
        return f"User config - \"{cfg.split('/')[-1]}\""

    else:
        if advanced_mode_setting or engine == 'spoofdpi':
            return "Custom - \"user.json\""
        elif not advanced_mode_setting:
            return get_preset_name(engine, settings.settings.getint(f'{engine.upper()}', "preset"))
    print(engine)
    return "UNKNOWN"


class ProxyProcess(QObject):
    output_added = Signal(str)
    handle_process_started = Signal()
    handle_process_stopped = Signal(str)
    handle_error = Signal(str)
    reg_error = Signal(str, str)
    
    def __init__(self):
        self.proxy_mode = settings.settings['PROXY']['proxy_now_used']
        super().__init__()
        self.output = ""
        self.is_running = False
        self.process = None
        self.log_file_path = None
        
        self.log_monitor_timer = QTimer()
        self.log_monitor_timer.setInterval(100) 
        self.log_monitor_timer.timeout.connect(self.read_new_log_content)
        self.log_file_search_start_time = None
        
    def del_log_file(self):
        log_pattern = os.path.join(DEBUG_PATH+DIRECTORY, "data", "proxifyre", "logs", "logfile_*.txt")
        for log_file in glob.glob(log_pattern):
            try:
                os.remove(log_file)
            except Exception as e:
                print(f"Error while trying to delete {log_file}: {e}")
        
    def find_new_log_file(self):
        if self.log_file_search_start_time is None:
            self.log_file_search_start_time = time.time() 

        log_pattern = os.path.join(DEBUG_PATH+DIRECTORY, "data", "proxifyre", "logs", "logfile_*.txt")
        log_files = glob.glob(log_pattern)
        if log_files:
            self.log_file_path = log_files[0]
            self.last_log_size = 0
            self.log_monitor_timer.start()
            self.log_file_search_start_time = None  
        else:
            elapsed_time = time.time() - self.log_file_search_start_time
            if elapsed_time > 60:  
                self.process.terminate()
                self.process.kill()
                self.process = None
                self.handle_process_stopped.emit("timeout")
                self.handle_error.emit("Log file search timeout")
                self.is_running = False
                self.log_file_search_start_time = None 
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
                    if "System.IO." in new_content:
                        self.log_monitor_timer.stop()
                        self.process.terminate()
                        self.process.kill()
                        self.process = None
                        self.handle_process_stopped.emit("by error")
                        self.handle_error.emit(new_content)
                        self.is_running = False
                    self.output_added.emit(new_content)
                    self.output += new_content
        else:
            self.log_monitor_timer.stop()
        
    def update_proxy_mode(self):
        if not self.is_running:
            self.proxy_mode = settings.settings['PROXY']['proxy_now_used']
    
    def check_engine(self, engine):
        if (engine not in supported_proxy_engines or 
            self.proxy_mode in proxy_mode_redflags):
            return 'NOT_SUPPORTED'
        return 'OK'
    
    def setup_system_proxy(self, mode:int):
        return save_proxy_settings(mode, signal=self.reg_error)
    
    def start_proxy(self, engine):
        self.proxy_mode = settings.settings['PROXY']['proxy_now_used']
        proxifyre_path = Path(DEBUG_PATH+DIRECTORY, "data", "proxifyre")
        self.output = ""
        
        if self.check_engine(engine) == 'NOT_SUPPORTED':
            self.handle_error.emit('NOT_SUPPORTED')
            return False
        if self.proxy_mode == 'proxifyre':
            if not check_proxifyre_install():
                self.handle_error.emit('ERR_PROXIFYRE_NOT_INSTALLED')
            
            self.del_log_file()
            
            new_env = os.environ.copy()

            execution_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

            for key, value in new_env.items():
                if execution_dir in value:
                    new_env[key] = value.replace(execution_dir, '')

            new_dir = os.path.join("C:", "TEMP", "proxifyre")  

            win32api.SetDllDirectory(new_dir)

            self.process = subprocess.Popen(
                [Path(proxifyre_path,"proxifyre.exe")],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=new_env,
                cwd=proxifyre_path,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            QTimer.singleShot(1000, self.find_new_log_file)
            result = True

        elif self.proxy_mode == 'basic':
            result = self.setup_system_proxy(1)

        self.is_running = True
        return result
        
            
    def stop_proxy(self, engine):
        if not self.is_running or self.check_engine(engine) == 'NOT_SUPPORTED':
            return
        
        if self.proxy_mode == 'proxifyre':
            self.log_monitor_timer.stop()
            self.process.terminate()
            self.process.kill()
            
            self.process = None
        elif self.proxy_mode == 'basic':
            self.setup_system_proxy(0)
            
        self.is_running = False
        
    def is_process_alive(self):
        return self.is_running
    
    def handle_output(self, data):
        self.output += data
        
class Process(QObject):
    output_added = Signal(str)
    proxifyre_output_added = Signal(str)
    error_happens = Signal(str)
    process_started = Signal(bool)
    process_stopped = Signal(str)
    engine_changed = Signal(str)
    preset_changed = Signal()
    clean_output = Signal()
    process_need_setup = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self.output = ""
        self.engine = settings.settings['GLOBAL']['engine']
        self.is_running = False
        self.process = GoodbyedpiProcess()
        self.process.output_signal.connect(self.output_added)
        self.process.output_signal.connect(self.handle_output)
        self.process.process_started.connect(self.handle_process_started)
        self.process.process_stopped.connect(self.handle_process_stopped)
        self.process.error_occurred.connect(self.handle_error)
        
        self.proxy_process = ProxyProcess()
        self.proxy_process.output_added.connect(self.proxifyre_output_added)
        self.proxy_process.handle_error.connect(self.handle_proxifyre_error)
        self.proxy_process.handle_process_stopped.connect(self.handle_proxifyre_stopped)
        self.proxy_process.reg_error.connect(self.reg_error)
    
    @Slot(result=bool)
    def is_proxifyre_used(self):
        _r = (settings.settings['PROXY']['proxy_now_used'] == 'proxifyre' and 
              self.engine in supported_proxy_engines)
        return _r
    
    @Slot(result=bool)
    def is_proxy_running(self):
        return self.engine in supported_proxy_engines
    
    @Slot(result=str)
    def get_proxifyre_output(self):
        return self.proxy_process.output
    
    @Slot()
    def update_preset(self):
        self.preset_changed.emit()

    @Slot(result=str)
    def get_preset(self):
        return get_engine_preset(self.engine)
    
    @Slot(str, result=str)
    def get_config_name(self, component):
        return configs[component].configfile

    @Slot(result=str)
    def get_executable(self):
        return EXECUTABLES[self.engine]
    
    @Slot(str)
    def change_engine(self, engine):
        change_setting("GLOBAL", "engine", engine)
        if not self.is_running:
            self.engine = engine
            self.engine_changed.emit(self.engine)
            self.preset_changed.emit()

    @Slot(result=bool)
    def is_process_alive(self):
        return self.is_running
    
    @Slot(str, str)
    def start_process_manually(self, engine, _args):
        return self.start_process(engine, _args.split(" ") if _args else None)

    @Slot(result=bool)
    def start_process(self, engine=None, _args=None):
        print(engine)
        self.engine = settings.settings['GLOBAL']['engine'] if engine is None else engine
        self.engine_changed.emit(self.engine)
        self.preset_changed.emit()
        self.clean_output.emit()
        
        if engine and not settings.settings['COMPONENTS'].getboolean(engine):
            self.handle_error('Component not installed correctly.')
            return False

        self.output = ""
        is_can_start = True
        
        if (
            (self.engine in supported_proxy_engines) and 
            settings.settings['PROXY']['proxy_now_used'] == ''
            ):
            
            self.process_need_setup.emit()
            self.process_stopped.emit("by user")
            return False
        elif self.engine in supported_proxy_engines:
            if settings.settings['PROXY']['proxy_now_used'] == 'manual':
                is_can_start = True
            else: 
                is_can_start = self.proxy_process.start_proxy(self.engine)
            
        if not is_can_start:
            return False
        
        try:
            new_args = [engine] if engine else [None]
            args = check_args(-1, engine) if _args is None else _args
            new_args.extend(args)
        except Exception as ex:
            error_sound()
            self.handle_error(f"Internal error. Unable to start process. \nError information: \n{ex}")
            if self.engine in supported_proxy_engines:
                self.proxy_process.stop_proxy(self.engine)
            return False
        
        self.is_running = True
        
        if self.engine in supported_proxy_engines:
            self.output += f"[PROXY] Proxy {self.engine} started.\n"
            self.output_added.emit(f"[PROXY] Proxy {self.engine} started.\n")
            self.process_started.emit(True)
            
        return self.process.start_goodbyedpi(*new_args)

    @Slot(result=bool)
    def stop_process(self):
        result = self.process.stop_goodbyedpi()
        return result
    
    @Slot()
    def stop_service(self):
        self.is_running = False
        self.process.stop_goodbyedpi()
        stop_servise()
    
    @Slot(result=str)
    def get_output(self):
        return self.output

    def handle_output(self, data):
        self.output += data

    def handle_process_started(self):
        self.engine_changed.emit(self.engine)
        self.preset_changed.emit()
        self.process_started.emit(True)

        self.is_running = True
        print("Process started.")

    def handle_process_stopped(self, reason):
        print(reason)
        self.proxy_process.stop_proxy(self.process.engine)
        self.is_running = False
        self.process_stopped.emit(reason)
        
        if self.engine in supported_proxy_engines:
            self.output += f"[PROXY] Proxy {self.engine} stopped.\n"
            self.output_added.emit(f"[PROXY] Proxy {self.engine} stopped.\n")
            
        print("Process stopped.")

    def handle_error(self, error_message):
        self.is_running = False
        self.proxy_process.stop_proxy(self.process.engine)
        self.output += ("\n\n[ERROR] " + error_message + "\n\n")
        self.error_happens.emit(error_message)
        
    def handle_proxifyre_stopped(self, reason):
        self.is_running = False
        self.process.stop_goodbyedpi()
        self.process_stopped.emit(reason)
        
    def handle_proxifyre_error(self, error_message):
        self.is_running = False
        self.output += ("\n\n[PROXIFYRE_ERROR] " + error_message + "\n\n")
        self.error_happens.emit(error_message)
        
    def reg_error(self, error_message, error_code):
        self.is_running = False
        self.output += ("\n\n[REG_ERROR] " + error_message + f" ({error_code})" + "\n\n")
        self.error_happens.emit(error_message)
        