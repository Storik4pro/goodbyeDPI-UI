import os
import shutil
import ctypes
import subprocess
import winreg

import requests
from _data import GOODBYE_DPI_PATH

def install_font(font_path):
    try:
        # Копирование шрифта в системную папку шрифтов
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(os.environ['WINDIR'], 'Fonts', font_name)
        shutil.copyfile(font_path, dest_path)

        # Регистрация шрифта в реестре
        reg_path = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, 'Nunito SemiBold (TrueType)', 0, winreg.REG_SZ, font_name)

        # Обновление кеша шрифтов
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

def download_blacklist(url, local_filename=GOODBYE_DPI_PATH+'russia-blacklist.txt'):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return True
