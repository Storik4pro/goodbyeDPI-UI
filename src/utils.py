import asyncio
import os
import shutil
import ctypes
import subprocess
import threading
import time
import winreg
import psutil
from toasted import Button, Image, Progress, Text, Toast, ToastButtonStyle, ToastImagePlacement

import requests
from _data import GOODBYE_DPI_PATH, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER

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

async def show_error(app_id : str, title, description, btnText):
    toast = Toast(
        app_id = app_id
    )
    toast.elements = [
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
    result = await toast.show()
    return result

def register_app():
    if Toast.is_registered_app_id("GoodbyeDPI_app"):
        Toast.unregister_app_id("GoodbyeDPI_app")
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
    
def start_process(*args):
    goodbyedpi_path = os.path.join(GOODBYE_DPI_PATH, 'x86_64', 'goodbyedpi.exe')
    
    _args = [
            goodbyedpi_path,
            *args,
    ]
    process = subprocess.Popen(_args, cwd=os.path.join(GOODBYE_DPI_PATH, 'x86_64'), creationflags=subprocess.CREATE_NO_WINDOW)
    return process

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

def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        
        if proc.info['name'] == process_name:
            if proc.info['pid'] != os.getpid():
                return proc
    return None
