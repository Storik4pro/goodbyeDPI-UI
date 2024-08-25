import ctypes
from tkinter import messagebox
import typing
from customtkinter import *
import tkinter as ttk

from customtkinter import CTkCanvas, CTkFrame
from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, text
from PIL import Image, ImageTk, ImageDraw
from ctypes import windll, c_char_p
from win32material import *
from Elements import CTkScrollableDropdown


ELEMENT_HEIGHT = 60
ELEMENT_WIDTH = 700

COLOR_HOVER = '#404040'
COLOR_FRAME = '#0f0f0f'
ELEMENT_COLOR = '#212121'

FONT_BOLD = 'Nunito ExtraBold'

def canvas_transparent(w):
    colorkey = 0x00030201
    hwnd = w.winfo_id()
    
    wnd_exstyle = windll.user32.GetWindowLongA(hwnd, -20)  # GWL_EXSTYLE
    new_exstyle = wnd_exstyle | 0x00080000  # WS_EX_LAYERED
    windll.user32.SetWindowLongA(hwnd, -20, new_exstyle)  # GWL_EXSTYLE
    windll.user32.SetLayeredWindowAttributes(hwnd, colorkey, 255, 0x00000001) 

class ValidateValue:
    def __init__(self, maxvalue, minvalue, valid_value=1) -> None:
        self.maxvalue = maxvalue
        self.minvalue = minvalue
        self.int_validate = True
        self.last_valid_value = valid_value
        if minvalue == 0 and maxvalue == 0:
            self.int_validate = False

    def validate(self, entry_var:Variable, entry, label_info:CTkLabel=None, valid_value=1):
        
        value = entry_var.get()
        if value.isdigit():
            num_value = int(value)
            if self.int_validate:
                if self.minvalue <= num_value <= self.maxvalue:
                    self.last_valid_value = value
                    entry.normal()
                    if label_info: label_info.configure(text_color="#FFFFFF")
                else:
                    entry_var.set(self.last_valid_value)
                    entry.red() 
                    if label_info: label_info.configure(text_color="red")
            else:
                self.last_valid_value = value
                entry.normal()
                if label_info: label_info.configure(text_color="#FFFFFF")
        elif value == '':
            pass
        else:
            if not self.last_valid_value in entry_var.get():
               entry_var.set("") 
            else:
                entry_var.set(self.last_valid_value)
            entry.red() 
            if label_info: label_info.configure(text_color="red")

class ValidateIntCol:
    def __init__(self, lenght, valid_value=1) -> None:
        self.lenght = lenght

    def validate(self, entry_var:Variable, entry, label_info:CTkLabel=None, valid_value=1):
        value = entry_var.get()
        if value.isdigit():
            if len(value) <= self.lenght:
                self.last_valid_value = value
                entry.normal()
            else:
                entry_var.set(self.last_valid_value)
                entry.red() 
        elif value == '':
            pass
        else:
            if not self.last_valid_value in entry_var.get():
               entry_var.set("") 
            else:
                entry_var.set(self.last_valid_value)
            entry.red() 
    

class BaseElement:
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0) -> None:
        self.frame = CTkFrame(parent, width=ELEMENT_WIDTH, height=ELEMENT_HEIGHT+2, fg_color=COLOR_FRAME)
        self.frame.grid_propagate(False)
        self.frame.grid(row=row, column=column, pady=2, padx=0)
        self.call = False 

    def disable(self):
        self.frame.configure(fg_color="#454545")

        for widget in self.frame.winfo_children():
            if type(widget) == CTkFrame:
                for _widget in widget.winfo_children():
                    try:
                        _widget.configure(text_color="#5D6B73")
                    except:pass
            if type(widget) == CTkLabel:
                widget.configure(text_color="#5D6B73")
            try:
                widget.configure(state="disabled")
            except:
                pass

    def enable(self):
        self.frame.configure(fg_color=COLOR_FRAME)

        for widget in self.frame.winfo_children():
            if type(widget) == CTkFrame:
                for _widget in widget.winfo_children():
                    try:
                        _widget.configure(text_color="#FFFFFF")
                    except:pass
            if type(widget) == CTkLabel:
                widget.configure(text_color="#FFFFFF")
            try:
                widget.configure(state="normal")
            except:
                pass

class EntryElement:
    def __init__(self, parent:CTkFrame|CTkCanvas, placeholder_text:str, label_element:CTkLabel=None, validate_function=None, width=240, window:CTk=None) -> None:
        self.label_info = label_element
        self.entry_var = StringVar(value="1")

        self.last_valid_value = self.entry_var.get()
        try:
            self.entry_var.trace_add("write", lambda *args :validate_function.validate(self.entry_var, self, label_element, self.last_valid_value))
        except Exception as ex:
            print(ex)
        self.entry = CTkEntry(master=parent, placeholder_text=placeholder_text, textvariable=self.entry_var, width=width, border_width=2, border_color=COLOR_FRAME)
        self.entry.grid(row=0, column=1, padx=(0, 0), pady=0)
        
        
        if window: window.bind_all("<Button-1>", lambda *args :validate_function.validate(self.entry_var, self, label_element, self.last_valid_value), add="+")
    
    def get(self):
        return self.entry.get()
    
    def red(self):
        self.entry.configure(border_color="red")

    def normal(self, valid_value=None):
        self.entry.configure(border_color=COLOR_FRAME)
        if valid_value: self.last_valid_value = valid_value

    def validate_input(self, *args):
        print(*args)
        value = self.entry_var.get()

        if value.isdigit():
            num_value = int(value)
            self.last_valid_value = value
            self.entry.configure(border_color=COLOR_FRAME)
            if self.label_info: self.label_info.configure(text_color="#FFFFFF")
        else:
            self.entry.configure(border_color="red") 
            if self.label_info: self.label_info.configure(text_color="red")
    
    def on_click(self, event):
        current_value = self.entry_var.get()

        if self.entry.cget("border_color") == "red":
            self.entry_var.set(self.last_valid_value)
            self.entry.configure(border_color=COLOR_FRAME)

class Switch(BaseElement):
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0, label='Sample label', subLabel:str=None, command=None,var:Variable=None, onvalue='On', offvalue='Off') -> None:
        super().__init__(parent, row=row, column=column)
        self.var = var if var else StringVar(value='Off')
        self.command = command
        self.onvalue = onvalue

        self.label_frame = CTkFrame(self.frame, width=570, height=ELEMENT_HEIGHT, fg_color="transparent")
        self.label_frame.grid_propagate(False)
        self.label_frame.grid(row=0, column=0, pady=0, padx=(20, 0))
        height = ELEMENT_HEIGHT//2 if subLabel else ELEMENT_HEIGHT

        self.label = CTkLabel(self.label_frame, text=label, font=(FONT, 15), height=height, width=570, fg_color="transparent", anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 0), pady=0)

        if subLabel:
            self.label_info = CTkLabel(self.label_frame, text=subLabel, font=(FONT, 12), height=height, width=570, fg_color="transparent", anchor="w")
            self.label_info.grid(row=1, column=0, padx=(0, 0), pady=0)

        self.stateLabel = CTkLabel(self.frame, text=self.var.get(), font=(FONT, 15), height=ELEMENT_HEIGHT, width=40, fg_color="transparent", anchor="w")
        self.stateLabel.grid(row=0, column=1, padx=(15, 0), pady=0)
    
        switch = CTkSwitch(self.frame, text='', variable=self.var, onvalue="On", offvalue="Off", width=40, fg_color="#1C1C1C", command=self.toggle, corner_radius=10)  # Закругленные углы
        switch.grid(row=0, column=2, padx=(0,19))

        try:
            self.command(self.var.get(), self)
        except:pass

    def toggle(self):
        self.stateLabel.configure(text=self.var.get())
        if self.command: 
            self.call = True
            if self.var.get() == self.onvalue: value='On'
            else: value='Off'
            self.command(value, self)
            self.call = False

class Combobox(BaseElement):
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0, label='Sample label', values=['sample value', 'sample value'], subLabel=None, function=None) -> None:
        super().__init__(parent, row=row, column=column)

        self.label_frame = CTkFrame(self.frame, width=420, height=ELEMENT_HEIGHT, fg_color="transparent")
        self.label_frame.grid_propagate(False)
        self.label_frame.grid(row=0, column=0, pady=0, padx=(20, 0))
        height = ELEMENT_HEIGHT//2 if subLabel else ELEMENT_HEIGHT

        self.label = CTkLabel(self.label_frame, text=label, font=(FONT, 15), height=height, width=570, fg_color="transparent", anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 0), pady=0)

        if subLabel:
            self.label_info = CTkLabel(self.label_frame, text=subLabel, font=(FONT, 12), height=height, width=570, fg_color="transparent", anchor="w")
            self.label_info.grid(row=1, column=0, padx=(0, 0), pady=0)

        self.combobox = CTkOptionMenu(self.frame, font=(FONT, 15),fg_color=ELEMENT_COLOR, button_color=ELEMENT_COLOR, hover=True, button_hover_color=COLOR_HOVER, values=values, width=240, corner_radius=5, dynamic_resizing=False, command=function)
        self.combobox.grid(row=0, column=1, padx=(0, 20))

        CTkScrollableDropdown(self.combobox, values=values, justify="left", button_color="transparent", hover_color="#404040", alpha=0.89, button_height=35, frame_border_width=0, frame_corner_radius=5, scrollbar=False)



class Button:
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample label', function=None, state='normal') -> None:
        self.button = CTkButton(parent, text=label, font=(FONT, 15), fg_color=COLOR_FRAME, hover_color=COLOR_HOVER, command=function, state=state)
        self.button.grid(row=row, column=column, sticky='w', pady=5)

    def disable(self):
        self.button.configure(state='disable')
    def enable(self):
        self.button.configure(state='normal')

class FrameButton(BaseElement):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample text', subLabel=None, func=None, window:CTk|ttk.Tk=None) -> None:
        super().__init__(parent, row, column)

        self.func = func
        self.window = window
        self.frame.configure(fg_color=COLOR_FRAME)

        self.label_frame = CTkFrame(self.frame, width=540, height=ELEMENT_HEIGHT, fg_color="transparent")
        self.label_frame.grid_propagate(False)
        self.label_frame.grid(row=0, column=0, pady=(0, 1), padx=(20, 0))

        height = ELEMENT_HEIGHT//2 if subLabel else ELEMENT_HEIGHT

        self.label = CTkLabel(self.label_frame, text=label, font=(FONT, 15), height=height, width=570, fg_color="transparent", anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 0), pady=0)

        if subLabel:
            self.label_info = CTkLabel(self.label_frame, text=subLabel, font=(FONT, 12), height=height, width=570, fg_color="transparent", anchor="w")
            self.label_info.grid(row=1, column=0, padx=(0, 0), pady=0)

        img = CTkImage(light_image=Image.open(DIRECTORY+"data/arrow-light.png"), dark_image=Image.open(DIRECTORY+"data/arrow-dark.png"), size=(20, 20))
        self.img_label = CTkLabel(self.frame, text='', width=20, height=20, compound = "right", anchor='s', image=img)
        self.img_label.grid(row=0, column=1, padx=(100, 0))

        self.bind_all_widgets(self.frame)

        self.bind_execute(self.frame)

        self.enter = False

    def bind_execute(self, widget):
        widget.bind("<Button-1>", self.execute_function)

        for child in widget.winfo_children():
            self.bind_execute(child)

    def bind_all_widgets(self, widget):
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)

        # Рекурсивно привязываем события ко всем дочерним виджетам
        for child in widget.winfo_children():
            self.bind_all_widgets(child)

    def on_enter(self, event):
        self.enter = True
        if self.window: self.window.after(2, self._hover)
        else: self._hover()         

    def on_leave(self, event):
        self.enter = False
        if self.window: self.window.after(2, self._normal)
        else: self._normal()

    def _hover(self):
        if self.enter:
            self.frame.configure(fg_color=COLOR_HOVER)
    
    def _normal(self):
        if not self.enter:
            self.frame.configure(fg_color=COLOR_FRAME)

    def execute_function(self, event):
        print("function executed")
        if self.func: self.func()

class ComboboxButton(FrameButton):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample text', subLabel=None, func=None, window:CTk|ttk.Tk=None, values=['Samle value', ], function=None) -> None:
        super().__init__(parent, row, column, label, subLabel, func, window)

        self.img_label.grid_forget()
        self.img_label.configure(width=20)

        self.label_frame.grid_forget()
        
        self.label_frame.configure(width=420)
        self.label_frame.grid_propagate(False)
        self.label_frame.grid(row=0, column=0, pady=0, padx=(20, 0))


        self.combobox = CTkOptionMenu(self.frame, font=(FONT, 15),fg_color=ELEMENT_COLOR, button_color=ELEMENT_COLOR, bg_color="transparent", hover=False, button_hover_color=COLOR_HOVER, values=values, width=200, corner_radius=5, dynamic_resizing=False, command=function)
        self.combobox.grid(row=0, column=1, pady=1, padx=(0, 20))
        CTkScrollableDropdown(self.combobox, values=values, justify="left", button_color="transparent", hover_color="#404040", alpha=0.89, button_height=35, frame_border_width=0, frame_corner_radius=5, scrollbar=False)

        self.img_label.grid(row=0, column=2, padx=(0,20))

        self.bind_all_widgets(self.frame)

class SwitchButton(FrameButton):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample text', subLabel=None, func=None, switch_command=None, var:Variable=None) -> None:
        super().__init__(parent, row, column, label, subLabel, func)
        self.command = switch_command
        self.var = var if var else StringVar(value='Off')

        self.img_label.grid_forget()
        self.img_label.configure(width=20)

        self.stateLabel = CTkLabel(self.frame, text=self.var.get(), font=(FONT, 15), height=ELEMENT_HEIGHT, width=40, fg_color="transparent", anchor="w")
        self.stateLabel.grid(row=0, column=1, padx=(15, 0), pady=0)
        
        switch = CTkSwitch(self.frame, text='', variable=self.var, onvalue='On', offvalue='Off', width=40, fg_color="#1C1C1C", command=self.toggle, corner_radius=10)  # Закругленные углы
        switch.grid(row=0, column=2, padx=(0,0))

        self.img_label.grid(row=0, column=3, padx=(0,20))

        self.bind_all_widgets(self.frame)

    def toggle(self):
        self.stateLabel.configure(text=self.var.get())
        if self.command: self.command(self.var.get())

class Entry(BaseElement):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample label', subLabel=None, window:CTk = None, validate:ValidateValue=None) -> None:
        super().__init__(parent, row, column)

        self.label_frame = CTkFrame(self.frame, width=420, height=ELEMENT_HEIGHT, fg_color="transparent")
        self.label_frame.grid_propagate(False)
        self.label_frame.grid(row=0, column=0, pady=0, padx=(20, 0))

        height = ELEMENT_HEIGHT//2 if subLabel else ELEMENT_HEIGHT

        self.label = CTkLabel(self.label_frame, text=label, font=(FONT, 15), height=height, width=570, fg_color="transparent", anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 0), pady=0)

        self.label_info = None

        if subLabel:
            self.label_info = CTkLabel(self.label_frame, text=subLabel, font=(FONT, 12), height=height, width=570, fg_color="transparent", anchor="w")
            self.label_info.grid(row=1, column=0, padx=(0, 0), pady=0)

        validate_value=ValidateValue(50, 1) if validate is None else validate

        self.entry = EntryElement(self.frame, placeholder_text="Значение от 1 до 50", label_element=self.label_info if subLabel else None, validate_function=validate_value, window=window)

        self.last_valid_value = self.entry.get()  # Переменная для хранения последнего правильного значения

    def validate_input(self, *args):
        value = self.entry.get()

        if value.isdigit():
            num_value = int(value)
            if 1 <= num_value <= 50:
                self.last_valid_value = value
                self.entry.normal(self.last_valid_value)
                if self.label_info: self.label_info.configure(text_color="#FFFFFF")
            else:
                self.entry.red()
                if self.label_info: self.label_info.configure(text_color="red")
        else:
            self.entry.red()
            if self.label_info: self.label_info.configure(text_color="red")
        

class Label:
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0, label='Sample label', font=(FONT_BOLD, 25), pady=(0, 20)) -> None:
        label = CTkLabel(parent, text=label, font=font, width=700, anchor='w', fg_color="transparent")
        label.grid(row=row, column=column, padx=0, pady=pady)
        self.call=False

    def disable(self):pass
    def enable(self):pass

class SubLabel(Label):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample label') -> None:
        font=(FONT, 20)
        super().__init__(parent, row, column, label, font, (0, 2))

class TooltipLabel(Label):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample label') -> None:
        font=(FONT, 14)
        super().__init__(parent, row, column, label, font, 2)
        
class Checkbox(BaseElement):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample Label', element:CTkEntry|CTkOptionMenu|CTkButton=None, args:tuple=None, func=None) -> None:
        super().__init__(parent, row, column)

        self.variable = StringVar(value='On')

        self.checkbox = CTkCheckBox(self.frame, width=420, height=ELEMENT_HEIGHT, text=label, variable=self.variable, onvalue='On', offvalue='Off', font=(FONT, 15), command=self.toggle)
        self.checkbox.grid(row=0, column=0, padx=(20, 0))
        if element == CTkOptionMenu:
            _q = args
            print(_q)
            self.element = element(self.frame, width=240, font=(FONT, 15), command=func, values=args)
            self.element.grid(row=0, column=1, padx=(0, 20))
        elif element == CTkEntry:
            self.entry = CTkEntry(textvariable=self.entry_var)
            self.element = element(self.frame, width=240, font=(FONT, 15), command=func,border_width=2, border_color=COLOR_FRAME, placeholder_text=args[0], values=args)
            self.element.grid(row=0, column=1, padx=(0, 20))
        elif element == CTkButton:
            self.element = element(self.frame, text=args, width=240, font=(FONT, 15), command=func, fg_color=ELEMENT_COLOR, hover_color=COLOR_HOVER, corner_radius=5)
            self.element.grid(row=0, column=1, padx=(0, 20))
        else:
            self.element = None
    
    def toggle(self):
        if self.variable.get() == 'On':
            if self.element: self.element.configure(state='normal')
        else:
            if self.element: self.element.configure(state='disabled')

class Content:
    def __init__(self, parent:CTkFrame|CTkCanvas, content:typing.Dict[Switch|Label|Combobox|BaseElement, tuple], disabled_func=None) -> None:
        row = 0
        column = 0
        self.content = []
        _q=False
        dis_check = 0
        for key, (cls, args) in content.items():
            args = list(args)
            if disabled_func:
                for i, word in enumerate(args):
                    if 'disabled' == word:
                        args[i] = self.disabled
            instance = cls(parent, row, column, *args)
            if not _q:self.content.append(instance)
            row += 1
            _q=False

    def disabled(self, value:str, call_element):
        _q = False
        if value=='Off':
            for i, content in enumerate(self.content):
                if content == call_element or (type(content)==type(call_element) and i>2):
                    if not _q: _q = True
                    else: 
                        _q = False
                        return
                    continue
                if _q: content.disable()
        else: 
            for i, content in enumerate(self.content):
                if content == call_element or (type(content)==type(call_element) and i>2):
                    if not _q: _q = True
                    else:
                        _q = False
                        return
                    continue
                if _q:content.enable()
                
class SettingsApp(ttk.Tk):
    def __init__(self):
        super().__init__()
        self.scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.title("Настройки")
        self.geometry(f"{int(1100*self.scaleFactor)}x600")
        self.configure(bg="black")
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.accent_color = "#00A4EF"
        self.text_color = "#FFFFFF"
        self.hover_color = COLOR_HOVER
        self.grid_color = "#010203"
        self.selected_button = None

        self.init_sidebar()

        self.init_content()

    def init_sidebar(self):
        sidebar_frame = CTkFrame(self, width=200, fg_color="transparent")
        sidebar_frame.grid(row=0, column=0, pady=30,rowspan=4, sticky="nsew")
        sidebar_frame.grid_rowconfigure(4, weight=1)

        buttons = [
            ("Персонализация", DIRECTORY+"data/find.ico"),
            ("Система", DIRECTORY+"data/find.ico"),
            ("goodbyeDPI", DIRECTORY+"data/find.ico"),
            ("О программе", DIRECTORY+"data/find.ico")
        ]

        self.sidebar_buttons = {}

        for i, butn in enumerate(buttons):
            icon = Image.open(butn[1])
            icon = icon.resize((20, 20))
            icon = ImageTk.PhotoImage(icon)

            button_frame = CTkFrame(sidebar_frame, height=40, width=250, fg_color="transparent")
            button_frame.grid_propagate(False)
            button_frame.grid(row=i, column=0, pady=0, padx=(20, 0))
            button_frame.grid_columnconfigure((0, 1, 2), weight=1)
            button_frame.grid_rowconfigure((0, 1), weight=1)

            accent_line = CTkFrame(button_frame, width=5, height=15, fg_color=self.accent_color)
            accent_line.grid(row=0, column=0, padx=(5, 0))
            accent_line.grid_forget()

            button = CTkButton(
                button_frame, 
                text=butn[0], 
                image=icon, 
                font=(FONT, 15),
                compound="left", 
                fg_color="transparent", 
                hover_color=self.hover_color,
                anchor="w",
                height=35,
                width= 250,
                corner_radius=10,  # Закругленные углы
                command=lambda name=butn[0]: self.switch_tab(name)
            )
            button.grid(padx=0, pady=1, row=1, column=2)

            self.sidebar_buttons[butn[0]] = (button, accent_line)

    def init_content(self):
        self.tab_frames = {}

        # Вкладка Персонализация
        personalization_tab = self.create_tab()
        self.tab_frames["Персонализация"] = personalization_tab

        Content(
            personalization_tab,
            {
                "Label1": (Label, ("Персонализация",)),
                "Combobox1": (Combobox, ("Язык", ["Русский", "Английский"])),
                "Switch1": (Switch, ("Темный режим", None, self.switch_theme)),
                "Switch2": (Combobox, ("Тема customtkinter", ["blue", "dark blue", "green"], self.theme_change)),
            }
        )

        # Вкладка Система
        system_tab = self.create_tab()
        self.tab_frames["Система"] = system_tab

        Content(
            system_tab,
            {
                "Label1": (Label, ("Система",)),
                "Switch1": (Switch, ("Автозапуск",)),
                "Combobox1": (Combobox, ("Регион", ["Россия", "США", "Европа"])),
                "Switch2": (Switch, ("Автообновление",)),
            }
        )

        # Вкладка goodbyeDPI
        
        goodbyedpi_tab = self.create_tab(scroll=True)
        self.tab_frames["goodbyeDPI"] = goodbyedpi_tab
        Content(
            goodbyedpi_tab[0],
            {
                "Label1": (Label, ("Параметры goodbyeDPI",)),
                "Combobox1": (ComboboxButton, ("Пресет настроек", "Изменение готовых пресетов, Создание новых пресетов", lambda: self.switch_tab('quick'), self, ["blacklist-с изменением DNS", "blacklist", "с изменением DNS", "без параметров"], None)),
                "Switch1": (Switch, ("Блокировка пассивных DPI",)),
                "Switch2": (Switch, ("Замена заголовка Host на hoSt",)),
                "Switch3": (Switch, ("Удаление пробела между именем параметра Host и его заголовком",)),
                "Switch4": (Switch, ("Изменение регистра для значения заголовка Host", 'Например, замена test.com на tEsT.cOm',)),
                "Switch5": (Switch, ("Фрагментация HTTP",)),
                "Button1": (SwitchButton, ("Фрагментация HTTPS", "Случайное кол-во фрагментаций, Выбор фрагментации TLS", lambda: self.switch_tab('HTTPS'))),
                "Switch6": (SwitchButton, ("Фрагментация длительных (persistent, keep-alive) HTTP-соединений", "Не дожидаться первого сегмента ACK", lambda: self.switch_tab('HTTP'))),
                "Switch8": (SwitchButton, ("Находить и обрабатывать HTTP-трафик на порте, отличном от 80", "Добавление собственного TCP порта", lambda: self.switch_tab('port'))),
                "Button2": (FrameButton, ("Перенаправление DNS запросов", "Перенаправление на IP адрес, Перенаправление на IPv6 адрес", lambda: self.switch_tab('DNS'))),
                "Switch9": (SwitchButton, ("Фильтрация дополнительных IP ID подключений", "Изменение значения ID", lambda: self.switch_tab('IPID'))),
                "Button10": (FrameButton, ("Отправка фейковых HTTP/HTTPS запросов", "Ручная настройка TTL, Автоопределение TTL, отправка контрольной суммы TCP", lambda: self.switch_tab('TTL'))),
                "Switch10": (Switch, ("Отправка поддельных запросов с помощью TCP SEQ/ACK",)),
                "Button11": (FrameButton, ("Оптимизация", "Ограничение обработки пакетов TCP", lambda: self.switch_tab('TCP'))),
                "Switch11": (Switch, ("Добавление пробела между методом HTTP и URL", "Обратите внимание: данная настройка влияет на работосопобность сайтов",)),
                "Button12": (FrameButton, ("Сайты, для которых будет включен goodbyedpi", "Обновление russia_blacklist.txt, Добавление своего списка сайтов", lambda: self.switch_tab('blacklist'))),
            }
        )
        goodbyedpi_quick = self.create_tab()
        self.tab_frames["quick"] = goodbyedpi_quick

        Content(
            goodbyedpi_quick,
            {
                "Label1": (Label, ("Пресет настроек",)),
                "SubLabel1":(SubLabel, ("Средство создания пресетов", )),
                "TooltipLabel1":(TooltipLabel, ("Средство создания пресетов позволит создать ваш собственный пресет настроек",)),
                "Button1":(Button, ("Открыть средство создания пресетов",)),
            },
            True
        )

        goodbyedpi_HTTPS = self.create_tab()
        self.tab_frames["HTTPS"] = goodbyedpi_HTTPS

        Content(
            goodbyedpi_HTTPS,
            {
                "Label1": (Label, ("Фрагментация HTTPS",)),
                "Switch1": (Switch, ("Фрагментация HTTPS", None, "disabled")),
                "Entry1": (Entry, ("Значение фрагментации HTTPS", "Значение фрагментации должно быть в пределах от 1 до 50", self)),
                "Checkbox1":(Checkbox, ("Случайное значение через", CTkOptionMenu, (['5 сек.', '10 сек.']))),
                "Combobox1": (Combobox, ("Тип фрагментации", ["Нормальная фрагментация", "Обратная фрагментация"], "Выбор фрагметации TLS, если некоторые сайты не открываются")),
            },
            True
        )
        goodbyedpi_HTTP = self.create_tab()
        self.tab_frames["HTTP"] = goodbyedpi_HTTP

        Content(
            goodbyedpi_HTTP,
            {
                "Label1": (Label, ("Фрагментация длительных HTTP соединений",)),
                "Switch6": (Switch, ("Фрагментация длительных (persistent, keep-alive) HTTP-соединений", None, "disabled")),
                "Switch1": (Switch, ("Не дожидаться первого сегмента ACK", )),

            },
            True
        )

        goodbyedpi_port = self.create_tab()
        self.tab_frames["port"] = goodbyedpi_port

        Content(
            goodbyedpi_port,
            {
                "Label1": (Label, ("Обработка трафика на пользовательском порте",)),
                "Switch1": (Switch, ("Находить и обрабатывать HTTP-трафик на порте, отличном от 80", None, "disabled")),
                "Entry1": (Entry, ("Собственные TCP порты", "Добавление собственных портов для обработки goodbyedpi", self, ValidateIntCol(5))),
            },
            True
        )

        goodbyedpi_DNS = self.create_tab()
        self.tab_frames["DNS"] = goodbyedpi_DNS

        Content(
            goodbyedpi_DNS,
            {
                "Label1": (Label, ("Перенаправление DNS-запросов ",)),
                "Switch1": (Switch, ("Перенаправлять запросы DNS запросы на указанный IP", None, "disabled")),
                "Entry1": (Entry, ("IP адрес для перенаправления", None, self)),
                "Entry2": (Entry, ("Порт для перенаправления", None, self, ValidateIntCol(5))),
                "Switch2": (Switch, ("Перенаправлять IPv6 запросы DNS запросы на указанный IPv6", None, "disabled")),
                "Entry3": (Entry, ("IPv6 адрес для перенаправления", None, self)),
                "Entry4": (Entry, ("Порт для перенаправления", None, self, ValidateIntCol(5))),
            },
            True
        )
        goodbyedpi_IPID = self.create_tab()
        self.tab_frames["IPID"] = goodbyedpi_IPID

        Content(
            goodbyedpi_IPID,
            {
                "Label1": (Label, ("Фильтрация дополнительных IP ID",)),
                "Switch6": (Switch, ("Фильтрация дополнительных IP ID", None, "disabled")),
                "Entry4": (Entry, ("Значение IP ID", "Например, для дом.ру это значение равно 54321", self, ValidateIntCol(5))),

            },
            True
        )

        goodbyedpi_TTL = self.create_tab()
        self.tab_frames["TTL"] = goodbyedpi_TTL

        Content(
            goodbyedpi_TTL,
            {
                "Label1": (Label, ("Отправка фейковых HTTP/HTTPS запросов",)),
                "Switch6": (Switch, ("Отправка неверной контрольной суммы TCP", "Самый безопасный способ (рекомендуется)", "disabled", None, 'Off', 'On')),
                "Switch5": (Switch, ("Автоопределение значения TTL", None, "disabled", None, 'Off', 'On')),
                "Entry1": (Entry, ("Количество фейковых TTL запросов", "Значение должно быть в пределах от 1 до 30", self, ValidateValue(30, 1))),

            },
            True
        )

        goodbyedpi_TCP = self.create_tab()
        self.tab_frames["TCP"] = goodbyedpi_TCP

        Content(
            goodbyedpi_TCP,
            {
                "Label1": (Label, ("Оптимизация",)),
                "Switch6": (Switch, ("Ограничивать обработку TCP", None, "disabled", None)),
                "Entry1": (Entry, ("Максимальное значение для обработки", None, self, ValidateIntCol(5))),

            },
            True
        )

        goodbyedpi_blacklist = self.create_tab()
        self.tab_frames["blacklist"] = goodbyedpi_blacklist

        Content(
            goodbyedpi_blacklist,
            {
                "Label1": (Label, ("Сайты, для которых необходимо включить goodbyedpi",)),
                "Switch6": (Switch, ("Активировать для всех сайтов", None, "disabled", None, 'Off', 'On')),
                "Checkbox1":(Checkbox, ("Активировать для сайтов из russia_blacklist.txt", CTkButton, ('Обновить blacklist'))),
                "Checkbox2":(Checkbox, ("Активировать для своего списка сайтов", CTkButton, ('Изменить список сайтов'))),

            },
            True
        )
        # Вкладка О программе
        about_tab = self.create_tab()
        self.tab_frames["О программе"] = about_tab

        Content(
            about_tab,
            {
                "Label1": (Label, ("Информация о goodbyedpi.exe",)),
                "Label2": (Label, ("Информация о goodbyeDPI UI",)),
                "Label3": (Label, ("Благодарности",)),
                
            }
        )

        self.update_idletasks()
        self.switch_tab("Персонализация")


    def create_tab(self, scroll=False):
        if not scroll:
            tab = CTkFrame(self, width=700, fg_color="transparent")
            tab.grid(row=0, column=1, padx=20, pady=30)
            tab.grid_forget()
            return tab
        else:
            def mouseWheel(event):
                if scrollable_frame.winfo_reqheight() > self.winfo_height():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas = CTkCanvas(borderwidth=0, bg='black', highlightthickness=0, height=self.winfo_height())
            #canvas_transparent(canvas)

            

            scrollable_frame = CTkFrame(canvas,width=800*self.scaleFactor, fg_color='transparent')
            scrollable_frame.bind("<Configure>", lambda e: self.on_frame_configure(canvas))
            scrollable_frame.grid(row=0, column=0, padx=0, pady=0)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=700*self.scaleFactor)
            canvas.grid(row=0, column=1, sticky="n", padx=0, pady=(30, 0))

            scrollbar = CTkScrollbar(self, orientation="vertical", command=canvas.yview, height=self.winfo_height())
            scrollbar.grid(row=0, column=3, sticky="ns")

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"), width=700*self.scaleFactor, height=self.winfo_height())
            
            canvas.bind("<Configure>", lambda e: self.adjust_scroll_visibility(scrollable_frame, canvas, scrollbar))
            self.bind("<MouseWheel>", mouseWheel)
            canvas.grid_forget()
            return scrollable_frame, canvas, scrollbar

        
    def adjust_scroll_visibility(self, scrollable_frame, canvas, scrollbar):
        canvas.update_idletasks()
        canvas.configure(height=self.winfo_height())

        if scrollable_frame.winfo_reqheight() > self.winfo_height():
            scrollbar.configure(height=self.winfo_height())
            scrollbar.grid()
        else:
            scrollbar.grid_remove()

    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def switch_tab(self, tab_name):
        try:
            selected_button = self.sidebar_buttons[tab_name]
            if self.selected_button:
                self.selected_button[0].configure(fg_color="transparent", text_color=self.text_color)
                self.selected_button[1].configure(fg_color="transparent")

            self.selected_button = self.sidebar_buttons[tab_name]
            self.selected_button[0].configure(fg_color=self.hover_color, text_color=self.accent_color)
            self.selected_button[1].configure(fg_color=self.accent_color)
            self.selected_button[1].grid(row=1, column=1)
        except Exception as ex:
            print(ex)

        

        for f in self.tab_frames.values():
            if isinstance(f, list) or isinstance(f, tuple):
                f[1].grid_forget()
                f[2].grid_forget()
            else:
                f.grid_forget()

        frame = self.tab_frames[tab_name]
        if isinstance(frame, list) or isinstance(frame, tuple):
            if len(frame) > 1:
                frame[1].grid(row=0, column=1, pady=(30, 0))
                frame[2].grid(row=0, column=3)
                self.on_frame_configure(frame[1])
        else:
            frame.grid(row=0, column=1, padx=20, pady=30, sticky='sn')
        
    def switch_theme(self, value, call):
        if value == 'On':
            self.text_color = "#FFFFFF"
            self.hover_color = "#404040"
            self.grid_color = "#242424"
            
        else:
            self.text_color = "black"
            self.hover_color = "#DBDBDB"
            self.grid_color = '#EBEBEB'

        for btn in self.sidebar_buttons:
            self.sidebar_buttons[btn][0].configure(text_color=self.text_color, hover_color=self.hover_color)
        self.selected_button[0].configure(fg_color=self.hover_color, text_color=self.accent_color)
        for f in self.tab_frames.values():
            if isinstance(f, list) or isinstance(f, tuple):
                f[1].configure(bg=self.grid_color)
                f[1].update()

    
    def theme_change(self, theme):
        set_default_color_theme(theme)
if __name__ == "__main__":
    
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(1)
    app = SettingsApp()
    
    ApplyMica(windll.user32.FindWindowW(c_char_p(None), "Настройки"), True, False)
    
    app.mainloop()