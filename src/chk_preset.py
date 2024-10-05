from ctypes import c_char_p, windll
import ctypes
from datetime import datetime
import threading
from customtkinter import *
from _data import FONT, DIRECTORY, text, settings
from utils import check_mica, open_custom_blacklist, sni_support
from PIL import Image, ImageTk
from tkinter import messagebox
import tkinter
from win32material import *
from Elements import CTkScrollableDropdown, LoadingIndicator, EntryElement, ValidateValue

mica = (settings.settings.getboolean('APPEARANCE_MODE', 'use_mica') and check_mica())
BaseWindow = tkinter.Toplevel if mica else CTkToplevel

COLOR_HOVER = '#404040' if mica else None
COLOR_FRAME = '#0f0f0f' if mica else None
ELEMENT_COLOR = '#212121' if mica else None

class ChkPresetApp(BaseWindow):
    def __init__(self, app, start_func, start_additional):
        super().__init__()
        self.app = app

        window_width = 800
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.title('goodbyeDPI UI - chkpreset [BETA]')
        self.minsize(800, 500)
        if mica:self.iconbitmap(DIRECTORY+'data/find.ico')
        else:self.after(200, lambda: self.iconbitmap(DIRECTORY+'data/find.ico'))
        if mica: self.configure(bg="black")
        self.resizable(False, False)

        self.current_frame = 0

        self.changelog_textbox = None
        self.start_func = start_func
        self.start_additional = start_additional
        self.output = None
        self.best_preset = 0
        self.stop_servise = False

        self.status_text = ""
        self.start_type = "easy"

        self.header_frame = CTkFrame(self)
        self.logo = CTkImage(light_image=Image.open(DIRECTORY + "data/find.ico"), size=(50, 50))
        self.logo_label = CTkLabel(self.header_frame, image=self.logo, text="")
        self.logo_label.pack(side="left", pady=(10, 10), padx=(10, 5))

        self.header_text_frame = CTkFrame(self.header_frame, fg_color='transparent')

        self.header_text = CTkLabel(
            self.header_text_frame,
            text=text.inAppText["header_preset_selection"],
            anchor="w",
            font=(FONT, 18, "bold")
        )
        self.header_text.pack(pady=(10, 0), padx=(5, 10), fill="x", expand=True)

        self.status_label = CTkLabel(
            self.header_text_frame,
            text=self.status_text,
            anchor="w",
            justify='left',
            font=(FONT, 14)
        )
        self.status_label.pack(side="bottom", padx=(5, 10), pady=(0, 10), fill="x", expand=True)

        self.header_text_frame.pack(fill='x', padx=(0, 10))

        self.header_frame.pack(fill="x",pady=(10, 0), padx=10)

        self.textbox_frame_height = self.winfo_height() - self.header_frame.winfo_height() - 150

        self.textbox_frame = CTkScrollableFrame(self, fg_color='transparent', height=self.textbox_frame_height)
        self.textbox_frame._scrollbar.grid_forget()

        self.output_textbox = None

        self.loading_label = CTkLabel(
            self.textbox_frame,
            text=text.inAppText["press_next_to_start"],
            anchor="w",
            justify='left',
            font=(FONT, 14)
        )
        self.loading_label.pack(side="top", fill="x", padx=10, pady=20)

        self.textbox_frame.pack(fill="x")

        self.button_frame = CTkFrame(self, fg_color='transparent')

        self.exit_button = CTkButton(
            self.button_frame,
            text=text.inAppText["close_tool"],
            fg_color="transparent",
            border_width=2,
            font=(FONT, 15),
            width=200,
            command=self.close
        )
        self.exit_button.pack(side="left", padx=(10, 5), pady=10)

        self.next_button = CTkButton(
            self.button_frame,
            text=text.inAppText["next_button"],
            font=(FONT, 15),
            width=200,
            command=self.load_content
        )
        self.next_button.pack(side="right", padx=(5, 10), pady=10)

        self.button_frame.pack(fill="x", side='bottom')

    def close(self):
        self.destroy()

    def load_content(self, page=0):
        for widget in self.textbox_frame.winfo_children():
            print(type(widget))
            widget.destroy()

        if page == 0:
            self.textbox_frame._scrollbar.configure(width=10, fg_color='transparent', bg_color='transparent')
            self.textbox_frame._scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
            self.textbox_frame._scrollbar.lift(self.textbox_frame)

            self.loading_label.destroy()
            self.status_label.configure(text="")
            self.checkbox = CTkCheckBox(
                self.textbox_frame,
                text=text.inAppText["stop_windrivert_after_each_check"],
                fg_color=ELEMENT_COLOR,
                font=(FONT, 14),
                command=self._stop_servise
            )
            self.checkbox.pack(fill="x", padx=(10, 10), pady=(20, 0))

            self.checkbox_label = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["force_stop_driver_service"],
                anchor="w",
                justify='left',
                font=(FONT, 12)
            )
            self.checkbox_label.pack(fill="x", padx=45, pady=(0, 5))

            self.separator = CTkLabel(self.textbox_frame, text="─" * 100)
            self.separator.pack(pady=(0, 0))

            self.warn = CTkImage(light_image=Image.open(DIRECTORY + "data/warning.ico"), size=(20, 20))
            self.warn_label = CTkLabel(
                self.textbox_frame,
                image=self.warn,
                text=text.inAppText["driver_restart_warning"],
                compound="left",
                wraplength=self.textbox_frame.winfo_width() - 40,
                anchor="s",
                justify="left",
                font=(FONT, 14),
                padx=10
            )
            self.warn_label.pack(pady=(0, 0), padx=(10, 5))

            self.separator = CTkLabel(self.textbox_frame, text="─" * 100)
            self.separator.pack(pady=(0, 5))

            self.label = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["check_type_label"],
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )
            self.label.pack(padx=(10, 10), pady=(0, 5), fill="x", expand=True)

            values = [
                "1. "+text.inAppText["quick_check_option"],
                "2. "+text.inAppText["slow_check_option"]
            ]
            self.combobox = CTkOptionMenu(
                self.textbox_frame,
                font=(FONT, 15),
                fg_color=ELEMENT_COLOR,
                button_color=ELEMENT_COLOR,
                bg_color="transparent",
                hover=False,
                button_hover_color=COLOR_HOVER,
                values=values,
                width=200,
                corner_radius=5,
                dynamic_resizing=False
            )
            self.combobox.pack(fill="x", padx=(10, 10), pady=(0, 10))
            CTkScrollableDropdown(
                self.combobox,
                values=values,
                width=self.textbox_frame.winfo_width() - 20,
                justify="left",
                button_color="transparent",
                hover_color="#404040",
                alpha=0.89,
                button_height=35,
                frame_border_width=0,
                frame_corner_radius=5,
                scrollbar=False,
                command=self.combobox_callback
            )

            self.label = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["site_list_label"],
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )
            self.label.pack(padx=(10, 10), pady=(0, 5), fill="x", expand=True)

            self.button = CTkButton(
                self.textbox_frame,
                text=text.inAppText["change_site_list_button"],
                font=(FONT, 15),
                fg_color=COLOR_FRAME,
                hover_color=COLOR_HOVER,
                command=self.open_blacklist
            )
            self.button.pack(padx=(10, 10), pady=(0, 5), fill="x", expand=True)

            self.label2 = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["max_wait_time_label"],
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )
            self.label2.pack(padx=(10, 10), pady=(0, 5), fill="x", expand=True)

            self.entry = EntryElement(
                self.textbox_frame,
                placeholder_text=text.inAppText["digital_value_placeholder"],
                label_element=self.label2,
                width="x",
                validate_function=ValidateValue(100000, 1, 7000),
                padx=10,
                pady=(0, 5),
                window=self
            )

            self.label3 = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["hex_value_label"],
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )

            self.entry3 = EntryElement(
                self.textbox_frame,
                placeholder_text=text.inAppText["hex_value_placeholder"],
                label_element=self.label3,
                width="x",
                value="1603030135010001310303424143facf5c983ac8ff20b819cfd634cbf5143c0005b2b8b142a6cd335012c220008969b6b387683dedb4114d466ca90be3212b2bde0c4f56261a9801",
                padx=10,
                pady=(0, 5)
            )

            self.label4 = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["sni_value_label"] + " " +(text.inAppText["sni_value_label_not_support"] if not sni_support() else ""),
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )

            self.entry4 = EntryElement(
                self.textbox_frame,
                placeholder_text=text.inAppText["sni_value_placeholder"],
                label_element=self.label4,
                width="x",
                value="www.google.com",
                padx=10,
                pady=(0, 5),
                state='disabled' if not sni_support() else "normal"
            )

            self.combobox_callback(self.combobox.get())

        elif page == 1:
            self.textbox_frame._scrollbar.place_forget()
            self.textbox_frame.configure(height=self.textbox_frame_height)

            self.next_button.configure(state="disabled")

            self.status_label.configure(text=text.inAppText["preparing_tool"])
            self.loading = LoadingIndicator(
                self.textbox_frame,
                bg_color="black",
                width=self.textbox_frame.winfo_width() - 20,
                fg_color="#3E8AC9"
            )

            self.label = CTkLabel(
                self.textbox_frame,
                text=text.inAppText["currently_running"],
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )
            self.label.pack(padx=(5, 10), pady=(0, 0), fill="x", expand=True)

            self.changelog_textbox = CTkTextbox(
                self.textbox_frame,
                wrap="word",
                height=self.textbox_frame_height - 50,
                corner_radius=0,
                font=('Cascadia Mono', 15)
            )
            self.changelog_textbox.pack(pady=5, padx=(5, 10), fill="both", expand=True)
            self.changelog_textbox.configure(state="disabled")

            self.add_log(text.inAppText["preparing_tool_log"])

            thread = threading.Thread(target=lambda: self.start())
            thread.start()

            self.status_label.configure(text=text.inAppText["preset_selection_in_progress"])

        elif page == 2:
            self.status_label.configure(text=text.inAppText["preset_selection_complete"])
            self.grab_release()

            best_preset_text = text.inAppText["best_preset"].format(preset=str(self.best_preset))
            self.label = CTkLabel(
                self.textbox_frame,
                text=best_preset_text,
                anchor="w",
                justify='left',
                font=(FONT, 14)
            )
            self.label.pack(padx=(5, 10), pady=(0, 5), fill="x", expand=True)

            self.changelog_textbox = CTkTextbox(
                self.textbox_frame,
                wrap="word",
                height=self.textbox_frame.winfo_height(),
                corner_radius=0,
                font=('Cascadia Mono', 15)
            )
            self.changelog_textbox.pack(pady=5, padx=(5, 10), fill="both", expand=True)

            print(self.output)
            self.changelog_textbox.insert("0.0", self.output)
            self.changelog_textbox.configure(state="disabled")
            self.next_button.destroy()

        self.next_button.configure(command=lambda: self.load_content(page + 1), text=text.inAppText["next_button"])

    def open_blacklist(self):
        open_custom_blacklist()

    def _stop_servise(self):
        print(self.checkbox.get())
        self.stop_servise = self.checkbox.getboolean(self.checkbox.get())
        print(self.stop_servise)

    def start(self):
        self.app._set_focus()
        self.grab_set()

        if "1. " in self.combobox.get():
            self.start_func(self.add_log, self.entry.get(), self.stop_servise)
            self.start_type = "easy"
        else:
            self.start_additional(self.add_log, self.entry.get(), self.entry3.get(), self.entry4.get(), self.stop_servise)
            self.start_type = "hard"

    def parse_textbox_content(self):
        text_content = self.changelog_textbox.get("1.0", "end").strip()
        best_preset = None
        error_presets = []
        available_presets = []

        lines = text_content.splitlines()
        for line in lines:
            l = line.split("]")[1]
            if "[ERROR_CNNALL]" in l:
                best_preset = None

            elif "[INFO_CNNBST" in l:
                best_preset = line[line.find("T") + 1:line.rindex("]")]

            elif "[INFO_STBST" in l:
                best_preset = line.split("'")[1]

            elif "[ERROR_ST" in l:
                preset = line.split("'")[1]
                error_presets.append(preset)

            elif "[INFO_ST" in l:
                preset = line.split("'")[1]
                available_presets.append(preset)

            elif "[ERROR_CNN" in l:
                preset = line[line.find("CNN") + 3:line.rindex("]")]
                error_presets.append(preset)

            elif "[INFO_CNN" in l:

                preset = line[line.find("[INFO_CNN") + 9:line.rindex("]")]
                available_presets.append(preset)

        return error_presets, available_presets, best_preset

    def generate_output(self, error_presets, available_presets, best_preset):
        output_lines = []

        preset_text = text.inAppText["_preset"] if self.start_type == 'easy' else text.inAppText["strategy"]

        for preset in error_presets:
            output_lines.append(f"{preset_text} {preset} - {text.inAppText['not_available']}.")

        for preset in available_presets:
            output_lines.append(f"{preset_text} {preset} - {text.inAppText['available']}.")

        if best_preset:
            output_lines.append(
                f"===========\n" +
                text.inAppText["recommended_preset"].format(preset_text=preset_text.lower(), preset=best_preset)
            )
        else:
            output_lines.append(text.inAppText["no_suitable_parameters"])

        return "\n".join(output_lines)

    def add_log(self, log_text):

        if "[CRITICAL_ERROR]" in log_text:
            self.next_button.configure(
                state="normal",
                text=text.inAppText["retry_button"],
                command=lambda: self.load_content(0)
            )
            self.status_label.configure(text=text.inAppText["preset_selection_failed"])
            self.loading.canvas.destroy()

        if "[END]" in log_text:
            self.next_button.configure(state="normal")
            self.status_label.configure(text=text.inAppText["preset_selection_completed"])
            self.loading.canvas.destroy()

            error_presets, available_presets, self.best_preset = self.parse_textbox_content()
            self.output = self.generate_output(error_presets, available_presets, self.best_preset)

        if self.changelog_textbox:
            current_time = datetime.now().strftime('%H:%M:%S')
            self.changelog_textbox.configure(state="normal")
            self.changelog_textbox.insert("end", f"\n[{current_time}] {log_text}")
            self.changelog_textbox.see("end")
            self.changelog_textbox.configure(state="disabled")

    def combobox_callback(self, selection):
        print(selection)
        if text.inAppText["slow_check_option"] in selection:
            self.label3.pack(padx=(10, 10), pady=(0, 5), fill="x", expand=True)
            self.entry3.pack(padx=(10, 10), pady=(0, 5), fill_mode="x")
            self.label4.pack(padx=(10, 10), pady=(0, 5), fill="x", expand=True)
            self.entry4.pack(padx=(10, 10), pady=(0, 5), fill_mode="x")
        else:
            self.label3.pack_forget()
            self.entry3.pack_forget()
            self.label4.pack_forget()
            self.entry4.pack_forget()
