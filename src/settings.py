from tkinter import messagebox
from customtkinter import *
import tkinter as ttk
from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, text

class SettingsApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("Settings")
        self.geometry("800x600")

        # Sidebar
        self.sidebar = CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.tabs = {
            "Персонализация": self.personalization_settings,
            "Система": self.system_settings,
            "goodbyeDPI": self.goodbye_dpi_settings,
            "О программе": self.about_program
        }

        self.buttons = {}
        for tab_name in self.tabs:
            button = CTkButton(self.sidebar, text=tab_name, command=lambda name=tab_name: self.switch_tab(name))
            button.pack(pady=10)
            self.buttons[tab_name] = button

        # Main content area
        self.content_frame = CTkFrame(self)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.current_tab = None
        self.switch_tab("Персонализация")

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.current_tab.pack_forget()
        self.current_tab = self.tabs[tab_name]
        self.current_tab.pack(fill="both", expand=True)

    def personalization_settings(self):
        frame = CTkFrame(self.content_frame)
        CTkLabel(frame, text="Настройки персонализации").pack(pady=20)
        # Add widgets for language, display mode, custom tkinter theme
        return frame

    def system_settings(self):
        frame = CTkFrame(self.content_frame)
        CTkLabel(frame, text="Системные настройки").pack(pady=20)
        # Add widgets for autostart, region, auto-update
        return frame

    def goodbye_dpi_settings(self):
        frame = CTkFrame(self.content_frame)
        CTkLabel(frame, text="Настройки goodbyeDPI").pack(pady=20)
        # Add widgets for goodbyeDPI settings
        return frame

    def about_program(self):
        frame = CTkFrame(self.content_frame)
        CTkLabel(frame, text="О программе").pack(pady=20)
        # Add widgets for information about goodbyedpi.exe, goodbyeDPI UI, acknowledgments
        return frame

if __name__ == "__main__":
    app = SettingsApp()
    app.mainloop()
