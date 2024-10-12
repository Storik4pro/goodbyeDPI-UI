from customtkinter import *
from _data import FONT, DIRECTORY, text
from PIL import Image, ImageTk

class ErrorWindow(CTkToplevel):
    def __init__(self, error_type, error_address, error_category, error_details):
        super().__init__()
        window_width=800; window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.title('goodbyeDPI UI - error')
        self.minsize(window_width, window_height)
        self.after(200, lambda: self.iconbitmap(DIRECTORY+'data/error.ico'))

        self.content_frame = CTkFrame(self)
        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.header_frame = CTkFrame(self.content_frame)
        self.header_frame.pack(fill="x", pady=(10, 0), padx=10)

        self.error_icon = CTkImage(light_image=Image.open(DIRECTORY+"data/error.ico"), size=(50, 50))
        self.icon_label = CTkLabel(self.header_frame, image=self.error_icon, text="")
        self.icon_label.pack(side="left", pady=10, padx=(10, 5))

        self.header_text_frame = CTkFrame(self.header_frame, fg_color='transparent')
        self.header_text_frame.pack(fill='x', padx=(0, 5))

        self.header_text = CTkLabel(self.header_text_frame, text=text.inAppText['prog_error'], anchor="w", font=(FONT, 18, "bold"))
        self.header_text.pack(pady=(10, 0), padx=(5, 10), fill="x", expand=True)

        self.status_label = CTkLabel(self.header_text_frame, text=error_type, anchor="w", justify='left', font=(FONT, 14))
        self.status_label.pack(side="bottom",padx=(5, 10), pady=(0, 10), fill="x", expand=True)

        self.info_frame = CTkFrame(self.content_frame, fg_color="transparent")
        self.info_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.error_address_label = CTkLabel(self.info_frame, text=f"From : {error_address}", anchor="w", font=(FONT, 14))
        self.error_address_label.pack(anchor="w", pady=(0, 2), padx=0)

        self.error_category_label = CTkLabel(self.info_frame, text=f"Type : {error_category}", anchor="w", font=(FONT, 14))
        self.error_category_label.pack(anchor="w", pady=(0, 2), padx=0)

        self.error_details_label = CTkLabel(self.info_frame, text="Details: ", anchor="w", font=(FONT, 14))
        self.error_details_label.pack(anchor="w", pady=(0, 2), padx=0)

        self.details_textbox = CTkTextbox(self.info_frame, wrap="word", font=('Cascadia Mono', 12))
        self.details_textbox.pack(fill="both", expand=True, padx=0, pady=(0,10))
        self.details_textbox.insert("1.0", error_details)
        self.details_textbox.configure(state="disabled")

        self.button_frame = CTkFrame(self.info_frame, fg_color="transparent", height=40)
        self.button_frame.pack(fill="x", side='bottom', pady=(0, 0), padx=0)

        self.copy_icon = CTkImage(light_image=Image.open(DIRECTORY+"data/copy_icon.png"), size=(20, 20))
        self.copy_button = CTkButton(self.button_frame, image=self.copy_icon, width=200, text="COPY", fg_color="transparent", border_width=2, font=(FONT, 15), command=self.copy_output)
        self.copy_button.pack(side="left", padx=(0, 5), pady=(10, 0))

        self.close_button = CTkButton(self.button_frame, width=200, text="OK", font=(FONT, 15), command=self.close_window)
        self.close_button.pack(side="right", padx=(5, 0), pady=(10, 0))

    def copy_output(self):
        self.clipboard_clear()
        self.clipboard_append(self.details_textbox.get("1.0", "end-1c"))

    def close_window(self):
        self.destroy()
