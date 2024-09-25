import asyncio
import configparser
from datetime import datetime
import random
import shlex
import subprocess
import threading
from tkinter import messagebox
from PIL import Image, ImageTk
from customtkinter import *
import psutil
import pystray
from pystray import MenuItem as item
from tktooltip import ToolTip
import tkinter
from toasted import ToastDismissReason
from _data import VERSION, settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, REPO_NAME, REPO_OWNER, \
                    BACKUP_SETTINGS_FILE_PATH, PARAMETER_MAPPING, VALUE_PARAMETERS, text
from utils import change_setting, check_mica, create_xml, install_font, remove_xml, start_process, download_blacklist, move_settings_file, \
                    ProgressToast, register_app, show_message, show_error, get_latest_release,\
                    is_process_running, GoodbyedpiProcess
from settings import start_qt_settings
from pseudo_console_view import GoodbyedpiApp
from error_view import ErrorWindow

version = VERSION

regions = {
        text.inAppText['ru']:'RU',
        text.inAppText['other']:'OTHER'
    }

def func():pass

BaseWindow = tkinter.Tk if settings.settings.getboolean('APPEARANCE_MODE', 'use_mica') and check_mica() else CTk

class MainWindow(BaseWindow):
    def __init__(self, install_font_result, autorun, first_run) -> None:
        super().__init__()
        self.geometry('300x400')
        self.title(f'goodbyeDPI UI - v {version}')
        self.resizable(False, False)

        self.mica = settings.settings.getboolean('APPEARANCE_MODE', 'use_mica') if check_mica() else False

        if self.mica:self.configure(bg="black")

        self.notification_thread = None
        self.is_update = False

        self.frame1 = CTkFrame(self, width=400, fg_color='#0f0f0f') 

        self.region = settings.settings['REGION']['region']
        self.process = False

        self.proc = GoodbyedpiProcess(self)
        self.proc_terminal = None

        self.error_info_app = None

        self.settings_window = None
        self.updates_availible = False
        if not DEBUG:
            try:
                if settings.settings['GLOBAL']['notifyaboutupdates'] == "True":
                    version_to_update = get_latest_release()
                    self.updates_availible = version!=version_to_update
                    if self.updates_availible: 
                        change_setting('GLOBAL', 'version_to_update', version_to_update)
                        change_setting('GLOBAL', 'lastcheckedtime', datetime.now().strftime("%H:%M %d.%m.%Y"))

            except:pass
        facts = tuple(text.inAppText[f'fact{i}'] for i in range(1, 16))
        random_fact = random.choice(facts)

        if self.updates_availible:
            self.display_text = text.inAppText['news']+"|"+text.inAppText['news_tip']
        elif first_run == "True":
            self.display_text = text.inAppText['first_run']+"|"+text.inAppText['first_run_tip']
        else:
            self.display_text = text.inAppText['fact']+f"|{random_fact}"

        self.active_dns = settings.settings['GLOBAL']['change_dns']
        self._active_dns = StringVar(value=self.active_dns)
        if self.active_dns == 'True': 
            self.active_dns = True
        else: self.active_dns = False
        
        self.autorun = autorun
        if self.autorun == 'True': 
            self.autorun = True
        else: self.autorun = False

        self.proc_state = StringVar(value = text.inAppText['work'] if self.process else text.inAppText['stop'])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Unmap>", self.on_minimize)
        self.tray_icon = None

        self.switch_var = StringVar(value="on" if self.process else "off")
        print(self.autorun)
        if self.autorun:
            
            self.perform_autorun_actions()
            self.hide_window()
            return
        self.create_region()
        
        if not install_font_result:
            self.show_notification(text.inAppText['font_error_info'], title=text.inAppText['font_error'], func=self.open_folder, button=text.inAppText['fix_manually'], _type='error')

    def create_region(self, region=None):
        self.header_frame = CTkFrame(self, fg_color='#0f0f0f' if self.mica else None)
        self.logo = CTkImage(light_image=Image.open(DIRECTORY+"data/icon.ico"), size=(50, 50))
        self.logo_label = CTkLabel(self.header_frame, image=self.logo, text="")
        self.logo_label.pack(side="left", pady=10, padx=(10, 5))

        self.switch_var = StringVar(value="on" if self.process else "off")
        self.proc_state = StringVar(value = text.inAppText['work'] if self.switch_var.get() == 'on' else text.inAppText['stop'])

        self.header_text_frame = CTkFrame(self.header_frame, fg_color='transparent')
        

        self.header_text = CTkLabel(self.header_text_frame, text="GoodbyeDPI UI", anchor="w", font=(FONT, 18, "bold"))
        self.header_text.pack(pady=(10, 0), padx=(5, 10), fill="x", expand=True)

        self.status_label = CTkLabel(self.header_text_frame, textvariable=self.proc_state, anchor="w", justify='left', font=(FONT, 14))
        self.status_label.pack(side="bottom",padx=(5, 10), pady=(0, 10), fill="x", expand=True)

        self.header_text_frame.pack(fill='x', padx=(0,5))
        self.header_frame.pack(fill="x",pady=(10, 0), padx=10)

        reg = CTkButton(self, text=text.inAppText['open_settings'], font=(FONT, 15), command=self.open_settings, width=200)
        
        

        self.create_other()

        reg.pack(padx=10, pady=15, fill='both')

    def create_other(self):
        self.frame1.destroy()

        self.frame1 = CTkFrame(self, width=400, fg_color='#0f0f0f' if self.mica else None)
        switch = CTkSwitch(self.frame1, text=text.inAppText['on'], command=self.toggle_process, font=(FONT, 15), width=400,
                                variable=self.switch_var, onvalue="on", offvalue="off")
        switch.pack(padx=10, pady=(15, 10), side=TOP)

        icon_image = CTkImage(light_image=Image.open(DIRECTORY+"data/find.ico"), size=(20, 20))

        fact_frame = CTkFrame(self.frame1, fg_color="transparent")
        fact_frame.pack(padx=10, pady=10, side=BOTTOM)

        fact_heading_frame = CTkFrame(fact_frame, fg_color="transparent")
        fact_heading_frame.pack(padx=0, pady=(20, 5), fill='x')

        fact_icon_label = CTkLabel(fact_heading_frame, image=icon_image, text="")
        fact_icon_label.pack(side="left")

        fact_heading_label = CTkLabel(fact_heading_frame, text=self.display_text.split("|")[0], justify="left", font=(FONT, 14))
        fact_heading_label.pack(side="left", padx=5)


        info_label = CTkLabel(fact_frame, text=self.display_text.split("|")[1], font=(FONT, 13), anchor=W, justify="left", width=400, wraplength=260)
        info_label.pack(pady=0)

        self.frame1.pack(pady=10, padx=(10, 10), fill="both", expand=True)

    def update_blacklist_thread(self):
        return_code = 0
        self.is_update = True 
        was_running = self.stop_process(notf=False)
        progress_toast = ProgressToast('GoodbyeDPI_app', text.inAppText['update_in_process'], text.inAppText['update_in_process_info'], 'russia_blacklist.txt')
        try:
            download_blacklist("https://p.thenewone.lol/domains-export.txt", progress_toast)
        except Exception as ex:
            self.show_notification(f"{ex}",title=text.inAppText['error'], func=self.update_txt, _type='error', error=[type(ex).__name__, ex.args, 'NOT_CRITICAL_ERROR', 'window:update_blacklist_thread'])
            return_code = 1
            
        self.is_update = False 
        if was_running:
            self.start_process(notf=False)
        
        if return_code == 0:self.show_notification(text.inAppText['update_complete'])

    def update_txt(self):
        update_thread = threading.Thread(target=self.update_blacklist_thread)
        update_thread.start()   
    
    def open_settings(self):
        if self.settings_window is None or not self.settings_window.is_alive():
            self._open_settings()

    def _open_settings(self):
        parent_conn, self.settings_window = start_qt_settings()
        def check_pipe():
            if parent_conn.poll():
                data = parent_conn.recv()
                print(data)
                if data == 'SETTINGS_UPDATE_NEED':
                    settings.reload_settings()
                    self.active_dns = settings.settings['GLOBAL']['change_dns']
                    self._active_dns.set(self.active_dns)
                    if self.active_dns == 'True': 
                        self.active_dns = True
                    else: self.active_dns = False
                    print(self._active_dns.get())
                if data == 'OPEN_PSEUDOCONSOLE':
                    self.connect_terminal()
                if data == 'UPDATE_TXT':
                    self.update_txt()
                if data == 'ADD_TO_AUTORUN':
                    print("adding")
                    self.install_service()
                if data == 'REMOVE_FROM_AUTORUN':
                    print("removing")
                    self.remove_service()
                if data == 'UPDATE_INSTALL':
                    self.stop_process()
                    move_settings_file(SETTINGS_FILE_PATH, BACKUP_SETTINGS_FILE_PATH)
                    subprocess.Popen(f'update.exe -directory-to-unpack "'+ DIRECTORY.replace("_internal/", "") + '" -directory-to-zip "' + DIRECTORY + "_portable.zip" + '" -localize ' + settings.settings['GLOBAL']['language'])
                    self.on_closing()
                if data == "SET_MODE":
                    settings.reload_settings()
                    if settings.settings['APPEARANCE_MODE']['mode'] != get_appearance_mode():
                        set_appearance_mode(settings.settings['APPEARANCE_MODE']['mode'])

            self.after(100, check_pipe)

        self.after(100, check_pipe) 

    def check_args(self):
        if settings.settings['GLOBAL']['use_advanced_mode'] == 'True':
            command = []

            params = settings.settings['GOODBYEDPI']

            for ini_param, cmd_param in PARAMETER_MAPPING.items():
                if ini_param in params:
                    value = params.getboolean(ini_param)
                    if value:
                        value_key = f"{ini_param}_value"
                        if ini_param in VALUE_PARAMETERS and value_key in params:
                            param_value = params[value_key].strip()
                            if param_value:
                                command.append(cmd_param)
                                command.append(param_value)
                        else:
                            command.append(cmd_param)

            for ini_param, cmd_param in VALUE_PARAMETERS.items():
                if ini_param in params:
                    value = params.getboolean(ini_param)
                    value_key = f"{ini_param}_value"
                    if value and value_key in params:
                        param_value = params[value_key].strip()
                        if param_value:
                            command.append(cmd_param)
                            command.append(param_value)

            if 'blacklist_value' in params:
                blacklist_value = params['blacklist_value'].strip()
                if blacklist_value:
                    print(blacklist_value)
                    blacklist_files = blacklist_value.split(",")
                    print(blacklist_files)
                    for filePath in blacklist_files:
                        command.append('--blacklist')
                        print(filePath, filePath.strip("\'"))
                        command.append(str(filePath).strip("\""))

            if 'custom_parameters' in params:
                custom_params = params['custom_parameters']
                if custom_params:
                    custom_params_list = [param.strip() for param in custom_params.split(' ') if param.strip()]
                    command.extend(custom_params_list)
            print(command)
            return command
        else:
            command = []

            preset = int(settings.settings['GOODBYEDPI']['preset'])
            if preset <= 9:
                command.append("-"+str(preset))
            elif preset == 10:
                command.extend(["-9", "--fake-gen", "5", "--fake-from-hex", "160301FFFF01FFFFFF0303594F5552204144564552544953454D454E542048455245202D202431302F6D6F000000000009000000050003000000"])
            elif preset == 11:
                command.extend(["-5", "-e1", "-q", "--fake-gen", "5", "--fake-from-hex", "160301FFFF01FFFFFF0303594F5552204144564552544953454D454E542048455245202D202431302F6D6F000000000009000000050003000000"])

            if settings.settings['GLOBAL']['change_dns'] == 'True':
                dns_pompt = [VALUE_PARAMETERS['dns'], settings.settings['GOODBYEDPI']['dns_value'], VALUE_PARAMETERS['dns_port'], settings.settings['GOODBYEDPI']['dns_port_value'],
                             VALUE_PARAMETERS['dnsv6'], settings.settings['GOODBYEDPI']['dnsv6_value'], VALUE_PARAMETERS['dnsv6_port'], settings.settings['GOODBYEDPI']['dnsv6_port_value']]
                command.extend(dns_pompt)
            if settings.settings['GOODBYEDPI']['use_blacklist'] == 'True': command.extend(['--blacklist', '..//russia-blacklist.txt'])
            if settings.settings['GOODBYEDPI']['use_blacklist_custom'] == 'True': command.extend(['--blacklist', '..//custom_blacklist.txt'])

            return command

    def toggle_process(self):
        if self.switch_var.get() == "on":
            self.start_process()
        else:
            self.stop_process()
    
    def start_process(self, notf=True):
        settings.reload_settings()
        _args = self.check_args()
        try:
            if not self.is_update:
                _q = self.proc.start_goodbyedpi(_args)
                self.switch_var.set("on")
                self.proc_state.set(text.inAppText['work'] if self.switch_var.get() == 'on' else text.inAppText['stop'])
                print(self.switch_var.get())
                self.process = True
            else:
                self.show_notification(f"Cannot run process goodbyedpi.exe while updating is running", title=text.inAppText['error'], func=self.start_process, _type='error')
        except Exception as ex:
            self.show_notification(f"{ex}", title=text.inAppText['error'], func=self.start_process, _type='error', error=[type(ex).__name__, ex.args, 'CRITICAL_ERROR', 'window:start_process'])           
    
    def stop_process(self, notf=True):
        print("stopping")
        if not self.proc.stop_event.is_set():
            try:
                try:
                    self.proc.stop_goodbyedpi()
                except Exception as ex:
                    if not '[WinError 5]' in str(ex):
                        self.show_notification(text.inAppText['close_error'] +" goodbyedpi.exe. " + text.inAppText['close_error1'] + str(ex), title=text.inAppText['error_title'], func=self.stop_process, _type='error', error=[type(ex).__name__, ex.args, 'NOT_CRITICAL_ERROR', 'window:stop_process[self.proc.stop_goodbyedpi]'])
                        return False
                if notf:self.show_notification(text.inAppText['process'] + " goodbyedpi.exe " + text.inAppText['close_complete'])
                self.switch_var.set("off")
                self.proc_state.set(text.inAppText['work'] if self.switch_var.get() == 'on' else text.inAppText['stop'])
                print(self.switch_var.get())
                self.process = False
                return True
            except Exception as ex:
                self.show_notification(text.inAppText['close_error'] +" goodbyedpi.exe. " + text.inAppText['close_error1'] + str(ex), title=text.inAppText['error_title'], func=self.stop_process, _type='error', error=[type(ex).__name__, ex.args, 'NOT_CRITICAL_ERROR', 'window:stop_process[internal_error]'])
                return False
        return True
    
    def on_closing(self):
        if not DEBUG:
            self.stop_process() 
        if not self.is_update: 
            if self.settings_window and self.settings_window.is_alive():
                self.settings_window.terminate()
            self.destroy()
            sys.exit(0)
        else:self.show_notification(f"Cannot close application while updating is running", title=text.inAppText['error'])

    def on_minimize(self, event):
        if self.state() == 'iconic':
            if self.proc_terminal:
                self.proc_terminal.destroy()
            if self.settings_window and self.settings_window.is_alive():
                self.settings_window.terminate()
            self.hide_window()

    def hide_window(self):
        self.show_notification(text.inAppText['tray_icon'], func=self.show_window)
        self.withdraw()
        if self.tray_icon:
            self.tray_icon.visible = True
        else:
            self.create_tray_icon()

    def create_tray_icon(self):
        image = Image.open(DIRECTORY+"data/icon.png") 
        menu = (item(text.inAppText['maximize'] , self.show_window), item(text.inAppText['quit'] , self.exit_app))
        self.tray_icon = pystray.Icon("name", image, "GoodbyeDPI UI", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.visible = False
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
        if settings.settings['GLOBAL']['autorun'] == 'True':return
        try:
            task_name = "GoodbyeDPI_UI_Autostart"
            executable = sys.executable
            arguments = '--autorun'

            temp_xml_path = create_xml("GoodbyeDPI UI", executable, arguments)
            
            command = [
                'schtasks', '/create',
                '/tn', task_name,
                '/xml', temp_xml_path,
                '/f'
            ]

            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False
            )

            remove_xml(temp_xml_path)
            
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE_PATH)
            config['GLOBAL']['autorun'] = 'True'
            with open(SETTINGS_FILE_PATH, 'w') as configfile:
                config.write(configfile)
            settings.reload_settings()
            self.autorun = True
            self.show_notification(text.inAppText['autorun_complete'])
        except subprocess.CalledProcessError as ex:
            error_output = str(ex.stdout.decode('cp866', errors='replace'))
            self.show_notification(
                error_output.split("\n")[0],
                title=text.inAppText['autorun_error'],
                func=self.install_service,
                _type='error',
                error=["SYSTEM ERROR", error_output, 'NOT_CRITICAL_ERROR', 'window:install_service']
            )
        except Exception as ex:
            self.show_notification(f"{ex}", title=text.inAppText['autorun_error'], func=self.install_service, _type='error', error=[type(ex).__name__, ex.args, 'NOT_CRITICAL_ERROR', 'window:install_service'])

    def remove_service(self):
        if settings.settings['GLOBAL']['autorun'] == 'False':return
        try:
            task_name = "GoodbyeDPI_UI_Autostart"

            command = f'schtasks /delete /tn "{task_name}" /f'

            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False
            )
            
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE_PATH)
            config['GLOBAL']['autorun'] = 'False'
            with open(SETTINGS_FILE_PATH, 'w') as configfile:
                config.write(configfile)
            settings.reload_settings()
            self.autorun = False
            self.show_notification(text.inAppText['autorun_complete1'])
        except subprocess.CalledProcessError as ex:
            error_output = str(ex.stdout.decode('cp866', errors='replace'))
            self.show_notification(
                error_output.split("\n")[0],
                title=text.inAppText['autorun_error'],
                func=self.remove_service,
                _type='error',
                error=["SYSTEM ERROR", error_output, 'NOT_CRITICAL_ERROR', 'window:remove_service']
            )
        except Exception as ex:
            self.show_notification(f"{ex}", title=text.inAppText['autorun_error1'], func=self.remove_service, _type='error', error=[type(ex).__name__, ex.args, 'NOT_CRITICAL_ERROR', 'window:remove_service'])

    def show_notification_tread(self, title="GoodbyeDPI UI", message='123', button=None, func=None, _type='normal', error:tuple=None):
        if _type=='normal':
            result = asyncio.run(show_message("GoodbyeDPI_app", title, message))
        else:
            result = asyncio.run(show_error("GoodbyeDPI_app", title, message, button if button else text.inAppText['retry'], "подробности" if error else None))
        if result.dismiss_reason == ToastDismissReason.NOT_DISMISSED:
            if result.arguments == 'accept':
                if func:
                    func()
            elif result.arguments == 'call2':
                error_info = "Type: " +error[0] + "\n" + \
                             "From: " +error[3] + "\n" + \
                             str(error[1]) + "\n"
                if self.error_info_app and self.error_info_app.winfo_exists():
                    self.error_info_app.destroy()
                
                self.error_info_app = ErrorWindow(error[0], error[3], error[2], error_info)
            else:
                if func: func()

    def connect_terminal(self, error=False):
        if error:
            self.switch_var.set("off")
        if self.proc_terminal is None or not self.proc_terminal.winfo_exists():
            self.show_window()
            self.proc_terminal = GoodbyedpiApp(self.stop_process, self.start_process)
            self.proc.connect_app(self.proc_terminal)

        else:
            self.proc_terminal.focus()

    def show_notification(self, message, title="GoodbyeDPI UI", func=None, button=None, _type='normal', error=None):
        self.notification_thread = threading.Thread(target=lambda: self.show_notification_tread(title, message, func=func, button=button, _type=_type, error=error))
        self.notification_thread.start() 

    def on_notification_click(self):
        self.show_window(None, None)

    def open_folder(self):
        os.startfile(os.path.dirname(os.path.abspath(__file__))+'/data/font')
