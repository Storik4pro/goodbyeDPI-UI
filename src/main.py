import asyncio
import getopt
from tkinter import messagebox
import sys
import subprocess
import os
import ctypes
import psutil
import requests
from toasted import ToastDismissReason
import tkinter.ttk 
from tkinter import filedialog
from tkinter.font import Font
import ctypes.wintypes
import darkdetect
from customtkinter import *
from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, BACKUP_SETTINGS_FILE_PATH, text
from utils import install_font, register_app, is_process_running
from quick_start import merge_settings, merge_blacklist
import pywintypes
import configparser
from win10toast_click import ToastNotifier
from plyer import notification
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageTk
import threading

from window import MainWindow


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_first_run():
    first_run = settings.settings['GLOBAL']['is_first_run']
    install_font_result = True  
    if not DEBUG:
        existing_app = is_process_running('goodbyeDPI.exe')
        if existing_app:
            result = messagebox.askyesno(text.inAppText['app_is_running'], text.inAppText['process']+" 'goodbyeDPI.exe' "+text.inAppText['app_is_running_info'])
            if result:
                existing_app.terminate()
                existing_app.wait()
            else:
                sys.exit(0)
        if first_run == 'True':
            register_app()
            install_font_result = install_font('data/font/Nunito-SemiBold.ttf')
            settings.reload_settings()
    return install_font_result

    
if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        options, args = getopt.getopt(argv, "", ["autorun", "after-update"])
    except getopt.GetoptError as err:
        pass

    autorun = 'False'
    after_update = False
    first_run = settings.settings['GLOBAL']['is_first_run'] if not DEBUG else 'False'
    pompt = ' '
    for name, value in options:
        if name == '--autorun':
            autorun = 'True'
        if name == '--after-update':
            after_update = 'True'
        pompt+=name+value
        
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__+pompt, None, 1)
    else:
        if after_update == 'True':
            merge_settings(BACKUP_SETTINGS_FILE_PATH, SETTINGS_FILE_PATH)
            merge_blacklist(GOODBYE_DPI_PATH)
            settings.reload_settings()
        
        set_default_color_theme("blue")

        install_font_result = check_first_run()

        if settings.settings['GLOBAL']['hide_to_tray'] == "True":
            autorun = 'True'

        window = MainWindow(install_font_result, autorun, after_update if after_update == 'True' else first_run)

        mode = settings.settings['APPEARANCE_MODE']['mode']
        set_appearance_mode(mode)
        set_widget_scaling(1)
        try:
            window.iconbitmap(DIRECTORY+'data/icon.ico')
            window.mainloop()
        except: pass
        
        if not DEBUG:
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE_PATH)
            config['GLOBAL']['is_first_run'] = 'False'
            with open(SETTINGS_FILE_PATH, 'w') as configfile:
                config.write(configfile)