import configparser
import logging
import os
import zipfile
import sys
import threading
from tkinter import messagebox
from datetime import datetime
import argparse
from customtkinter import *
from PIL import Image
import subprocess
import shutil

import psutil

FONT = 'Nunito SemiBold'
DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}/'
logger = logging.getLogger(__name__)
logging.basicConfig(filename='update.log', level=logging.INFO)

zapret_path = "_internal/data/zapret"
config_path = "_internal/data/settings/"
skip_files = [
    "update.exe", "custom_blacklist.txt", 
    f"WinDivert64.sys", f"list-discord.txt",
    f"list-general.txt", f"list-youtube.txt", 
    "user.json", "youtube.txt"
]

def close_procces():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'goodbyedpi.exe':
            try:
                proc.terminate()
                logger.info(f'process goodbyedpi.exe terminated')
            except psutil.NoSuchProcess:
                pass
        if proc.info['name'] == 'goodbyeDPI.exe':
            try:
                proc.terminate()
                logger.info(f'process goodbyeDPI.exe terminated')
            except psutil.NoSuchProcess:
                pass

class Text:
    def __init__(self, language) -> None:
        self.inAppText = {'': ''}
        self.reload_text(language)

    def reload_text(self, language=None):
        self.selectLanguage = language if language else 'EN' 
        config = configparser.ConfigParser()
        config.read(DIRECTORY+'loc.ini', encoding='utf-8')
        self.inAppText = config[f'{self.selectLanguage}']

class UpdaterApp(CTk):
    def __init__(self, zip_file_path, unpack_directory, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_file_path = zip_file_path
        self.unpack_directory = unpack_directory
        self.geometry("800x500")
        self.resizable(False, False)
        self.title("Update Assistant")
        self.iconbitmap(DIRECTORY+'update_icon.ico')
        self.end = False

        self.content_frame = CTkFrame(self)
        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.header_frame = CTkFrame(self.content_frame)
        self.header_frame.pack(fill="x", pady=(10, 0), padx=10)

        self.logo = CTkImage(light_image=Image.open(DIRECTORY+"update_icon.png"), size=(50, 50))
        self.logo_label = CTkLabel(self.header_frame, image=self.logo, text="")
        self.logo_label.pack(side="left", pady=10, padx=(10, 5))

        self.header_text_frame = CTkFrame(self.header_frame, fg_color='transparent')
        self.header_text_frame.pack(fill='x')

        self.header_text = CTkLabel(self.header_text_frame, text = text.inAppText['update_log'], anchor="w", font=(FONT, 18, "bold"))
        self.header_text.pack(pady=(10, 0), padx=(5, 10), fill="x", expand=True)

        self.status_text = text.inAppText['update_installing']
        self.status_label = CTkLabel(self.header_text_frame, text=self.status_text, anchor="w", justify='left', font=(FONT, 14))
        self.status_label.pack(side="bottom", padx=(5, 10), pady=(0, 10), fill="x", expand=True)

        self.textbox_frame = CTkFrame(self.content_frame, fg_color='transparent')
        self.textbox_frame.pack(fill="both", expand=True)

        self.changelog_textbox = CTkTextbox(self.textbox_frame, wrap="word", font=(FONT, 15))
        self.changelog_textbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.changelog_textbox.configure(state="disabled")

        self.progress_var = DoubleVar(value=0)
        self.progress_bar = CTkProgressBar(self.content_frame, variable=self.progress_var)
        self.progress_bar.pack(pady=(10, 0), padx=10, fill="x")

        self.button_frame = CTkFrame(self.content_frame, fg_color='transparent')
        self.button_frame.pack(fill="x", side='bottom')

        self.exit_button = CTkButton(self.button_frame, text=text.inAppText['exit'], fg_color="transparent", border_width=2, font=(FONT, 15), width=200, state=DISABLED, command=self.safe_exit)
        self.exit_button.pack(side="right", padx=(5, 10), pady=10)

        self.finish_status = 0

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.updating = threading.Thread(target=self.update_program)
        self.updating.start()

    def on_closing(self):
        if self.end:
            try:
                self.safe_exit()
            except: sys.exit(0)

    def create_logs(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        logger.info(f'[{_time}] {text}')
        self.changelog_textbox.configure(state="normal")
        self.changelog_textbox.insert("end", f"\n[{_time}] {text}")
        self.changelog_textbox.see("end")
        self.changelog_textbox.configure(state="disabled")
        self.status_label.configure(text=text)

    def update_program(self):
        self.create_logs("Starting extraction process")
        self.extract_zip()
        if self.finish_status == 0:
            self.header_text.configure(text="Update Complete")
            self.status_label.configure(text="Extraction completed successfully.")
            self.create_logs("Extraction completed successfully.")
            self.launch_application()
        else:
            self.header_text.configure(text="Update Error")
            self.status_label.configure(text="An error occurred during extraction.")
            self.create_logs("An error occurred during extraction.")
            self.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def extract_zip(self):
        try:
            zip_file = self.zip_file_path
            extract_to = self.unpack_directory

            if not os.path.exists(extract_to):
                os.makedirs(extract_to)

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                members = zip_ref.infolist()
                total_files = len(members)
                extracted_files = 0

                index = 0  
                while index < len(members):
                    member = members[index]
                    member_path = member.filename
                    if member_path.startswith("goodbyeDPI UI/"):
                        relative_path = member_path[len("goodbyeDPI UI/"):]
                        if relative_path == '':
                            index += 1
                            continue 
                        
                        

                        destination_path = os.path.join(extract_to, relative_path)
                        destination_dir = os.path.dirname(destination_path)
                        
                        if relative_path.split("/")[-1] in skip_files and os.path.exists(destination_path):
                            self.create_logs(f"Skipping {relative_path}")
                            index += 1
                            continue
                        
                        if relative_path.split("/")[-1].split(".")[-1] == 'txt' and os.path.exists(destination_path):
                            self.create_logs(f"Skipping {relative_path}")
                            index += 1
                            continue
                        
                        if not os.path.exists(destination_dir):
                            os.makedirs(destination_dir)

                        if member.is_dir():
                            if not os.path.exists(destination_path):
                                os.makedirs(destination_path)
                        else:
                            try:
                                with zip_ref.open(member) as source, open(destination_path, "wb") as target:
                                    shutil.copyfileobj(source, target)
                            except OSError as pe:
                                print(pe.errno)
                                if '13' in str(pe.errno):
                                    self.create_logs(f"Permission denied when extracting {relative_path}")
                                    user_choice = self.show_permission_error_dialog(relative_path)
                                    if user_choice == "skip":
                                        self.create_logs(f"Skipping {relative_path}")
                                        index += 1
                                        continue
                                    elif user_choice == "retry":
                                        self.create_logs(f"Retrying {relative_path}")
                                        continue 
                                    elif user_choice == "cancel":
                                        self.create_logs("Installation cancelled by user.")
                                        self.finish_status = 1
                                        return
                                else:
                                    self.create_logs(f"Error extracting {relative_path}: {ex}")
                                    messagebox.showerror('Error', f"Error extracting {relative_path}:\n{ex}")
                                    self.finish_status = 1
                                    return
                            except Exception as ex:
                                self.create_logs(f"Error extracting {relative_path}: {ex}")
                                messagebox.showerror('Error', f"Error extracting {relative_path}:\n{ex}")
                                self.finish_status = 1
                                return

                        extracted_files += 1
                        progress = extracted_files / total_files
                        self.progress_var.set(progress)
                        self.create_logs(f"Extracted {relative_path}")
                        self.update_idletasks()
                    index += 1  

        except Exception as ex:
            messagebox.showerror('An error occurred', str(ex))
            logger.error(f'Extraction failed: {ex}', exc_info=True)
            self.finish_status = 1

    def show_permission_error_dialog(self, file_name):
        dialog = CTkToplevel(self)
        dialog.title("Cannot extract file")
        dialog_width = 400
        dialog_height = 205

        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog_width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        dialog.resizable(False, False)
        dialog.transient(self)  
        dialog.grab_set() 

        dialog.after(200, lambda: dialog.iconbitmap(DIRECTORY+'update_icon.ico'))
        
        top_frame = CTkFrame(dialog, corner_radius=0)
        top_frame.pack(fill=X, padx=10, pady=5)

        file_icon_image = Image.open(DIRECTORY+"file_icon.png") 
        file_icon_photo = CTkImage(file_icon_image, size=(50, 50))
        file_icon_label = CTkLabel(top_frame, text="", image=file_icon_photo)
        file_icon_label.pack(side=LEFT, padx=10)

        text_frame = CTkFrame(top_frame, corner_radius=0)
        text_frame.pack(fill=X, expand=True)

        cannot_extract_label = CTkLabel(text_frame, text=text.inAppText['error1'], font=(FONT, 16, "bold"))
        cannot_extract_label.pack(anchor='nw', padx=20)

        file_name_label = CTkLabel(text_frame, text=file_name, font=(FONT, 12))
        file_name_label.pack(anchor='sw', pady=(0, 0), padx=20)

        bottom_frame = CTkFrame(dialog, fg_color='transparent')
        bottom_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        skip_icon = Image.open(DIRECTORY+"skip_icon.png")  
        skip_icon_photo = CTkImage(light_image=skip_icon, size=(20, 20))

        retry_icon = Image.open(DIRECTORY+"retry_icon.png")  
        retry_icon_photo = CTkImage(light_image=retry_icon, size=(20, 20))

        cancel_icon = Image.open(DIRECTORY+"cancel_icon.png") 
        cancel_icon_photo = CTkImage(light_image=cancel_icon, size=(20, 20))

        def on_skip():
            dialog.destroy()
            return_value[0] = "skip"

        def on_retry():
            dialog.destroy()
            return_value[0] = "retry"

        def on_cancel():
            if messagebox.askyesno("Confirm Cancellation", "Cancelling the installation may cause issues. Do you wish to continue?"):
                dialog.destroy()
                return_value[0] = "cancel"
            else:
                pass

        return_value = [None]

        button_width = dialog_width - 40  

        skip_button = CTkButton(bottom_frame, text=text.inAppText['skip'], width=button_width, height=40,
            corner_radius=0, image=skip_icon_photo, fg_color='transparent', text_color=['black', 'white'], border_width=1,
             anchor='w', command=on_skip, compound='left')
        skip_button.configure(font=(FONT, 14))
        skip_button.pack(fill=X, pady=1)

        retry_button = CTkButton(bottom_frame, text=text.inAppText['retry'], width=button_width, height=40,
             corner_radius=0, image=retry_icon_photo, fg_color='transparent', text_color=['black', 'white'], border_width=1, 
             anchor='w', command=on_retry, compound='left')
        retry_button.configure(font=(FONT, 14))
        retry_button.pack(fill=X, pady=1)

        cancel_button = CTkButton(bottom_frame, text=text.inAppText['exit'], width=button_width, height=40, 
             corner_radius=0, image=cancel_icon_photo, fg_color='transparent', text_color=['black', 'white'], border_width=1, 
             anchor='w', command=on_cancel, compound='left')
        cancel_button.configure(font=(FONT, 14))
        cancel_button.pack(fill=X, pady=1)

        self.wait_window(dialog)
        return return_value[0]

    def launch_application(self):
        try:
            goodbye_dpi_exe = os.path.join(self.unpack_directory, "goodbyeDPI.exe")
            if os.path.exists(goodbye_dpi_exe):
                self.create_logs("Launching goodbyeDPI.exe with --after-update parameter")
                subprocess.Popen([goodbye_dpi_exe, "--after-update"], creationflags=subprocess.DETACHED_PROCESS)

                self.end = True
                self.after(0, self.safe_exit)
                
            else:
                raise FileNotFoundError(f"{goodbye_dpi_exe} not found")
        except Exception as ex:
            self.after(0, self.handle_launch_error, ex)
    
    def handle_launch_error(self, ex):
        messagebox.showerror('An error occurred', str(ex))
        logger.error(f'Failed to launch application: {ex}', exc_info=True)
        self.finish_status = 1
        self.exit_button.configure(state='normal')
        self.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def safe_exit(self):
        self.destroy()
        self.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory-to-unpack', required=True, help='Directory to unpack to')
    parser.add_argument('-directory-to-zip', required=True, help='Path to zip file to unpack')
    parser.add_argument('-localize', required=True, help='Localization for UI')
    args = parser.parse_args()

    zip_file_path = args.directory_to_zip
    unpack_directory = args.directory_to_unpack
    loc = args.localize

    text = Text(loc)

    logger.info('Starting UpdaterApp')
    close_procces()
    app = UpdaterApp(zip_file_path, unpack_directory, text)
    logger.info('App started successfully')
    app.mainloop()
