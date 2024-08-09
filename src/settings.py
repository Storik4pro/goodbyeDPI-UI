from customtkinter import *
import tkinter
from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, text

class Settings(CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry('1300x400')
        self.title(f'goodbyeDPI UI - settings')

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar()

        self.canvas = tkinter.Canvas(borderwidth=0, background="black", highlightthickness=0)
        self.frame4 = CTkFrame(self.canvas, width=700)
        self.frame4.grid(padx=0, pady=0, row=0, column=1)
        self.canvas.create_window((4, 4), window=self.frame4, anchor="nw", width=700)
        self.canvas.grid(padx=0, pady=0, row=0, column=1)
        self.frame5 = CTkFrame(self)
        self.frame5.grid(padx=50, pady=10, row=1, column=1)

        self.show_UI()
        self.show_save_dialog()

        scrollbar = CTkScrollbar(self, command=self.canvas.yview, height=600)
        scrollbar.grid(padx=0, pady=20, row=0, column=2)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=700, height=600)
        self.bind("<MouseWheel>", self.mouseWheel)

    def mouseWheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def sidebar(self):
        sidebar_frame = CTkFrame(self, width=140, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sidebar_frame.grid_rowconfigure(4, weight=1)

        label = CTkLabel(sidebar_frame, text="ПАРАМЕТРЫ", font=(FONT, 30))
        label.grid(pady=(20, 10), padx=20, row=0, column=0)

        but_1 = CTkButton(sidebar_frame, text='пользовательский интерфейс', command=self.button,
                      font=(FONT, 15), width=280)
        but_1.grid(padx=10, pady=10, row=1, column=0)

        but_2 = CTkButton(sidebar_frame, text='система', command=self.button,
                        font=(FONT, 15), width=280)
        but_2.grid(padx=10, pady=10, row=2, column=0)

        but_3 = CTkButton(sidebar_frame, text='goodbyeDPI settings', command=self.button,
                        font=(FONT, 15), width=280)
        but_3.grid(padx=10, pady=10, row=3, column=0)

        about_label = CTkLabel(sidebar_frame, text="goodbye DPI UI", anchor="w",
                                     font=(FONT, 15), width=280)
        about_label.grid(row=6, column=0, padx=20, pady=(10, 0))

        but_about = CTkButton(sidebar_frame, text='о программе ...', command=self.button,
                        font=(FONT, 15), width=280)
        but_about.grid(row=7, column=0, padx=20, pady=(10, 10))

    def show_UI(self):
        system_label = CTkLabel(self.frame4, text="ОСНОВНЫЕ", anchor="w",
                                     font=(FONT, 25), width=350)
        system_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        appearance_mode_label = CTkLabel(self.frame4, text="Тема интерфейса: ", anchor="w",
                                     font=(FONT, 20), width=300)
        appearance_mode_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        appearance_mode_optionemenu = CTkOptionMenu(self.frame4, values=["Светлая", "Тёмная"],
                                            command=self.button, width=300)
        appearance_mode_optionemenu.grid(row=1, column=1, padx=0, pady=(10, 0))

        language_label = CTkLabel(self.frame4, text="Локализация: ", anchor="w",
                                     font=(FONT, 20), width=300)
        language_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        language_optionemenu = CTkOptionMenu(self.frame4, values=["Русская", "Английская"],
                                            command=self.button, width=300)
        language_optionemenu.grid(row=2, column=1, padx=0, pady=(10, 0))

        region_label = CTkLabel(self.frame4, text="Регион: ", anchor="w",
                                     font=(FONT, 20), width=300)
        region_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        region_optionemenu = CTkOptionMenu(self.frame4, values=["Россия", "Другие"],
                                            command=self.button, width=300)
        region_optionemenu.grid(row=3, column=1, padx=0, pady=(10, 0))
        personalize_label = CTkLabel(self.frame4, text="ПЕРСОАНАЛИЗАЦИЯ", anchor="w",
                                     font=(FONT, 25), width=350)
        personalize_label.grid(row=4, column=0, padx=20, pady=(10, 0))

    def show_save_dialog(self):
        but_b = CTkButton(self.frame5, text='сохранить', command=self.button,
                      font=(FONT, 15), width=200)
        but_b.grid(padx=20, pady=(20, 20), row=0, column=0)
        but_b = CTkButton(self.frame5, text='сбросить', command=self.button,
                      font=(FONT, 15), width=200)
        but_b.grid(padx=20, pady=(20, 20), row=0, column=1)
        but_b = CTkButton(self.frame5, text='отмена', command=self.button,
                      font=(FONT, 15), width=200)
        but_b.grid(padx=20, pady=(20, 20), row=0, column=2)

    def button(self):
        pass

settings = Settings()

settings.mainloop()