# Available Updates icon by Icons8
from customtkinter import *
from PIL import Image
import webbrowser

REPO_OWNER = "Storik4pro"
REPO_NAME = "goodbyeDPI-UI"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"

def open_git():
    webbrowser.open(REPO_URL)

class AboutApp(CTkToplevel):
    def __init__(self, loc, font, directory, repo_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("480x250")
        self.resizable(False, False)
        self.title(loc['about']+f" - Update assistant")
        self.after(200, lambda: self.iconbitmap(directory+'update_icon.ico'))
        self.loc = loc
        self.font = font
        self.directory = directory
        self.create_content()
        self.grab_set()

    def create_content(self):
        print(self.directory)
        self.logo = CTkImage(light_image=Image.open(self.directory+"update_icon.png"), size=(80, 80))
        self.logo_text = CTkLabel(self, image=self.logo, text="")
        self.logo_text.pack(side='left', pady=50, padx=20)

        self.info_frame = CTkFrame(self)
        self.info_frame.pack(side='left', padx=(0, 20), pady=20, fill="both", expand=True)

        self.label = CTkLabel(self.info_frame, text="UPDATE ASSISTANT", font=(self.font, 20, "bold"))
        self.label.pack(padx=20, pady=(10, 0), fill="both", expand=True)

        self.info_label = CTkLabel(self.info_frame, text=self.loc['version']+" 1.0.0 ("+self.loc['build']+" от 11.08.2024)", font=(self.font, 15))
        self.info_label.pack(padx=20, pady=0)

        github_logo = CTkImage(light_image=Image.open(self.directory+"github-mark-white.png"), size=(24, 24))

        self.github_image_button = CTkButton(self.info_frame, text=self.loc['goto_github'], font=(self.font, 15), command=open_git, width=30,height=30, image=github_logo)
        self.github_image_button.pack(side="left", padx=(10, 10), pady=10, fill="both", expand=True)