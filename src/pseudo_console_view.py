from customtkinter import *
from _data import FONT, DIRECTORY, GOODBYE_DPI_EXECUTABLE, ZAPRET_EXECUTABLE, text, settings
from utils import stop_servise
from PIL import Image, ImageTk
from tkinter import messagebox

class GoodbyedpiApp(CTkToplevel):
    def __init__(self, stop_func=None, start_func=None):
        super().__init__()
        window_width=800; window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.title(f'goodbyeDPI UI - pseudo console')
        self.minsize(800, 500)
        self.after(200, lambda: self.iconbitmap(DIRECTORY+'data/find.ico'))

        self.stop = False
        self.stop_func = stop_func
        self.start_func = start_func

        self.execut = GOODBYE_DPI_EXECUTABLE if settings.settings["GLOBAL"]["engine"] == 'goodbyeDPI' else ZAPRET_EXECUTABLE

        self.gif = Image.open(DIRECTORY+'data/find.gif')
        self.frames = []

        try:
            while True:
                self.frames.append(ImageTk.PhotoImage(self.gif.copy()))
                self.gif.seek(len(self.frames))
        except EOFError:
            pass

        self.current_frame = 0
        

        self.content_frame = CTkFrame(self, width=400)
        self.status_text = text.inAppText['pseudoconsole_find']

        self.header_frame = CTkFrame(self.content_frame)
        self.logo = CTkImage(light_image=Image.open(DIRECTORY+"data/find.ico"), size=(50, 50))
        self.logo_label = CTkLabel(self.header_frame, image=self.logo, text="")
        self.logo_label.pack(side="left", pady=10, padx=(10, 5))

        self.header_text_frame = CTkFrame(self.header_frame, fg_color='transparent')
        

        self.header_text = CTkLabel(self.header_text_frame, text=text.inAppText['pseudoconsole_title'].format(executable=self.execut), anchor="w", font=(FONT, 18, "bold"))
        self.header_text.pack(pady=(10, 0), padx=(5, 10), fill="x", expand=True)

        self.status_label = CTkLabel(self.header_text_frame, text=self.status_text, anchor="w", justify='left', font=(FONT, 14))
        self.status_label.pack(side="bottom",padx=(5, 10), pady=(0, 10), fill="x", expand=True)

        self.header_text_frame.pack(fill='x')
        
        self.header_frame.pack(fill="x",pady=(10, 0), padx=10)

        self.textbox_frame = CTkFrame(self.content_frame, fg_color='transparent')

        self.output_textbox=None

        self.loading_label = CTkLabel(self.textbox_frame, text='')
        self.loading_label.pack(fill="both", expand=True)

        self.textbox_frame.pack(fill="both", expand=True)

        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.button_frame = CTkFrame(self.content_frame, fg_color='transparent')

        self.copy_icon = CTkImage(light_image=Image.open(DIRECTORY+"data/copy_icon.png"), size=(20, 20))
        self.copy_button = CTkButton(self.button_frame, image=self.copy_icon, text=text.inAppText['pseudoconsole_copy'],fg_color="transparent",border_width=2, font=(FONT, 15), width=200, state='disabled', command=self.copy_output)
        self.copy_button.pack(side="left", padx=(10, 5),pady=10)

        self.stop_button = CTkButton(self.button_frame, text=text.inAppText['pseudoconsole_stop'], font=(FONT, 15), width=200, command=self.stop_service)
        self.stop_button.pack(side="right", padx=(5, 10),pady=10)

        self.restart_button = CTkButton(self.button_frame, text=text.inAppText['pseudoconsole_restart'], font=(FONT, 15), width=200, state='disabled', command=self.restart_service)
        self.restart_button.pack(side="right", padx=(5, 10),pady=10)

        self.button_frame.pack(fill="x", side='bottom')

        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.after(0, self.update_frame)

    def update_frame(self):
        try:
            frame = self.frames[self.current_frame]
            self.loading_label.configure(image=frame)
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(200, self.update_frame)
        except:pass

    def enable_copy(self, event):
        self.output_textbox.configure(state="normal")
        self.output_textbox.after(100, lambda: self.output_textbox.configure(state="disabled"))

    def clear_output(self):
        if self.output_textbox:
            self.output_textbox.configure(state="normal")
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.configure(state="disabled")

    def add_output(self, output):
        if self.output_textbox is None and output != '':
            for widget in self.textbox_frame.winfo_children():
                widget.destroy()
            self.output_textbox = CTkTextbox(self.textbox_frame, wrap="word", width=700, height=250, font=('Cascadia Mono', 15))
            self.output_textbox.pack(pady=10, padx=10, fill="both", expand=True)
            self.output_textbox.insert("1.0", f'[DEBUG] Connecting to {self.execut} ...\n\n')
            self.output_textbox.bind("<Control-c>", self.enable_copy)
            self.output_textbox.configure(state="disabled")
            self.restart_button.configure(state='normal')
            self.copy_button.configure(state='normal')
        elif self.output_textbox is None and output == '':
            return
            
        output = str(output if type(output)==str else ''.join(output))
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert(END, output)
        self.output_textbox.configure(state="disabled")
        
        self.output_textbox.see(END)
        
        if "Filter activated" in output or "[PROXY] created a listener on port" in output:
            self.update_status(text.inAppText['pseudoconsole_success'].format(executable=self.execut))
            self.logo.configure(light_image=Image.open(DIRECTORY+"data/find.ico"))

        if "Error opening filter" in output or "unknown option" in output or "[PROXY] error creating listener:" in output:
            self.update_status(text.inAppText['pseudoconsole_error'].format(executable=self.execut))
            self.logo.configure(light_image=Image.open(DIRECTORY+"data/error.ico"))
            if self.stop_func: 
                self.stop_func(notf=False)

        elif f"[DEBUG] The {self.execut} process has been terminated by user" in output:
            self.update_status(text.inAppText['pseudoconsole_user_stop'].format(executable=self.execut))

        elif f"[DEBUG] The {self.execut} process has been terminated for unknown reason" in output:
            self.logo.configure(light_image=Image.open(DIRECTORY+"data/error.ico"))
            self.update_status(text.inAppText['pseudoconsole_uncn_stop'].format(executable=self.execut))
        print(self.logo._light_image)

    def update_status(self, status_text):
        self.status_label.configure(text=status_text)

    def copy_output(self):
        self.clipboard_clear()
        self.clipboard_append(self.output_textbox.get("1.0", "end-1c"))

    def connect_func(self, stop_func, start_func):
        self.stop_func = stop_func
        self.start_func = start_func

    def stop_service(self):
        result = messagebox.askyesno('GoodbyeDPI UI', text.inAppText['pseudoconsole_question'], parent=self)
        if result:
            self.add_output("\n[DEBUG] Initializing process stop\n")
            _q = True
            if self.stop_func:
                _q = self.stop_func()
            if _q:
                self.add_output("\n[DEBUG] Initializing windrivert.dll stop\n")
                stop_servise()
            else:
                self.add_output("\n[DEBUG] Error while initializing windrivert.dll stop\n")

    def restart_service(self):
        self.add_output("\n[DEBUG] Initializing process restart\n")
        if self.stop_func and self.start_func:
            self.stop_func()
            self.clear_output()
            self.add_output("[DEBUG] Initializing process start ...\n")
            self.start_func()
        

