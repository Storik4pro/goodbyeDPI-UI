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
from _data import BYEDPI_EXECUTABLE, LOG_LEVEL, SPOOFDPI_EXECUTABLE, VERSION, ZAPRET_EXECUTABLE, settings,\
      SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, BACKUP_SETTINGS_FILE_PATH, text
from utils import check_mica, install_font, is_weak_pc, register_app, is_process_running, change_setting
from quick_start import kill_update, merge_settings, merge_blacklist, rename_update_exe, merge_settings_to_json
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
    
def check_app_is_runned():
    if not DEBUG:
        existing_app = is_process_running('goodbyeDPI.exe')
        if existing_app:
            result = messagebox.askyesno(text.inAppText['app_is_running'], 
                                         text.inAppText['process']+" 'goodbyeDPI.exe' "+text.inAppText['app_is_running_info'])
            if result:
                try:
                    existing_app.terminate()
                    existing_app.wait()
                except psutil.NoSuchProcess:
                    logger.create_debug_log(traceback.format_exc())
                except:
                    logger.create_error_log(traceback.format_exc())
            else:
                sys.exit(0)

def first_run_actions():
    first_run = settings.settings.getboolean('GLOBAL', 'is_first_run')
    if first_run:
        register_app()
        install_font('data/font/Nunito-SemiBold.ttf')

        settings.change_setting('GLOBAL', 'is_first_run', 'False')

        if is_weak_pc():
            settings.change_setting('APPEARANCE_MODE', 'animations', 'False')

def after_update_actions():
    try:
        kill_update()
        update_result = rename_update_exe()
        settings.change_setting('GLOBAL', 'update_complete', "True")
    except:
        logger.create_error_log(traceback.format_exc())
        settings.change_setting('GLOBAL', 'update_complete', "False")

def chk_directory():
    if settings.settings['GLOBAL']["work_directory"] != DIRECTORY and not "System32" in DIRECTORY:
        settings.change_setting('GLOBAL', 'work_directory', DIRECTORY)
    
if __name__ == "__main__":
    if not DEBUG: multiprocessing.freeze_support()
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
            after_update = True
            settings.change_setting('GLOBAL', 'update_complete', "False")
        pompt+=name+value
    
    logger.create_debug_log("Getting ready for start application.")

    if not is_admin():
        logger.create_debug_log("Retrying as administrator")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__+pompt, None, 1)
        logger.cleanup_logs()
    else:
        logger.create_debug_log("Started as administrator")

        check_app_is_runned()

        if settings.settings['GLOBAL']['hide_to_tray'] == "True":
            autorun = 'True'
        try:
            if not DEBUG:
                # merge settings  
                if after_update:
                    merge_settings(BACKUP_SETTINGS_FILE_PATH, SETTINGS_FILE_PATH)
                    merge_blacklist(GOODBYE_DPI_PATH)
                    merge_settings_to_json()
                    settings.reload_settings()

                    settings.change_setting('GLOBAL', 'after_update', 'False')

                # first run actions
                first_run_actions()

                # check work directory 
                chk_directory()

                # check components installed
                config = settings.settings
                config.set('GLOBAL', 'is_first_run', 'False')

                components_to_check = {
                    'spoofdpi': SPOOFDPI_EXECUTABLE,
                    'byedpi': BYEDPI_EXECUTABLE,
                    'zapret':ZAPRET_EXECUTABLE,
                }

                for component, executable in components_to_check.items():
                    component_path = os.path.join(DIRECTORY, "data", component, executable)
                    if config.getboolean('COMPONENTS', component) and not os.path.exists(component_path):
                        settings.change_setting('COMPONENTS', component, 'False')
                        logger.create_info_log(f'Component {component} will be unregistered, because {executable} not exist')

                # check after update actions
                if not settings.settings.getboolean('GLOBAL', 'update_complete'):
                    after_update_actions()

                
            settings.save_settings()
        except:
            logger.raise_critical(traceback.format_exc())
        
        # getting ready window
        mode = settings.settings['APPEARANCE_MODE']['mode']
        mica = settings.settings['APPEARANCE_MODE']['use_mica'] if check_mica() else "False"

        set_default_color_theme("blue")
        set_widget_scaling(1)
        set_appearance_mode(mode if mica != "True" else "dark")

        window = MainWindow(autorun, 'True' if after_update else first_run)

        try:
            window.iconbitmap(DIRECTORY+'data/icon.ico')

            if mica == "True": 
                ApplyMica(windll.user32.FindWindowW(c_char_p(None), window.title()), True, False)

            window.mainloop()
        except: pass

        logger.cleanup_logs()
        