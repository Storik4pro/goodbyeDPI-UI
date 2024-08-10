# app icon
"""Download by Bence Bezeredy from <a href="https://thenounproject.com/browse/icons/term/download/" target="_blank" title="Download Icons">Noun Project</a> (CC BY 3.0)"""
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

DEBUG = False

REPO_OWNER = "Storik4pro"
REPO_NAME = "goodbyeDPI-UI"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
FONT = 'Nunito SemiBold'
DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}/' if not DEBUG else 'update/'
directory = "."
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

class UpdaterApp(CTk):
    def __init__(self, version, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version
        self.geometry("480x480")
        self.resizable(False, False)
        self.title(f"Update assistant")

        self.main_frame = CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.header_label = CTkLabel(self.main_frame, text=text.inAppText['update_ready']+f" {self.version}", font=(FONT, 20, "bold"))
        self.header_label.pack(pady=10)

        self.content_frame = CTkFrame(self.main_frame)
        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.changelog_textbox = CTkTextbox(self.content_frame, wrap="word", width=400, height=150, font=(FONT, 15))
        self.changelog_textbox.pack(pady=10)
        self.changelog_textbox.insert("1.0", text.inAppText['update_info_load'])
        self.changelog_textbox.configure(state="disabled")

        self.progress_var = DoubleVar(value=0)
        self.progress_bar = CTkProgressBar(self.content_frame, variable=self.progress_var, width=400)
        self.progress_bar.pack(pady=10)

        self.checkbox = StringVar(value='True')

        self.start_button = CTkButton(self.content_frame, text=text.inAppText['update_start'], font=(FONT, 15), command=self.start_update_thread, width=400)
        self.start_button.pack(pady=20)

        self.separator = CTkLabel(self.main_frame, text="─" * 100)
        self.separator.pack(pady=(5, 0))

        self.link_frame = CTkFrame(self.main_frame)
        self.link_frame.pack(pady=(0, 10))

        github_logo = CTkImage(light_image=Image.open(DIRECTORY+"github-mark-white.png"), size=(24, 24))
        self.github_image_label = CTkLabel(self.link_frame, image=github_logo, text="")
        self.github_image_label.pack(side="left", padx=(20, 10), pady=10)

        self.repo_link = CTkLabel(self.link_frame, text=text.inAppText['goto_github'],text_color="#FFFFFF", font=(FONT, 15, "bold"), fg_color="#333333", cursor="hand2")
        self.repo_link.pack(side="left", padx=(0, 20))
        self.repo_link.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.load_changelog()

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

    def get_download_url(self):
        data = self.get_release_info()
        download_url = None

        for asset in data["assets"]:
            if asset["name"].endswith(".zip"):
                download_url = asset["browser_download_url"]
                break

        return download_url

    def download_and_extract(self, url, extract_to=directory):
        try:
            local_filename = url.split('/')[-1]
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
                            dl += len(data)
                            f.write(data)
                            self.progress_var.set((dl / total_length) * 100)
                            self.update_idletasks()

            with zipfile.ZipFile(local_filename, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.startswith('GoodbyeDPI UI/'):
                        filename = os.path.basename(member)
                        if filename:
                            source = zip_ref.open(member)
                            target = open(os.path.join(extract_to, filename), "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)

            os.remove(local_filename)
        except Exception as ex:
            messagebox.showerror('An error just occurred', ex)

    def update_program(self):
        self.header_label.configure(text=text.inAppText['update_downloading'])
        download_url = self.get_download_url()
        self.download_and_extract(download_url)

        self.header_label.configure(text=text.inAppText['update_installing'])
        self.progress_var.set(90)
        time.sleep(2)

        self.header_label.configure(text=text.inAppText['update_complete'])
        self.progress_var.set(100)

        self.finish_update()

    def finish_update(self):
        self.progress_bar.destroy()
        self.start_button.destroy()

        self.checkbox_1 = CTkCheckBox(self.content_frame, text=text.inAppText['run'], command=self.run_program, variable=self.checkbox, onvalue="True", offvalue="False",
                                font=(FONT, 15), width=400)
        self.checkbox_1.pack(pady=10)
        self.start_button = CTkButton(self.content_frame, text=text.inAppText['exit'], font=(FONT, 15), command=self.restart_program, width=400)
        self.start_button.pack(pady=(0, 20))

    def run_program(self):
        pass

    def restart_program(self):
        if self.checkbox.get() == 'True': 
            try:
                os.execv("goodbyeDPI.exe", ["goodbyeDPI.exe"])
            except Exception as ex:
                messagebox.showerror('An error just occurred', ex)
        sys.exit(0)

def get_latest_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    response = requests.get(url)
    data = response.json()
    latest_version = data["tag_name"]

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
        messagebox.showinfo('Update assistant', text.inAppText['version_error'])
    
    for name, value in options:
        if name in ['-v', '--version']:
            version = value
        elif name in ['-l', '--language']:
            lang = value
        elif name in ['-d', '--directory']:
            directory = value
        print(value)
    text.reload_text(lang)
    if version == '':
        messagebox.showinfo('Update assistant', text.inAppText['version_error'])
        version = get_latest_release()
    app = UpdaterApp(version)
    app.mainloop()