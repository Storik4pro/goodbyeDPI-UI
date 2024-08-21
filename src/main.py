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
            try:
                config_old = configparser.ConfigParser()
                config_old.read(BACKUP_SETTINGS_FILE_PATH)

                config = configparser.ConfigParser()
                config.read(SETTINGS_FILE_PATH)

                for section in config.sections():
                    if not config_old.has_section(section):
                        config_old.add_section(section)
                    for key, value in config.items(section):
                        if not config_old.has_option(section, key):
                            config_old.set(section, key, value)
                with open(SETTINGS_FILE_PATH, 'w') as configfile:
                    config_old.write(configfile)
                settings.reload_settings()
                config = config_old
            except:
                config = configparser.ConfigParser()
                config.read(SETTINGS_FILE_PATH)

            install_font_result = install_font('data/font/Nunito-SemiBold.ttf')
            
            config['GLOBAL']['is_first_run'] = 'False'
            with open(SETTINGS_FILE_PATH, 'w') as configfile:
                config.write(configfile)
            settings.reload_settings()
    return install_font_result

    
if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        options, args = getopt.getopt(argv, "", ["autorun"])
    except getopt.GetoptError as err:
        pass

    autorun = 'False'

    for name, value in options:
        if name == '--autorun':
            autorun = 'True'

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        set_default_color_theme("blue")

        install_font_result = check_first_run()
        window = MainWindow(install_font_result, autorun)
        
        mode = settings.settings['APPEARANCE_MODE']['mode']
        set_appearance_mode(mode)
        set_widget_scaling(1)
        try:
            window.iconbitmap(DIRECTORY+'data/icon.ico')
            window.mainloop()
        except: pass