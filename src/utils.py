import hashlib
import json
import platform
import sys
import zipfile

def check_winpty():
    version = platform.version()
    major, minor, build = map(int, version.split('.'))
    return build >= 17763
winpty_support = check_winpty()

import asyncio
import configparser
from datetime import datetime
import os
import queue
import re
import shutil
import ctypes
import subprocess
import tempfile
import threading
import time
import webbrowser
import winreg
import psutil
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
if winpty_support: import winpty
from toasted import Button, Image, Progress, Text, Toast, ToastButtonStyle, ToastImagePlacement
import winsound

import requests
from _data import GOODBYE_DPI_EXECUTABLE, ZAPRET_EXECUTABLE, ZAPRET_PATH, \
    GOODBYE_DPI_PATH, DEBUG, DIRECTORY, DEBUG_PATH, REPO_NAME, REPO_OWNER, CONFIGS_REPO_NAME, SETTINGS_FILE_PATH,\
    CONFIG_PATH, SPOOFDPI_EXECUTABLE, BYEDPI_EXECUTABLE, EXECUTABLES, COMPONENTS_URLS, text, settings

def error_sound():
    winsound.MessageBeep(winsound.MB_ICONHAND)

# PC test
def is_weak_pc():
    cpu_freq = psutil.cpu_freq().max
    cpu_cores = psutil.cpu_count(logical=False)
    total_memory_gb = psutil.virtual_memory().total / (1024 ** 3)

    LOW_CPU_FREQ = 2000 
    LOW_CPU_CORES = 2
    LOW_MEMORY_GB = 4 

    weak_cpu = cpu_freq < LOW_CPU_FREQ or cpu_cores <= LOW_CPU_CORES
    weak_memory = total_memory_gb <= LOW_MEMORY_GB

    if weak_cpu or weak_memory:
        return True
    else:
        return False
    
def get_locale(element):
    try:
        return text.inAppText[element]
    except:
        return f"locale:{element}"

# Toast

class ProgressToast():
    def __init__(self, app_id : str, title, description, filename='sample_file.txt') -> None:
        self.toast = Toast(
            app_id = app_id,
            arguments = "click",
        )
        self.toast.elements = [
            Text(title),
            Text(description),
            Progress(
                value = "-1",
                status = "{status}",
                title = filename,
                display_value = "0% @ 0 MB/s"
            ),
        ]
        self.notification_thread = None
        print(self.toast.elements[2].value)
        self.start_toast(-1, 'downloading')

    async def update_toast_tread(self, value, status):
        self.result = await self.toast.show({
            "status": status,
            "value":value
        })
        return self.result
    
    def start_toast(self, value, status):
        if self.notification_thread is None or not self.notification_thread.is_alive():
            self.notification_thread = threading.Thread(target=lambda: asyncio.run(self.update_toast_tread(value, status)))
            self.notification_thread.start() 

    def update_toast(self, value, status, body=None, title=None):
        print(value)
        self.toast.elements[2].value = value
        self.toast.elements[2].status = status
        if body: self.toast.elements[1].content = body
        if title: self.toast.elements[0].content = title

async def show_message(app_id : str, title, description):
    toast = Toast(
        app_id = app_id
    )
    toast.elements = [
        Text(title),
        Text(description),
    ]
    result = await toast.show()
    return result

async def show_error(app_id : str, title, description, btnText, btnText2):
    toast = Toast(
        app_id = app_id
    )
    elements = [
        Image(f"file:///{(DIRECTORY if not DEBUG else DEBUG_PATH)+'/data/warning.png'}?foreground=#FFFFFF&background=#F7630C&padding=40",
            placement = ToastImagePlacement.LOGO
        ),
        Text(title),
        Text(description),
        Button(
            btnText, 
            arguments = "accept",
            style = ToastButtonStyle.CRITICAL
        ),
    ]
    if btnText2:
        elements.append(
            Button(
                btnText2,
                arguments = "call2",
            )
        )
    toast.elements = elements

    result = await toast.show()
    return result

def register_app():
    if not Toast.is_registered_app_id("GoodbyeDPI_app"):
        Toast.register_app_id("GoodbyeDPI_app", "GoodbyeDPI UI", icon_uri = DIRECTORY+"data\icon.png")

# utils

def install_font(font_path):
    try:
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(os.environ['WINDIR'], 'Fonts', font_name)
        shutil.copyfile(font_path, dest_path)

        
        reg_path = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, 'Nunito SemiBold (TrueType)', 0, winreg.REG_SZ, font_name)

        
        ctypes.windll.gdi32.AddFontResourceW(dest_path)
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)

        return True
    except Exception as e:
        return False
    
# engine load'n'read

spoofdpi_logo = \
"""███████ ██████   ██████   ██████  ███████ ██████  ██████  ██
██      ██   ██ ██    ██ ██    ██ ██      ██   ██ ██   ██ ██
███████ ██████  ██    ██ ██    ██ █████   ██   ██ ██████  ██
     ██ ██      ██    ██ ██    ██ ██      ██   ██ ██      ██
███████ ██       ██████   ██████  ██      ██████  ██      ██"""
def remove_ansi_sequences(text):
    stage1 = re.sub(r'\w:\\[^ ]+', '', text)
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE

    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])|\]0;')
    stage2 = ansi_escape.sub('', stage1)
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    stage2 = stage2.replace("https://github.com/ValdikSS/GoodbyeDPI", "https://github.com/ValdikSS/GoodbyeDPI\n\n")

    if settings.settings['GLOBAL']['engine'] == "spoofdpi":
        stage2 = stage2.replace("•ADDR", "\n\n•ADDR")
        stage2 = stage2.replace("to quit", "to quit\n\n")
        stage2 = stage2.replace("Press", "\nPress")
        stage2 = re.sub(r'█.*█', '', stage2, flags=re.DOTALL)
        print(stage2)
        stage2 = spoofdpi_logo + stage2

    return stage2

"""class GoodbyedpiProcess(QObject):
    # Define signals
    output_signal = Signal(str)
    process_started = Signal()
    process_stopped = Signal()
    error_occurred = Signal(str)

    def __init__(self, app, output_app = None) -> None:
        super().__init__()

        self.path = os.path.join(GOODBYE_DPI_PATH, 'x86_64', GOODBYE_DPI_EXECUTABLE) \
            if settings.settings['GLOBAL']['engine'] == 'goodbyeDPI' \
            else os.path.join(ZAPRET_PATH, ZAPRET_EXECUTABLE)
        self.app = app
        self.output_app = output_app
        self.args = ''
        self.output = ''
        self.pty=None
        self.goodbyedpi_thread = None
        self.stop_event = threading.Event()
        self.pty_process = None
        self.queue = queue.Queue()
        self.proc = None
        self.reason = 'for unknown reason'
        self.error = False

    def start_goodbyedpi_thread(self, *args):
        engine = settings.settings['GLOBAL']['engine']
        execut = EXECUTABLES[engine]

        self.path = os.path.join(GOODBYE_DPI_PATH, 'x86_64', GOODBYE_DPI_EXECUTABLE) \
            if engine == 'goodbyeDPI' \
            else os.path.join(DIRECTORY+f'data/{engine}', execut)
        command = [str(self.path)]
        command.extend(*args)
        print(command)

        self.output = []

        if winpty_support:
            try:
                self.pty_process = winpty.PtyProcess.spawn(
                    command,
                    cwd=os.path.join(GOODBYE_DPI_PATH, 'x86_64') if settings.settings['GLOBAL']['engine'] == 'goodbyeDPI' \
                        else os.path.join(DIRECTORY+f'data/{engine}')
                )
            except Exception as ex:
                data = f"Component not installed correctly. ({ex})"
                self.queue.put(data)
                self.output.append(data)
                return

            while not self.stop_event.is_set():
                if self.pty_process.isalive():
                    try:
                        data = self.pty_process.read(10000)
                        if data:
                            data = remove_ansi_sequences(data)
                            print("data2")
                            self.queue.put(data)
                            self.output.append(data)
                    except OSError as e:
                        print(e)
                        break
                else:
                    break

            self.cleanup()

        else:
            self.proc = start_process(*command)
            self.queue.put("Filter activated")
            self.cleanup()

        return


    def cleanup(self):
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except:pass
        self.pty_process = None
        execut = EXECUTABLES[settings.settings["GLOBAL"]["engine"]]
        term = f'\n[DEBUG] The {execut} process has been terminated {self.reason}\n'
        self.output.append(term)
        self.queue.put(term)
        self.reason = 'for unknown reason'

    def check_process_status(self):
        self.reason = 'by user'
        if self.proc and self.proc.poll() is not None:
            self.stop_goodbyedpi()
            print(self.pty_process.isalive())
        elif not self.goodbyedpi_thread.is_alive():
            self.cleanup()
        else:
            if self.app: 
                self.app.after(5000, self.check_process_status)

    def start_goodbyedpi(self, notf=True, *args):
        if not self.goodbyedpi_thread or not self.goodbyedpi_thread.is_alive():
            self.stop_event.clear()
            self.goodbyedpi_thread = threading.Thread(target=lambda: self.start_goodbyedpi_thread(*args))
            self.goodbyedpi_thread.start()

            if self.output_app and self.output_app.winfo_exists():
                self.output_app.clear_output()

            self.check_queue(notf)
            
            return True
        else:
            return False
        
    def stop_goodbyedpi(self):
        self.reason = 'by user'
        print('stopping ...')
        self.stop_event.set()
        if self.pty_process:
            self.pty_process.close(True)

    def check_queue(self, notf=True):
        execut = EXECUTABLES[settings.settings["GLOBAL"]["engine"]]
        while not self.queue.empty():
            data = self.queue.get()
            if self.output_app and self.output_app.winfo_exists():
                self.output_app.add_output(data)
            if "Filter activated" in data or "capture is started." in data or 'created a listener' in data:
                if notf: self.app.show_notification(text.inAppText['process']+f" {execut} " + text.inAppText['run_comlete'])
            elif "Error opening filter" in data or "unknown option" in data or "hostlists load failed" in data or\
                "must specify port filter" in data or "ERROR:" in data or "Component not installed correctly" in data :
                self.reason = 'for unknown reason'
                self.error = True
                print("Trying to connect terminal")
                error_sound()
                self.app.connect_terminal(error=True)
                self.app.show_notification(f"Unable to connect {execut}. See pseudo console for more information", title=text.inAppText['error'], button='open pseudo console', func=self.app.connect_terminal, _type='error')
        if self.goodbyedpi_thread.is_alive():
            self.app.after(100, lambda: self.check_queue(notf=notf))

    def connect_app(self, output_app):
        self.output_app = output_app
        self.output_app.add_output(self.output)

    def disconnect_app(self):
        if self.output_app:
            try:self.output_app.destroy()
            except:pass
            self.output_app = None"""

class GoodbyedpiWorker(QThread):
    output_signal = Signal(str)
    process_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, args, engine, parent=None):
        super().__init__(parent)
        self.args = args
        self.engine = engine
        self.stop_event = threading.Event()
        self.queue = queue.Queue()
        self.output = []
        self.reason = 'for unknown reason'
        self.error = False
        self.proc = None
        self.pty_process = None

    def run(self):
        engine = self.engine
        execut = EXECUTABLES[engine]

        if engine == 'goodbyeDPI':
            self.path = os.path.join(GOODBYE_DPI_PATH, 'x86_64', GOODBYE_DPI_EXECUTABLE)
            cwd = os.path.join(GOODBYE_DPI_PATH, 'x86_64')
        else:
            self.path = os.path.join(DIRECTORY, f'data/{engine}', execut)
            cwd = os.path.join(DIRECTORY, f'data/{engine}')

        command = [str(self.path)]
        command.extend(self.args)
        print(command)

        self.output = []

        if winpty_support:
            try:
                self.pty_process = winpty.PtyProcess.spawn(
                    command,
                    cwd=cwd
                )
            except Exception as ex:
                data = f"Component not installed correctly. ({ex})"
                self.queue.put(data)
                self.output.append(data)
                self.output_signal.emit(data)
                self.error_occurred.emit(data)
                return

            while not self.stop_event.is_set():
                if self.pty_process.isalive():
                    try:
                        data = self.pty_process.read(10000)
                        if data:
                            data = remove_ansi_sequences(data)
                            print("data received")
                            self.queue.put(data)
                            self.output.append(data)
                            self.output_signal.emit(data)
                    except OSError as e:
                        print(e)
                        break
                else:
                    break

            self.cleanup()

        else:
            self.proc = start_process(*command)
            data = "Filter activated"
            self.queue.put(data)
            self.output_signal.emit(data)
            self.cleanup()

    def cleanup(self):
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except:
                pass
            self.pty_process = None
        execut = EXECUTABLES[self.engine]
        term = f'\n[DEBUG] The {execut} process has been terminated {self.reason}\n'
        self.output.append(term)
        self.queue.put(term)
        self.output_signal.emit(term)
        
        self.process_finished.emit(self.reason)

    def stop(self):
        self.reason = 'by user'
        print('Stopping process...')
        self.stop_event.set()
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except:
                pass
        if self.proc:
            try:
                self.proc.terminate()
            except:
                pass
        self.wait()

stop_flags = [
    "Error opening filter",
    "unknown option",
    "hostlists load failed",
    "must specify port filter",
    "ERROR:",
    "Component not installed correctly",
    "--debug=0|1|syslog|@<filename>"
]

class GoodbyedpiProcess(QObject):
    output_signal = Signal(str)
    process_started = Signal()
    process_stopped = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.error = False
        self.stop = False
        self.engine = settings.settings['GLOBAL']['engine']
        self.reason = 'by user'

    @Slot()
    def start_goodbyedpi(self, *args):
        self.engine = settings.settings['GLOBAL']['engine']
        if self.worker is None or not self.worker.isRunning():
            self.worker = GoodbyedpiWorker(args=args, engine=self.engine)
            self.worker.output_signal.connect(self.handle_output)
            self.worker.process_finished.connect(self.handle_process_finished)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.start()
            self.process_started.emit()
            self.error = False
            self.stop = False
            return True
        else:
            return False

    @Slot()
    def stop_goodbyedpi(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.process_stopped.emit(self.reason)
            self.error = False
            self.stop = True

    def handle_output(self, data):
        execut = EXECUTABLES[settings.settings["GLOBAL"]["engine"]]
        if not self.error and not self.stop: self.output_signal.emit(data)
        if "Filter activated" in data or "capture is started." in data or 'created a listener' in data:
            self.error = False
        elif any(error_msg in data for error_msg in stop_flags):
            self.reason = 'for unknown reason'
            self.error = True
            print("Trying to connect terminal")
            error_sound()
            self.error_occurred.emit("Unknown error occurred while process running")
            
        

    def handle_process_finished(self, reason):
        self.reason = reason
        self.process_stopped.emit(self.reason)

    def handle_error(self, error_message):
        self.error_occurred.emit(error_message)

def start_process(*args, **kwargs):
    '''
    :param *args: startup args: turple
    :param engine: Setting custom engine. Default -> `settings.settings["GLOBAL"]["engine"]`
    :param execut: Executable file. Default -> `EXECUTABLES[engine]`
    :param path: Path to execut. Default -> `DIRECTORY+f'data/{engine}/{execut}'`
    :param cwd: Process work directory. Default -> `DIRECTORY+f'data/{engine}'`
    '''
    engine = kwargs.get('engine', settings.settings["GLOBAL"]["engine"]) 
    execut = kwargs.get('execut', EXECUTABLES[engine])
    path = kwargs.get('path', os.path.join(GOODBYE_DPI_PATH, 'x86_64', GOODBYE_DPI_EXECUTABLE) \
                                           if engine == 'goodbyeDPI' \
                                           else os.path.join(DIRECTORY+f'data/{engine}', execut))
    cwd = kwargs.get('cwd', os.path.join(GOODBYE_DPI_PATH, 'x86_64') \
                                         if settings.settings['GLOBAL']['engine'] == 'goodbyeDPI'\
                                         else os.path.join(DIRECTORY+f'data/{engine}'))

    _args = [
            path,
            *args,
    ]
    process = subprocess.Popen(_args, cwd=cwd, creationflags=subprocess.CREATE_NO_WINDOW)
    return process

def stop_servise():
    try:
        subprocess.run(['sc', 'stop', 'WinDivert'], check=True)
        subprocess.run(['sc', 'delete', 'WinDivert'], check=True)
    except Exception as e:
        pass

def download_blacklist(url, progress_toast:ProgressToast, local_filename=GOODBYE_DPI_PATH+'russia-blacklist.txt'):
    temp_filename = local_filename + '.tmp'
    progress_toast.update_toast(-1, 'downloading')
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get('content-length')
            if total_length is None:
                total_length = 1  
            else:
                total_length = int(total_length)
            with open(temp_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
        if os.path.exists(local_filename):
            os.remove(local_filename)
        os.rename(temp_filename, local_filename)
        
    except Exception as ex:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        progress_toast.update_toast(0, 'error', str(ex), 'Something went wrong')
        return False
    progress_toast.update_toast(100, 'complete!')
    return True

def move_settings_file(settings_file_path, backup_settings_file_path):
    shutil.copy(settings_file_path, backup_settings_file_path)

# settings change


def change_setting(setting_group, setting, value):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_PATH, encoding='utf-8')
    config[setting_group][setting] = value

    with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    settings.reload_settings()

def change_settings(setting_group, settings_list):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_PATH, encoding='utf-8')
    for i, setting in enumerate(settings_list):
        config[setting_group][setting[0]] = setting[1]

    with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    settings.reload_settings()

def open_custom_blacklist():
    os.startfile(f"{GOODBYE_DPI_PATH}/custom_blacklist.txt")

def check_mica():
    version = platform.version()
    major, minor, build = map(int, version.split('.'))
    return build >= 22000

# update

def get_latest_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    response = requests.get(url)
    data = response.json()
    latest_version = data["tag_name"]

    return latest_version if not DEBUG else "1.1.3"

def get_release_info(version):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{version}"
    response = requests.get(url)
    data = response.json()
    return data

def get_download_url(version):
    if DEBUG: return "https://google.com"
    try:
        data = get_release_info(version)
        download_url = None

        for asset in data["assets"]:
            if asset["name"].endswith(".zip"):
                download_url = asset["browser_download_url"]
                break

        if download_url is None:
            return 'ERR_INVALID_URL'

        return download_url
    except requests.ConnectionError:
        return 'ERR_CONNECTION_LOST'
    except Exception as ex:
        return 'ERR_UNKNOWN'
    
def download_update(url, directory, signal=None):
    if not DEBUG or signal is None:
        with requests.get(url, stream=True) as r:
            total_length = r.headers.get('content-length')
            if total_length is None:
                with open(directory, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                dl = 0
                total_length = int(total_length)
                with open(directory, 'wb') as f:
                    for data in r.iter_content(chunk_size=4096):
                        if signal:signal.emit(float((dl / total_length)*100))
                        dl += len(data)
                        f.write(data)
    else:
        i=0
        while i < 100:
            i+=1
            if signal:signal.emit(i)
            time.sleep(0.05)

def get_component_download_url(component_name:str):
    component_addres = COMPONENTS_URLS[component_name]
    component_url = f"https://api.github.com/repos/{component_addres}/releases"
    try:
        response = requests.get(component_url)
        if response.status_code == 200:
            releases = response.json()
            if releases:
                latest_release = releases[0]
                version = latest_release.get("tag_name")
                if component_name == 'zapret':
                    return f"https://github.com/bol-van/zapret-win-bundle/archive/refs/heads/master.zip|{version}"
                
                if component_name == 'goodbyeDPI' and version == '0.2.3rc3':
                    return f'ERR_LATEST_VERSION_ALREADY_INSTALLED|{version}'
                pre_download_url = f"https://api.github.com/repos/{component_addres}/releases/tags/{version}"

                download_url = None

                _response = requests.get(pre_download_url)
                data = _response.json()

                for asset in data["assets"]:
                    if asset["name"].endswith(".zip"):
                        if component_name == 'byedpi': 
                            if "x86_64-w64" in asset["name"]:
                                download_url = asset["browser_download_url"]
                                break
                            continue
                        else:
                            download_url = asset["browser_download_url"]
                        break
                    elif asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break

                if download_url is None:
                    return 'ERR_INVALID_URL'

                
                return download_url+"|"+version
                
                
            else:
                return 'ERR_CANNOT_FIND_RELEASE'
        else:
            return f'ERR_SERVER_STATUS_CODE_{response.status_code}'
    except Exception as ex:
        return 'ERR_UNKNOWN'
    
def extract_zip(zip_file, zip_folder_to_unpack, extract_to, files_to_skip=[]):
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            members = zip_ref.infolist()
            total_files = len(members)
            extracted_files = 0

            index = 0  
            while index < len(members):
                member = members[index]
                member_path = member.filename
                if member_path.count("/") == 1 and member_path.split("/")[1] == '' and\
                    zip_folder_to_unpack == "/":
                    zip_folder_to_unpack = member_path

                if member_path.startswith(zip_folder_to_unpack):
                    relative_path = member_path[len(zip_folder_to_unpack):]
                    if relative_path == '':
                        index += 1
                        continue 
                    
                    if any(skip_item in relative_path for skip_item in files_to_skip):
                        index += 1
                        continue


                    destination_path = os.path.join(extract_to, relative_path)
                    destination_dir = os.path.dirname(destination_path)
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    if relative_path.endswith(".txt") and os.path.exists(destination_path):
                        index += 1
                        continue

                    if member.is_dir():
                        if not os.path.exists(destination_path):
                            os.makedirs(destination_path)
                    else:
                        try:
                            with zip_ref.open(member) as source, open(destination_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                        except OSError as pe:
                            print(pe.errno)
                            if '13' in str(pe.errno):
                                return 'ERR_PERMISSION_DENIED'
                            else:
                                return 'ERR_FILE_UNPACKING'
                        except Exception as ex:
                            return "ERR_FILE_UNPACKING"

                    extracted_files += 1
                    progress = extracted_files / total_files
                index += 1  

    except Exception as ex:
        print(ex)
        return "ERR_FILE_UNPACKING"

def download_files_from_github(remote_dir, local_dir):
    base_url = f"https://api.github.com/repos/{REPO_OWNER}/{CONFIGS_REPO_NAME}/contents/{remote_dir}?ref=main"
    headers = {'Accept': 'application/vnd.github.v3.raw'}

    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            return f"ERR_SERVER_STATUS_CODE_{response.status_code}"

        files = response.json()

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        for file_info in files:
            if file_info['type'] == 'file':
                filename = file_info['name']
                if filename in ('.', '..'):
                    continue

                local_filepath = os.path.join(local_dir, filename)
                if filename == 'user.json' and os.path.exists(local_filepath):
                    print(local_filepath)
                    continue

                download_url = file_info['download_url']
                file_response = requests.get(download_url, headers=headers)
                if file_response.status_code == 200:
                    with open(local_filepath, 'wb') as f:
                        f.write(file_response.content)
                else:
                    continue

        return 
    except Exception as ex:
        return "ERR_CONFIG_DOWNLOAD_UNKNOWN"

def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            return 'ERR_FILE_NOT_FOUND'
        return
    except FileNotFoundError:
        return 'ERR_FILE_NOT_FOUND'
    except PermissionError:
        return 'ERR_PERMISSION_DENIED'
    except Exception as e:
        return 'ERR_CLEANUP_FILES'
    
def open_folder(folder_path):
    os.startfile(folder_path)

def register_component(component_name:str, version):
    component_directory = DIRECTORY+f"data/{component_name}" if not DEBUG else f"E:/_component/{component_name}"
    result = download_files_from_github(remote_dir=f"{component_name.lower()}/", local_dir=component_directory)
    if result: return result

    config_component_path = CONFIG_PATH+f"/{component_name.lower()}" if not DEBUG else f"E:/_component/{component_name}/config"
    result = download_files_from_github(remote_dir=f"{component_name.lower()}/configs", local_dir=config_component_path)
    if result: return result

    change_settings('COMPONENTS', [
        [f'{component_name.lower()}', 'True'],
        [f'{component_name.lower()}_version', version],
        [f'{component_name.lower()}_server_version', version]
        ])

def unregister_component(component_name:str):
    if component_name == 'goodbyeDPI':
        return 'ERR_CANNOT_REMOVE_COMPONENT'
    if settings.settings['GLOBAL']['engine'] == component_name: change_setting('GLOBAL', f'engine', 'goodbyeDPI')
    change_setting('COMPONENTS', f'{component_name.lower()}', 'False')
    return 'True'

def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        
        if proc.info['name'] == process_name:
            if proc.info['pid'] != os.getpid():
                return proc
    return None


# autorun

def create_xml(author, executable, arguments):
  xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
  <Task xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
    <RegistrationInfo>
      <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
      <Author>{author}</Author>
    </RegistrationInfo>
    <Triggers>
      <LogonTrigger>
        <Enabled>true</Enabled>
      </LogonTrigger>
    </Triggers>
    <Principals>
      <Principal id="Author">
        <RunLevel>HighestAvailable</RunLevel>
      </Principal>
    </Principals>
    <Settings>
      <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
      <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
      <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
      <AllowHardTerminate>true</AllowHardTerminate>
      <StartWhenAvailable>true</StartWhenAvailable>
      <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
      <IdleSettings>
        <StopOnIdleEnd>false</StopOnIdleEnd>
        <RestartOnIdle>false</RestartOnIdle>
      </IdleSettings>
      <AllowStartOnDemand>true</AllowStartOnDemand>
      <Enabled>true</Enabled>
      <Hidden>false</Hidden>
      <RunOnlyIfIdle>false</RunOnlyIfIdle>
      <WakeToRun>false</WakeToRun>
      <ExecutionTimeLimit>P3D</ExecutionTimeLimit>
      <Priority>7</Priority>
    </Settings>
    <Actions Context="Author">
      <Exec>
        <Command>{executable}</Command>
        <Arguments>{arguments}</Arguments>
      </Exec>
    </Actions>
  </Task>
  """
  with tempfile.NamedTemporaryFile('w', encoding='utf-16', suffix='.xml', delete=False) as temp_xml:
      temp_xml.write(xml_content)
      temp_xml_path = temp_xml.name
  return temp_xml_path

def remove_xml(path):
    os.remove(path)

# goodbyeDPI

hash_gdpi_64_023rc32="afa7f66231b9cec7237e738b622c0181"
hash_gdpi_64_023testbuild="4d060be292eb50783c0d8022d4bf246c"
hash_gdpi_64_testbuild_by_Decavoid="c25b01de6d5471f3b7337122049827f6"

def calculate_hash(file_path, algorithm='md5'):
    hash_function = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_function.update(chunk)

    return hash_function.hexdigest()

def check_version(gdpi_exe_fullpath=GOODBYE_DPI_PATH+"\\x86_64\\goodbyedpi.exe"):
    hash_value = calculate_hash(gdpi_exe_fullpath)
    
    if hash_value == hash_gdpi_64_023testbuild:
        return "test version - FWSNI support"
    elif hash_value == hash_gdpi_64_testbuild_by_Decavoid:
        return "test version (Decavoid) - FWSNI support"
    elif hash_value == hash_gdpi_64_023rc32:
        return "0.2.3-rc3-2"
    
    return "UNKNOWN VERSION (FWSNI support enabled)"

def sni_support():
    if "FWSNI support" in check_version():
        return True
    else:
        return False 
    
def check_urls():
    with open(f"{(DEBUG_PATH if DEBUG else '') + GOODBYE_DPI_PATH}/custom_blacklist.txt", 'r') as file:
        urls = file.read().splitlines()

    sites = []
    print(urls)

    for url in urls:
        try:
            print(url)
            response = requests.head("https://"+url, timeout=5)
            print(response)
            if response.status_code != 404:
                sites.append("https://"+url)
        except requests.RequestException as ex:
            if "Read timed out." in str(ex):
                sites.append("https://"+url)
            print(str(ex), ex)
            continue
        except Exception as ex:
            continue
    
    return sites

# JSON
def get_preset_parameters(index:int|str, engine:str):
    filename = f"{index}.json"
    path = os.path.join((DEBUG_PATH if DEBUG else "") + CONFIG_PATH + "/" + engine.lower(), filename)
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            custom_parameters = data.get('custom_parameters')
            if custom_parameters is not None:
                return str(custom_parameters).split()
            else:
                raise KeyError(f"Unable to load {filename}. JSON file not setup right")
    except FileNotFoundError:
        raise FileNotFoundError(f"Unable to found config file {filename}. File is not exist in current location {path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Unable to found config file {filename}. File encoding is incorrect")

def replace_system_folders_with_short_names(path):
    system_folders = {
        'Program Files': 'Progra~1',
        'Program Files (x86)': 'Progra~2',
        'ProgramData': 'Progra~3',
        'Users': 'Users',
        'Documents and Settings': 'Docume~1',
        'Application Data': 'Applic~1',
        'Local Settings': 'LocalS~1',
    }

    path_parts = path.split(os.sep)

    new_path_parts = []
    for part in path_parts:
        if part in system_folders:
            new_path_parts.append(system_folders[part])
        else:
            new_path_parts.append(part)
    
    new_path = os.sep.join(new_path_parts)
    return new_path
