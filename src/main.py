import asyncio
from tkinter import messagebox
import sys
import subprocess
import os
import ctypes
import psutil
import requests
from toasted import ToastDismissReason
from win11toast import notify, update_progress, toast, clear_toast, toast_async

def run_as_admin(cmd, cwd):
    try:
        subprocess.Popen(cmd, shell=True, cwd=cwd, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as ex:
        messagebox.showerror("Error", f"Application work wrong\n{ex}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        
        if proc.info['name'] == process_name:
            if proc.info['pid'] != os.getpid():
                return proc
    return None

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
else:
    import tkinter.ttk 
    from tkinter import filedialog
    from tkinter.font import Font
    import ctypes.wintypes
    import darkdetect
    from customtkinter import *
    from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, BACKUP_SETTINGS_FILE_PATH, text
    from utils import install_font, start_process, download_blacklist, move_settings_file, ProgressToast, register_app, show_message, show_error
    import pywintypes
    import configparser
    from win10toast_click import ToastNotifier
    from plyer import notification
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageTk
    import threading

    

    first_run = settings.settings['GLOBAL']['is_first_run']
    install_font_result = False
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

    version = "1.0.4"
    
    def get_latest_release():
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
        response = requests.get(url)
        data = response.json()
        latest_version = data["tag_name"]

        return latest_version

    regions = {
        text.inAppText['ru']:'RU',
        text.inAppText['other']:'OTHER'
    }

    class MainWindow(CTk):
        def __init__(self) -> None:
            super().__init__()
            self.geometry('300x400')
            self.title(f'goodbyeDPI UI - v {version}')
            self.resizable(False, False)

            self.notification_thread = None
            self.is_update = False

            self.frame1 = CTkFrame(self, width=400) 
            self.frame2 = CTkFrame(self, width=400)

            self.region = settings.settings['REGION']['region']
            self.process = is_process_running('goodbyedpi.exe')
            self.active_dns = settings.settings['GLOBAL']['change_dns']
            self._active_dns = StringVar(value=self.active_dns)
            if self.active_dns == 'True': 
                self.active_dns = True
            else: self.active_dns = False
            
            self.autorun = settings.settings['GLOBAL']['autorun']
            if self.autorun == 'True': 
                self.autorun = True
            else: self.autorun = False

            
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.bind("<Unmap>", self.on_minimize)
            self.tray_icon = None

            self.notifier = ToastNotifier()
            
            if self.autorun:
                self.perform_autorun_actions()
                self.hide_window()
                return
            self.create_region()
            
            if not install_font_result:
                self.show_notification(text.inAppText['font_error_info'], title=text.inAppText['font_error'], func=self.open_folder, button=text.inAppText['fix_manually'], _type='error')

        def create_region(self, region=None):
            self.frame2.destroy()
            self.frame2 = CTkFrame(self, width=400)
            lbl_hi = CTkLabel(self.frame2, text=text.inAppText['region'], font=(FONT, 15))
            lbl_hi.pack(padx=10, pady=15, side=LEFT)

            update_logo = CTkImage(light_image=Image.open(DIRECTORY+"data/update_icon.png"), size=(20, 20))
            self.settings_button = CTkButton(self.frame2, text='', command=self.update_prog, width=25, height=25, image=update_logo)
            self.settings_button.pack(side="right", padx=(0, 10), pady=1)

            reg = CTkOptionMenu(self.frame2, values=[text.inAppText['ru'], text.inAppText['other']],
                                                            command=self.change_region, width=200)
            reg.pack(padx=10, pady=15, side=RIGHT, fill='both')
            reg.set(region if region else self.region)
            

            self.switch_var = StringVar(value="on" if self.process else "off")

            if self.region == 'RU':
                self.create_ru()
            else:
                self.create_other()

            self.frame2.pack(pady=10, padx=10, fill="both")

        def create_ru(self):
            self.frame1.destroy()
            self.frame1 = CTkFrame(self, width=400)
            checkbox_1 = CTkCheckBox(self.frame1, text=text.inAppText['dns'], command=self.dns_change, variable=self._active_dns, onvalue="True", offvalue="False",
                                font=(FONT, 15), width=400)
            checkbox_1.pack(padx=10, pady=10, side=TOP)
            
            switch = CTkSwitch(self.frame1, text=text.inAppText['on'], command=self.toggle_process, font=(FONT, 15), width=400,
                                    variable=self.switch_var, onvalue="on", offvalue="off")
            switch.pack(padx=10, pady=10, side=TOP)
            if not self.autorun:
                but_3 = CTkButton(self.frame1, text=text.inAppText['autorun_in'], font=(FONT, 15), width=400, command=self.install_service)
                but_3.pack(padx=10, pady=10, side=TOP)
            else:
                but_3 = CTkButton(self.frame1, text=text.inAppText['autorun_out'], font=(FONT, 15), width=400, command=self.remove_service)
                but_3.pack(padx=10, pady=10, side=TOP)
            
            but_4 = CTkButton(self.frame1, text=text.inAppText['update']+' blacklist.txt', font=(FONT, 15), width=400, command=self.update_txt)
            but_4.pack(padx=10, pady=10, side=TOP)
            self.frame1.pack(pady=10, padx=10, fill="both", expand=True)

        def create_other(self):
            self.frame1.destroy()
            self.frame1 = CTkFrame(self, width=400)
            checkbox_1 = CTkCheckBox(self.frame1, text=text.inAppText['dns'], command=self.dns_change, variable=self._active_dns, onvalue="True", offvalue="False",
                                font=(FONT, 15), width=400)
            checkbox_1.pack(padx=10, pady=10, side=TOP)
            switch = CTkSwitch(self.frame1, text=text.inAppText['on'], command=self.toggle_process, font=(FONT, 15), width=400,
                                    variable=self.switch_var, onvalue="on", offvalue="off")
            switch.pack(padx=10, pady=10, side=TOP)
            if not self.autorun:
                but_3 = CTkButton(self.frame1, text=text.inAppText['autorun_in'], font=(FONT, 15), width=400, command=self.install_service)
                but_3.pack(padx=10, pady=10, side=TOP)
            else:
                but_3 = CTkButton(self.frame1, text=text.inAppText['autorun_out'], font=(FONT, 15), width=400, command=self.remove_service)
                but_3.pack(padx=10, pady=10, side=TOP)
            self.frame1.pack(pady=10, padx=10, fill="both", expand=True)

        def update_blacklist_thread(self):
            return_code = 0
            self.is_update = True 
            was_running = self.stop_process()
            progress_toast = ProgressToast('GoodbyeDPI_app', text.inAppText['update_in_process'], text.inAppText['update_in_process_info'], 'russia_blacklist.txt')
            try:
                download_blacklist("https://p.thenewone.lol/domains-export.txt", progress_toast)
            except Exception as ex:
                self.show_notification(f"{ex}",title=text.inAppText['error'], func=self.update_txt, _type='error')
                return_code = 1
                
            self.is_update = False 
            if was_running:
                self.start_process()
            
            if return_code == 0:self.show_notification(text.inAppText['update_complete'])

        def update_txt(self):
            update_thread = threading.Thread(target=self.update_blacklist_thread)
            update_thread.start()   

        def update_prog(self):
            if not self.is_update:
                update_version = get_latest_release()
                if version != update_version:
                    result = messagebox.askyesno('GoodbyeDPI UI', text.inAppText['ask_update_prog'])
                    if result:
                        self.stop_process()
                        move_settings_file(SETTINGS_FILE_PATH, BACKUP_SETTINGS_FILE_PATH)
                        subprocess.Popen('update.exe -l '+settings.settings['GLOBAL']['language']+f' -v {update_version}')
                
                else:
                    messagebox.showinfo('GoodbyeDPI UI', text.inAppText['lastest_version'])

        def change_region(self, region):
            _region = settings.settings['REGION']['region']
            if region == _region:
                return
            else:
                config = configparser.ConfigParser()
                config.read(SETTINGS_FILE_PATH)
                config['REGION']['region'] = regions[region]
                with open(SETTINGS_FILE_PATH, 'w') as configfile:
                    config.write(configfile)
                settings.reload_settings()
                self.region = regions[region]
                self.create_region(region)

        def dns_change(self):
            if self._active_dns.get() == 'True': 
                self.active_dns = True
            else: self.active_dns = False

        def check_args(self):
            if self.region == 'RU':
                if self.active_dns:
                    return settings.settings['COMMANDS']['russia_blacklist_dnsredir'].split(", ")
                else:
                    return settings.settings['COMMANDS']['russia_blacklist'].split(", ")
            else:
                if self.active_dns:
                    return settings.settings['COMMANDS']['any_contry_dnsredir'].split(", ")
                else:
                    return settings.settings['COMMANDS']['any_contry'].split(", ")

        def toggle_process(self):
            if self.switch_var.get() == "on":
                self.start_process()
            else:
                self.stop_process()
        
        def start_process(self):
            _args = self.check_args()
            try:
                if not self.is_update:
                    self.process = start_process(*_args)
                    self.show_notification(text.inAppText['process']+" goodbyedpi.exe " + text.inAppText['run_comlete'])
                else:
                    self.show_notification(f"Cannot run process goodbyedpi.exe while updating is running", title=text.inAppText['error'], func=self.start_process, _type='error')
            except Exception as ex:
                self.show_notification(f"{ex}", title=text.inAppText['error'], func=self.start_process, _type='error')           
        
        def stop_process(self):
            if self.process:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == 'goodbyedpi.exe':
                        try:
                            proc.terminate()
                            self.show_notification(text.inAppText['process'] + " goodbyedpi.exe " + text.inAppText['close_complete'])
                            self.process = None
                            return True
                        except psutil.NoSuchProcess:
                            self.show_notification((text.inAppText['close_error'] + " goodbyedpi.exe. " + text.inAppText['close_error2']) , title=text.inAppText['error_title'], func=self.stop_process, _type='error')
                self.show_notification(text.inAppText['close_error'] +" goodbyedpi.exe. " + text.inAppText['close_error1'], title=text.inAppText['error_title'], func=self.stop_process, _type='error')
        
        def on_closing(self):
            if not DEBUG:
                if self.process: self.stop_process() 
            if not self.is_update: self.destroy()
            else:self.show_notification(f"Cannot close application while updating is running", title=text.inAppText['error'])

        def on_minimize(self, event):
            if self.state() == 'iconic':
                self.hide_window()

        def hide_window(self):
            self.show_notification(text.inAppText['tray_icon'], func=self.show_window)
            self.withdraw()
            self.create_tray_icon()

        def create_tray_icon(self):
            image = Image.open(DIRECTORY+"data/icon.png") 
            menu = (item(text.inAppText['maximize'] , self.show_window), item(text.inAppText['quit'] , self.exit_app))
            self.tray_icon = pystray.Icon("name", image, "GoodbyeDPI UI", menu)
            self.tray_icon.run()

        def show_window(self, icon=None, item=None):
            if self.tray_icon:
                self.tray_icon.stop()
            self.after(10, self.deiconify)
            self.after(10, self.lift)
            self.after(10, self.focus_force)
            

        def exit_app(self, icon, item):
            self.stop_process()
            self.tray_icon.stop()
            self.destroy()
            sys.exit(0)

        def perform_autorun_actions(self):
            self.start_process()
            self.create_region()
            

        def install_service(self):
            try:
                script_path = os.path.abspath(sys.argv[0])
                
                task_name = "GoodbyeDPI_UI_Autostart"

                command = f'schtasks /create /tn "{task_name}" /tr "\'{sys.executable}\'" /sc onlogon /rl highest /f'

                subprocess.run(command, check=True, shell=True)
                
                config = configparser.ConfigParser()
                config.read(SETTINGS_FILE_PATH)
                config['GLOBAL']['autorun'] = 'True'
                with open(SETTINGS_FILE_PATH, 'w') as configfile:
                    config.write(configfile)
                settings.reload_settings()
                self.autorun = True

                self.show_notification(text.inAppText['autorun_complete'])
                self.create_region()
            except Exception as ex:
                self.show_notification(f"{ex}", title=text.inAppText['autorun_error'], func=self.install_service, _type='error')

        def remove_service(self):
            try:
                task_name = "GoodbyeDPI_UI_Autostart"

                command = f'schtasks /delete /tn "{task_name}" /f'

                subprocess.run(command, check=True, shell=True)
                config = configparser.ConfigParser()
                config.read(SETTINGS_FILE_PATH)
                config['GLOBAL']['autorun'] = 'False'
                with open(SETTINGS_FILE_PATH, 'w') as configfile:
                    config.write(configfile)
                settings.reload_settings()
                self.autorun = False
                self.show_notification(text.inAppText['autorun_complete1'])
                self.create_region()
            except Exception as ex:
                self.show_notification(f"{ex}", title=text.inAppText['autorun_error1'], func=self.remove_service, _type='error')

        def show_notification_tread(self, title="GoodbyeDPI UI", message='123', button=None, func=None, _type='normal'):
            if _type=='normal':
                result = asyncio.run(show_message("GoodbyeDPI_app", title, message))
            else:
                result = asyncio.run(show_error("GoodbyeDPI_app", title, message, button if button else text.inAppText['retry']))
            if result.dismiss_reason == ToastDismissReason.NOT_DISMISSED:
                if func:
                    func()

        def show_notification(self, message, title="GoodbyeDPI UI", func=None, button=None, _type='normal'):
            self.notification_thread = threading.Thread(target=lambda: self.show_notification_tread(title, message, func=func, button=button, _type=_type))
            self.notification_thread.start() 

        def on_notification_click(self):
            self.show_window(None, None)

        def open_folder(self):
            os.startfile(os.path.dirname(os.path.abspath(__file__))+'/data/font')
            
    def func():pass
    
    window = MainWindow()
    mode = settings.settings['APPEARANCE_MODE']['mode']
    set_appearance_mode(mode)
    set_default_color_theme("blue")
    set_widget_scaling(1)
    window.iconbitmap(DIRECTORY+'data/icon.ico')
    window.mainloop()
    