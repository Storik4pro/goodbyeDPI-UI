import asyncio
import configparser
import os
import platform
import queue
import re
import shutil
import ctypes
import subprocess
import threading
import time
import webbrowser
import winreg
import psutil
import winpty
from toasted import Button, Image, Progress, Text, Toast, ToastButtonStyle, ToastImagePlacement
import winsound

import requests
try: from _data import GOODBYE_DPI_PATH, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, SETTINGS_FILE_PATH, text, settings
except: from src._data import GOODBYE_DPI_PATH, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, SETTINGS_FILE_PATH, text, settings
def error_sound():
    winsound.MessageBeep(winsound.MB_ICONHAND)


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
        Image(f"file:///{(DIRECTORY if not DEBUG else 'E:/ByeDPI')+'/data/warning.png'}?foreground=#FFFFFF&background=#F7630C&padding=40",
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
    
# goodbyedpi.exe

def remove_ansi_sequences(text):
    stage1 = re.sub(r'\w:\\[^ ]+', '', text)
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE

    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])|\]0;')
    stage2 = ansi_escape.sub('', stage1)
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    stage2 = stage2.replace("https://github.com/ValdikSS/GoodbyeDPI", "https://github.com/ValdikSS/GoodbyeDPI\n\n")
    return stage2

class GoodbyedpiProcess:
    def __init__(self, app, output_app = None) -> None:
        self.path = os.path.join(GOODBYE_DPI_PATH, 'x86_64', 'goodbyedpi.exe')
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
        command = [str(self.path)]
        command.extend(*args)
        print(command)

        self.pty_process = winpty.PtyProcess.spawn(command, cwd=os.path.join(GOODBYE_DPI_PATH, 'x86_64'))


        self.output = []

        while not self.stop_event.is_set():
            if self.pty_process.isalive():
                try:
                    data = self.pty_process.read(10000) 
                    print("data2")
                    if not data:
                        pass
                    data = remove_ansi_sequences(data)
                    self.queue.put(data)
                    self.output.append(data)
                except OSError as e:
                    print(e)
                    break
            else: break

        self.cleanup()

        return

    def cleanup(self):
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except:pass
        self.pty_process = None
        
        term = f'\n[DEBUG] The goodbyedpi.exe process has been terminated {self.reason}\n'
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

    def start_goodbyedpi(self, *args):
        if not self.goodbyedpi_thread or not self.goodbyedpi_thread.is_alive():
            self.stop_event.clear()
            self.goodbyedpi_thread = threading.Thread(target=lambda: self.start_goodbyedpi_thread(*args))
            self.goodbyedpi_thread.start()

            if self.output_app and self.output_app.winfo_exists():
                self.output_app.clear_output()

            self.check_queue()
            
            return True
        else:
            return False
        
    def stop_goodbyedpi(self):
        self.reason = 'by user'
        print('stopping ...')
        self.stop_event.set()
        if self.pty_process:
            self.pty_process.close(True)

    def check_queue(self):
        while not self.queue.empty():
            data = self.queue.get()
            if self.output_app and self.output_app.winfo_exists():
                self.output_app.add_output(data)
            if "Filter activated" in data:
                self.app.show_notification(text.inAppText['process']+" goodbyedpi.exe " + text.inAppText['run_comlete'])
            elif "Error opening filter" in data or "unknown option" in data:
                self.reason = 'for unknown reason'
                self.error = True
                print("Trying to connect terminal")
                error_sound()
                self.app.connect_terminal(error=True)
                self.app.show_notification(f"Unable to connect goodbyedpi.exe. See pseudo console for more information", title=text.inAppText['error'], button='open pseudo console', func=self.app.connect_terminal, _type='error')
        if self.goodbyedpi_thread.is_alive():
            self.app.after(100, self.check_queue)

    def connect_app(self, output_app):
        self.output_app = output_app
        self.output_app.add_output(self.output)

    def disconnect_app(self):
        if self.output_app:
            try:self.output_app.destroy()
            except:pass
            self.output_app = None
    
def start_process(*args):
    goodbyedpi_path = os.path.join(GOODBYE_DPI_PATH, 'x86_64', 'goodbyedpi.exe')
    
    _args = [
            goodbyedpi_path,
            *args,
    ]
    process = subprocess.Popen(_args, cwd=os.path.join(GOODBYE_DPI_PATH, 'x86_64'), creationflags=subprocess.CREATE_NO_WINDOW)
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

def get_latest_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    response = requests.get(url)
    data = response.json()
    latest_version = data["tag_name"]

    return latest_version

def get_release_info(version):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{version}"
    response = requests.get(url)
    data = response.json()
    return data

def get_download_url(version):
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
    
def download_update(url, directory, signal):
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
                    signal.emit(float((dl / total_length)*100))
                    dl += len(data)
                    f.write(data)

def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        
        if proc.info['name'] == process_name:
            if proc.info['pid'] != os.getpid():
                return proc
    return None

# settings change


def change_setting(setting_group, setting, value):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_PATH)
    config[setting_group][setting] = value

    with open(SETTINGS_FILE_PATH, 'w') as configfile:
        config.write(configfile)
    
    settings.reload_settings()

def change_settings(setting_group, settings_list):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_PATH)
    for i, setting in enumerate(settings_list):
        config[setting_group][setting[0]] = setting[1]

    with open(SETTINGS_FILE_PATH, 'w') as configfile:
        config.write(configfile)
    
    settings.reload_settings()

def open_custom_blacklist():
    os.startfile(f"{GOODBYE_DPI_PATH}/custom_blacklist.txt")

def check_mica():
    version = platform.version()
    major, minor, build = map(int, version.split('.'))
    return build >= 22000