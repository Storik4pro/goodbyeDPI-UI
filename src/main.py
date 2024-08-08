from tkinter import messagebox
import sys
import subprocess
import os
import ctypes

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


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
else:
    import tkinter.ttk 
    from tkinter import filedialog
    from tkinter.font import Font
    import ctypes.wintypes
    import darkdetect
    from customtkinter import *
    from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, text
    from utils import install_font
    import pywintypes
    import configparser
    import psutil
    from win10toast_click import ToastNotifier
    from plyer import notification
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageTk

    first_run = settings.settings['GLOBAL']['is_first_run']
    if first_run == 'True':
        install_font('data/font/Nunito-SemiBold.ttf')
        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE_PATH)
        config['GLOBAL']['is_first_run'] = 'False'
        with open(SETTINGS_FILE_PATH, 'w') as configfile:
            config.write(configfile)
        settings.reload_settings()

    version = "1.0.0"

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

            self.frame1 = CTkFrame(self, width=400) 
            self.frame2 = CTkFrame(self, width=400)

            self.region = settings.settings['REGION']['region']
            self.process = None
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

        def create_region(self, region=None):
            self.frame2.destroy()
            self.frame2 = CTkFrame(self, width=400)
            lbl_hi = CTkLabel(self.frame2, text=text.inAppText['region'], font=(FONT, 15))
            lbl_hi.pack(padx=10, pady=15, side=LEFT)
            reg = CTkOptionMenu(self.frame2, values=[text.inAppText['ru'], text.inAppText['other']],
                                                            command=self.change_region, width=400)
            reg.pack(padx=10, pady=15, side=RIGHT, fill="both")
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

        def update_txt(self):
            try:
                subprocess.Popen(['cmd', '/c', '0_russia_update_blacklist_file.cmd'], shell=True, cwd=GOODBYE_DPI_PATH, creationflags=subprocess.CREATE_NO_WINDOW)
                self.show_notification(text.inAppText['update_complete'])
            except Exception as ex:
                messagebox.showerror('An error just ocruppted', f"{ex}")
                self.show_notification(f"{ex}",title=text.inAppText['error'])

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

        def check_comma(self):
            if self.region == 'RU':
                if self.active_dns:
                    return "1_russia_blacklist_dnsredir.cmd"
                else:
                    return "1_russia_blacklist.cmd"
            else:
                if self.active_dns:
                    return "2_any_country_dnsredir.cmd"
                else:
                    return "2_any_country.cmd"

        def toggle_process(self):
            if self.switch_var.get() == "on":
                self.start_process()
            else:
                self.stop_process()
        
        def start_process(self):
            cmd_file = self.check_comma()
            try:
                self.process = subprocess.Popen(["cmd", "/c", cmd_file],cwd=GOODBYE_DPI_PATH, creationflags=subprocess.CREATE_NO_WINDOW)
                self.show_notification(text.inAppText['process']+" goodbyedpi.exe " + text.inAppText['run_comlete'])
            except Exception as ex:
                self.show_notification(f"{ex}", title=text.inAppText['error'])
        
        def stop_process(self):
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait()
                except psutil.NoSuchProcess:
                    pass
                self.process = None

            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'goodbyedpi.exe':
                    try:
                        proc.terminate()
                        self.show_notification(text.inAppText['process'] + " goodbyedpi.exe " + text.inAppText['close_complete'])
                        return
                    except psutil.NoSuchProcess:
                        self.show_notification((text.inAppText['close_error'] + " goodbyedpi.exe. " + text.inAppText['close_error1']) , title=text.inAppText['error_title'] )
            self.show_notification(text.inAppText['close_error'] +" goodbyedpi.exe. " + text.inAppText['close_error1'], title=text.inAppText['error_title'] )

        def on_closing(self):
            if self.process: self.stop_process() 
            self.destroy()  

        def on_minimize(self, event):
            if self.state() == 'iconic':
                self.hide_window()

        def hide_window(self):
            self.withdraw()
            self.create_tray_icon()

        def create_tray_icon(self):
            image = Image.open("data/icon.png") 
            menu = (item(text.inAppText['maximize'] , self.show_window), item(text.inAppText['quit'] , self.exit_app))
            self.tray_icon = pystray.Icon("name", image, "GoodbyeDPI UI", menu)
            self.tray_icon.run()

        def show_window(self, icon=None, item=None):
            if self.tray_icon:
                self.tray_icon.stop()
            self.after(0, self.deiconify)
            self.after(0, self.lift)
            self.after(0, self.focus_force)
            

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

                command = f'schtasks /create /tn "{task_name}" /tr "{sys.executable}" /sc onlogon /rl highest /f'

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
                self.show_notification(f"{ex}", title=text.inAppText['autorun_error'] )

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
                self.show_notification(f"{ex}", title=text.inAppText['autorun_error1'])
        

        def show_notification(self, message, title="GoodbyeDPI UI"):
            print(message, title)
            self.notifier = ToastNotifier()
            self.notifier.show_toast(
            title,
            str(message),
            icon_path="data/icon.ico",
            duration=10,
            threaded=True,
            callback_on_click=self.on_notification_click
            )

        def on_notification_click(self):
            self.show_window(None, None)
            
    def func():pass
    
    window = MainWindow()
    mode = settings.settings['APPEARANCE_MODE']['mode']
    set_appearance_mode(mode)
    set_default_color_theme("blue")
    set_widget_scaling(1)
    window.iconbitmap('data/icon.ico')
    window.mainloop()
    