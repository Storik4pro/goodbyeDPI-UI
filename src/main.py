import asyncio
import getopt
import multiprocessing
from tkinter import messagebox
import sys
import subprocess
import os
import ctypes
from ctypes import windll, c_char_p
import traceback
import psutil
import requests
from toasted import ToastDismissReason
import tkinter.ttk 
from tkinter import filedialog
from tkinter.font import Font
import ctypes.wintypes
import darkdetect
from customtkinter import *
from _data import LOG_LEVEL, VERSION, settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, BACKUP_SETTINGS_FILE_PATH, text
from utils import check_mica, install_font, register_app, is_process_running, change_setting
from quick_start import kill_update, merge_settings, merge_blacklist, rename_update_exe
from logger import AppLogger
import pywintypes
import configparser
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageTk
import threading
try: from win32material import *
except:pass

from window import MainWindow

logger = AppLogger(VERSION, "goodbyeDPI", LOG_LEVEL)
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
                try:
                    existing_app.terminate()
                    existing_app.wait()
                except:
                    logger.create_error_log(traceback.format_exc())
            else:
                sys.exit(0)
        if first_run == 'True':
            register_app()
            install_font_result = install_font('data/font/Nunito-SemiBold.ttf')
            settings.reload_settings()
    return install_font_result

def chk_directory():
    if settings.settings['GLOBAL']["work_directory"] != DIRECTORY and not "System32" in DIRECTORY:
        change_setting('GLOBAL', 'work_directory', DIRECTORY)
    
if __name__ == "__main__":
    if not DEBUG: multiprocessing.freeze_support()
    argv = sys.argv[1:]
    try:
        options, args = getopt.getopt(argv, "", ["autorun", "after-update"])
    except getopt.GetoptError as err:
        pass

    autorun = 'False'
    after_update = 'False'
    first_run = settings.settings['GLOBAL']['is_first_run'] if not DEBUG else 'False'
    pompt = ' '
    for name, value in options:
        if name == '--autorun':
            autorun = 'True'
        if name == '--after-update':
            after_update = 'True'
            change_setting('GLOBAL', 'update_complete', "False")
        pompt+=name+value
    
    logger.create_debug_log("Getting ready for start application.")

    if not is_admin():
        logger.create_debug_log("Retrying as administrator")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__+pompt, None, 1)
        logger.cleanup_logs()
    else:
        logger.create_debug_log("Started as administrator")
        if after_update == 'True':
            merge_settings(BACKUP_SETTINGS_FILE_PATH, SETTINGS_FILE_PATH)
            merge_blacklist(GOODBYE_DPI_PATH)
            settings.reload_settings()
            change_setting('GLOBAL', 'after_update', 'False')

        if (after_update == 'True' or first_run == 'True' or settings.settings['GLOBAL']['update_complete'] == 'False') and not DEBUG:
            try:
                kill_update()
                update_result = rename_update_exe()
                change_setting('GLOBAL', 'update_complete', "True")
            except:
                logger.create_error_log(traceback.format_exc())
                change_setting('GLOBAL', 'update_complete', "False")
        if first_run == 'True':
            change_setting('GLOBAL', 'work_directory', DIRECTORY)
        
        set_default_color_theme("blue")

        install_font_result = check_first_run()

        if settings.settings['GLOBAL']['hide_to_tray'] == "True":
            autorun = 'True'

        window = MainWindow(install_font_result, autorun, after_update if after_update == 'True' else first_run)

        if not DEBUG:
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE_PATH)
            config['GLOBAL']['is_first_run'] = 'False'
            with open(SETTINGS_FILE_PATH, 'w') as configfile:
                config.write(configfile)

        mode = settings.settings['APPEARANCE_MODE']['mode']
        mica = settings.settings['APPEARANCE_MODE']['use_mica'] if check_mica() else "False"
        
        set_appearance_mode(mode if mica != "True" else "dark")
        set_widget_scaling(1)
        try:
            window.iconbitmap(DIRECTORY+'data/icon.ico')
            if mica == "True": ApplyMica(windll.user32.FindWindowW(c_char_p(None), window.title()), True, False)
            window.mainloop()
        except: pass
        logger.cleanup_logs()
        