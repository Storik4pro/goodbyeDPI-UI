# app icon
"""Download by Bence Bezeredy from <a href="https://thenounproject.com/browse/icons/term/download/" target="_blank" title="Download Icons">Noun Project</a> (CC BY 3.0)"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='update.log', level=logging.INFO)
import os
import requests
import zipfile
import shutil
import sys
import time
from customtkinter import *
import threading
import webbrowser
from PIL import Image
import configparser
import getopt
from tkinter import messagebox
from datetime import datetime
from about import AboutApp
import psutil

DEBUG = False

ERROR_TITLE = "Update assistant error"
REPO_OWNER = "Storik4pro"
REPO_NAME = "goodbyeDPI-UI"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
FONT = 'Nunito SemiBold'
DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}/update/' if not DEBUG else 'update/'
directory = "./"
about_app = None

class Text:
    def __init__(self, language) -> None:
        self.inAppText = {'': ''}
        self.reload_text(language)

    def reload_text(self, language=None):
        self.selectLanguage = language if language else 'EN' 
        config = configparser.ConfigParser()
        config.read(DIRECTORY+'loc.ini', encoding='utf-8')
        self.inAppText = config[f'{self.selectLanguage}']

text = Text('EN')

def open_git():
    webbrowser.open("https://storik4pro.github.io/installer-issues/")

def open_about():
    global about_app
    if about_app is None or not about_app.winfo_exists():
        about_app = AboutApp(text.inAppText, FONT, DIRECTORY, REPO_URL)
        about_app.mainloop()
    else:
        about_app.focus()

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

class UpdaterApp(CTk):
    def __init__(self, version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version
        self.geometry("480x480")
        self.resizable(False, False)
        self.title(f"Update assistant")
        self.iconbitmap(DIRECTORY+'update_icon.ico')

        self.header_label = CTkLabel(self, text=text.inAppText['update_ready']+f" {self.version}", font=(FONT, 20, "bold"))
        self.header_label.pack(pady=10)

        self.content_frame = CTkFrame(self)
        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.changelog_textbox = CTkTextbox(self.content_frame, wrap="word", width=400, height=150, font=(FONT, 15))
        self.changelog_textbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.changelog_textbox.insert("1.0", text.inAppText['update_info_load'])
        self.changelog_textbox.configure(state="disabled")

        self.checkbox = StringVar(value='True')
        self.restart_button = CTkButton(self.content_frame, text=text.inAppText['update_retry'], font=(FONT, 15), command=self.start_update_thread, width=400)

        self.start_button = CTkButton(self.content_frame, text=text.inAppText['update_start'], font=(FONT, 15), command=self.start_update_thread, width=400)
        self.start_button.pack(pady=20, padx=10, fill="both")

        self.separator = CTkLabel(self, text="─" * 100)
        self.separator.pack(pady=(5, 0))

        self.link_frame = CTkFrame(self)
        self.link_frame.pack(pady=(0, 10))

        github_logo = CTkImage(light_image=Image.open(DIRECTORY+"help.png"), size=(24, 24))
        self.github_image_button = CTkButton(self.link_frame, text='', command=open_git, width=30,height=30, image=github_logo)
        self.github_image_button.pack(side="left", padx=(10, 10), pady=10)

        settings_logo = CTkImage(light_image=Image.open(DIRECTORY+"info.png"), size=(24, 24))
        self.settings_button = CTkButton(self.link_frame, text='', command=open_about, width=30, height=30, image=settings_logo)
        self.settings_button.pack(side="left", padx=(0, 10), pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.load_changelog()

        self.finish_status = 0
        self.now_id = 1

    def on_closing(self):
        if hasattr(self, 'updating') and self.updating.is_alive():
            self.header_label.configure(text=text.inAppText['update_in_process'])
        else:
            self.destroy()

    def start_update_thread(self):
        self.start_button.configure(state="disabled")
        self.updating = threading.Thread(target=self.update_program)
        self.updating.start()

    def get_release_info(self):
        logger.info(f'getting release info ...')
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{self.version}"
        response = requests.get(url)
        data = response.json()
        return data

    def format_changelog(self, changelog):
        changelog = changelog.replace("### ", "").replace("## ", "").replace("# ", "")
        return changelog

    def load_changelog(self):
        data = self.get_release_info()
        changelog = data.get("body", text.inAppText['update_info_error'])
        formatted_changelog = self.format_changelog(changelog)
        self.changelog_textbox.configure(state="normal")
        self.changelog_textbox.delete("1.0", "end")
        self.changelog_textbox.insert("1.0", formatted_changelog)
        self.changelog_textbox.configure(state="disabled")

    def create_logs(self, text, stop=True):
        _time = datetime.now().strftime('%H:%M:%S')
        logger.info(f'[{_time}] {text}')
        self.log_label.configure(text=f''+text+'\n')

    def get_download_url(self):
        try:
            data = self.get_release_info()
            download_url = None

            for asset in data["assets"]:
                if asset["name"].endswith(".zip"):
                    download_url = asset["browser_download_url"]
                    break

            return download_url
        except Exception as ex:
            logger.error(text.inAppText['check_internet']+f"\n{ex}", exc_info=1)
            self.finish_status = 1
            messagebox.showerror(ERROR_TITLE, text.inAppText['check_internet']+f"\n{ex}")

    def download_and_extract(self, url):
        try:
            extract_to=directory if not DEBUG else 'goodbyeDPI UI/'
            local_filename = extract_to+url.split('/')[-1]
            last_persent = 0
            self.create_logs(f"Downloading archive ...")
            
            with requests.get(url, stream=True) as r:
                total_length = r.headers.get('content-length')
                if total_length is None:
                    with open(local_filename, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                else:
                    dl = 0
                    total_length = int(total_length)
                    with open(local_filename, 'wb') as f:
                        for data in r.iter_content(chunk_size=4096):
                            if int((dl / total_length) * 100) > last_persent:
                                self.create_logs(f"Downloading archive {int((dl / total_length) * 100)} % [{dl}/{total_length}]", True)
                                last_persent = int((dl / total_length) * 100)
                                self.progress_var.set((dl / total_length))
                            dl += len(data)
                            f.write(data)
                            self.update_idletasks()
            self.create_logs(f"Preparing for unpacking ...")
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
            self.progress_var.set((100))
            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.startswith('goodbyeDPI UI/'):
                        target_path = os.path.join(extract_to, os.path.relpath(member, 'GoodbyeDPI UI'))
                        target_dir = os.path.dirname(target_path)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                        try:
                            if not member.endswith('/'):
                                source = zip_ref.open(member)
                                if str(source.name.split('/')[-1]) != 'update.exe':
                                    target = open(target_path, "wb")
                                    self.create_logs(f"Unpacking the '{source.name.split('/')[-1]}' file")
                                    with source, target:
                                        shutil.copyfileobj(source, target)
                        except PermissionError as ex:
                            logger.error(f'Permission error {ex}')
                            result=messagebox.askyesno('Permission error',f'{ex}'+"\n"+text.inAppText['update_ask'])
                            if result:
                                pass
                            else:
                                self.finish_status = 1
                                logger.error(f'process canceled by user')
                                return
            os.remove(local_filename)
        except Exception as ex:
            messagebox.showerror('An error just occurred', ex)
            logger.error(f'download or extract failed {ex}')
            self.finish_status = 1

    def update_program(self):
        self.finish_status = 0
        close_procces()
        self.start_button.destroy()
        self.restart_button.destroy()

        self.progress_var = DoubleVar(value=0)
        self.progress_bar = CTkProgressBar(self.content_frame, variable=self.progress_var, width=400)
        self.progress_bar.pack(pady=(10, 0), padx=10, fill="both")

        self.log_label = CTkLabel(self.content_frame, text=text.inAppText['update_log'], width=400, font=(FONT, 15))
        self.log_label.pack(pady=0, padx=10, fill="both")


        self.create_logs(f"Getting ready URL")
        self.header_label.configure(text=text.inAppText['update_downloading'])
        download_url = self.get_download_url()
        self.create_logs(f"Getting ready for downloading ...")
        self.download_and_extract(download_url)

        self.header_label.configure(text=text.inAppText['update_installing'])
        time.sleep(2)
        if self.finish_status != 0:
            self.header_label.configure(text=text.inAppText['update_error'])
        else:
            self.header_label.configure(text=text.inAppText['update_complete'])
        self.progress_var.set(100)

        self.finish_update()

    def finish_update(self):
        self.log_label.destroy()
        self.progress_bar.destroy()
        if self.finish_status == 0:
            self.checkbox_1 = CTkCheckBox(self.content_frame, text=text.inAppText['run'], command=self.run_program, variable=self.checkbox, onvalue="True", offvalue="False",
                                    font=(FONT, 15), width=400)
            self.checkbox_1.pack(pady=10, padx=10, fill="both")
        else:
            self.restart_button = CTkButton(self.content_frame, text=text.inAppText['update_retry'], font=(FONT, 15), command=self.start_update_thread, width=400)
            self.restart_button.pack(pady=(0, 20), padx=10, fill="both")
        self.start_button = CTkButton(self.content_frame, text=text.inAppText['exit'], font=(FONT, 15), command=self.restart_program, width=400)
        self.start_button.pack(pady=(0, 20), padx=10, fill="both")

    def run_program(self):
        pass

    def restart_program(self):
        if self.checkbox.get() == 'True' and self.finish_status==0: 
            try:
                if directory == '.':
                    os.execv('../'+"goodbyeDPI.exe", ['../'+"goodbyeDPI.exe"])
                else:
                    os.execv(directory+"goodbyeDPI.exe", [directory+"goodbyeDPI.exe"])
            except Exception as ex:
                logger.error(f'executing failure {ex}. Directory {directory+"goodbyeDPI.exe"}')
                messagebox.showerror('An error just occurred', ex)
        sys.exit(0)

def get_latest_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    logger.info(f'url used: {url}')
    response = requests.get(url)
    data = response.json()
    latest_version = data["tag_name"]
    logger.info(f'version for update: {latest_version}')

    return latest_version

version =""
lang ="EN"
if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        options, args = getopt.getopt(argv, "v:l:d:",
                                    ["version =",
                                        "language =",
                                        "directory ="])
    except:
        logger.info(text.inAppText['version_error'])
        messagebox.showinfo('Update assistant', text.inAppText['version_error'])
    
    for name, value in options:
        if name in ['-v', '--version']:
            version = value
        elif name in ['-l', '--language']:
            lang = value
        elif name in ['-d', '--directory']:
            directory = value+'/'
    text.reload_text(lang)
    if version == '':
        logger.info(text.inAppText['version_error'])
        messagebox.showinfo('Update assistant', text.inAppText['version_error'])
        version = get_latest_release()
    logger.info('getting ready app')
    app = UpdaterApp(version)
    logger.info('app started successfully')
    app.mainloop()