from tkinter import messagebox
import typing
from customtkinter import *
import tkinter as ttk

from customtkinter import CTkCanvas, CTkFrame
from _data import settings, SETTINGS_FILE_PATH, GOODBYE_DPI_PATH, FONT, DEBUG, DIRECTORY, text
from PIL import Image, ImageTk, ImageDraw
import win32gui
import win32con
import win32api
from ctypes import windll, c_char_p
from win32material import *


ELEMENT_HEIGHT = 60
ELEMENT_WIDTH = 700

COLOR_HOVER = '#404040'
COLOR_FRAME = '#0f0f0f'

def canvas_transparent(w):
    colorkey = 0x00030201
    hwnd = w.winfo_id()
    
    wnd_exstyle = windll.user32.GetWindowLongA(hwnd, -20)  # GWL_EXSTYLE
    new_exstyle = wnd_exstyle | 0x00080000  # WS_EX_LAYERED
    windll.user32.SetWindowLongA(hwnd, -20, new_exstyle)  # GWL_EXSTYLE
    windll.user32.SetLayeredWindowAttributes(hwnd, colorkey, 255, 0x00000001) 

class BaseElement:
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0) -> None:
        self.frame = CTkFrame(parent, width=ELEMENT_WIDTH, height=ELEMENT_HEIGHT, fg_color=COLOR_FRAME)
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
            try:
                widget.configure(state="normal")
            except:
                pass

class EntryElement:
    def __init__(self, parent:CTkFrame|CTkCanvas, placeholder_text:str, label_element:CTkLabel=None, validate_function=None, width=240, window:CTk=None) -> None:
        self.label_info = label_element
        self.entry_var = StringVar(value="1")
        self.entry_var.trace_add("write", self.validate_input if validate_function is None else validate_function)

        self.entry = CTkEntry(master=parent, placeholder_text=placeholder_text, textvariable=self.entry_var, width=width, border_width=2, border_color=COLOR_FRAME)
        self.entry.grid(row=0, column=1, padx=(0, 0), pady=0)

        self.last_valid_value = self.entry_var.get()

        if window: window.bind_all("<Button-1>", self.on_click, add="+")
    
    def get(self):
        return self.entry.get()
    
    def red(self):
        self.entry.configure(border_color="red")

    def normal(self, valid_value=None):
        self.entry.configure(border_color=COLOR_FRAME)
        if valid_value: self.last_valid_value = valid_value

    def validate_input(self, *args):
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

class FrameButton:
    def __init__(self, id, parent) -> None:
        pass

class Switch(BaseElement):
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0, label='Sample label', subLabel:str=None, command=None, var:Variable=None) -> None:
        super().__init__(parent, row=row, column=column)
        self.var = var if var else StringVar(value='Off')
        self.command = command

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
        
        switch = CTkSwitch(self.frame, text='', variable=self.var, onvalue='On', offvalue='Off', width=40, fg_color="#1C1C1C", command=self.toggle, corner_radius=10)  # Закругленные углы
        switch.grid(row=0, column=2, padx=(0,20))

    def toggle(self):
        self.stateLabel.configure(text=self.var.get())
        if self.command: 
            self.call = True
            self.command(self.var.get(), self)
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

        self.combobox = CTkOptionMenu(self.frame, values=values, font=(FONT, 15), width=240, corner_radius=10, command=function)
        self.combobox.grid(row=0, column=1, padx=(0, 20))

class Button(BaseElement):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample text', subLabel=None, func=None) -> None:
        super().__init__(parent, row, column)

        self.func = func
        self.frame.configure(fg_color=COLOR_FRAME)

        self.label_frame = CTkFrame(self.frame, width=540, height=ELEMENT_HEIGHT, fg_color="transparent")
        self.label_frame.grid_propagate(False)
        self.label_frame.grid(row=0, column=0, pady=0, padx=(20, 0))

        height = ELEMENT_HEIGHT//2 if subLabel else ELEMENT_HEIGHT

        self.label = CTkLabel(self.label_frame, text=label, font=(FONT, 15), height=height, width=570, fg_color="transparent", anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 0), pady=0)

        if subLabel:
            self.label_info = CTkLabel(self.label_frame, text=subLabel, font=(FONT, 12), height=height, width=570, fg_color="transparent", anchor="w")
            self.label_info.grid(row=1, column=0, padx=(0, 0), pady=0)

        img = CTkImage(light_image=Image.open(DIRECTORY+"data/arrow-light.png"), dark_image=Image.open(DIRECTORY+"data/arrow-dark.png"), size=(20, 20))
        self.img_label = CTkLabel(self.frame, text='', width=218, height=20, compound = "right", anchor='s', image=img)
        self.img_label.grid(row=0, column=1, padx=(0, 20))

        self.bind_all_widgets(self.frame)

        self.bind_execute(self.frame)

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
        self.frame.configure(fg_color=COLOR_HOVER)

    def on_leave(self, event):
        self.frame.configure(fg_color=COLOR_FRAME)

    def execute_function(self, event):
        print("function executed")
        if self.func: self.func()

class SwitchButton(Button):
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
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample label', subLabel=None, window:CTk = None) -> None:
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

        self.entry = EntryElement(self.frame, placeholder_text="Значение от 1 до 50", label_element=self.label_info if subLabel else None, validate_function=self.validate_input, window=window)

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
    def __init__(self, parent:CTkFrame|CTkCanvas, row=0, column=0, label='Sample label') -> None:
        label = CTkLabel(parent, text=label, font=(FONT, 25), width=700, anchor='w', fg_color="transparent")
        label.grid(row=row, column=column, padx=0, pady=(0, 20))
        self.call=False

    def disable(self):pass
    def enable(self):pass

        
class Checkbox(BaseElement):
    def __init__(self, parent: CTkFrame | CTkCanvas, row=0, column=0, label='Sample Label', element:CTkEntry|CTkOptionMenu=None, args:tuple=None, func=None) -> None:
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
    
    def toggle(self):
        if self.variable.get() == 'On':
            self.element.configure(state='normal')
        else:
            self.element.configure(state='disabled')

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
        self.title("Настройки")
        self.geometry("1100x600")
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
                "Combobox1": (Combobox, ("Пресет настроек", ["blacklist-с изменением DNS", "blacklist", "с изменением DNS", "без параметров"])),
                "Switch1": (Switch, ("Блокировка пассивных DPI",)),
                "Switch2": (Switch, ("Замена заголовка Host на hoSt",)),
                "Switch3": (Switch, ("Удаление пробела между именем параметра Host и его заголовком",)),
                "Switch4": (Switch, ("Изменение регистра для значения заголовка Host", 'Например, замена test.com на tEsT.cOm',)),
                "Switch5": (Switch, ("Фрагментация HTTP",)),
                "Button1": (SwitchButton, ("Фрагментация HTTPS", "Случайное кол-во фрагментаций, Выбор фрагментации TLS", lambda: self.switch_tab('HTTPS'))),
                "Switch6": (SwitchButton, ("Фрагментация длительных (persistent, keep-alive) HTTP-соединений", "Не дожидаться первого сегмента ACK", lambda: self.switch_tab('HTTP'))),
                "Switch8": (SwitchButton, ("Находить и обрабатывать HTTP-трафик на порте, отличном от 80", "Добавление собственного TCP порта", lambda: self.switch_tab('port'))),
                "Button2": (Button, ("Перенаправление DNS запросов", "Перенаправление на IP адрес, Перенаправление на IPv6 адрес", lambda: self.switch_tab('DNS'))),
                "Switch9": (SwitchButton, ("Фильтрация дополнительных IP ID подключений", "Изменение значения ID", lambda: self.switch_tab('IPID'))),
                "Button10": (Button, ("Отправка фейковых HTTP/HTTPS запросов", "Ручная настройка TTL, Автоопределение TTL, отправка контрольной суммы TCP", lambda: self.switch_tab('IPID'))),
                "Switch10": (Switch, ("Отправка поддельных запросов с помощью TCP SEQ/ACK",)),
                "Button11": (Button, ("Оптимизация", "Ограничение обработки пакетов TCP", lambda: self.switch_tab('IPID'))),
                "Switch11": (Switch, ("Добавление пробела между методом HTTP и URL", "Обратите внимание: данная настройка влияет на работосопобность сайтов",)),
                "Button12": (Button, ("Список сайтов для обхода блокировки", "Обновление russia_blacklist.txt, Добавление своего списка сайтов", lambda: self.switch_tab('IPID'))),
            }
        )
        goodbyedpi_HTTPS = self.create_tab()
        self.tab_frames["HTTPS"] = goodbyedpi_HTTPS

        Content(
            goodbyedpi_HTTPS,
            {
                "Label1": (Label, ("Параметры goodbyeDPI > Фрагментация HTTPS",)),
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
                "Entry1": (Entry, ("Собственные TCP порты", "Добавление собственных портов для обработки goodbyedpi", self)),
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
                "Entry2": (Entry, ("Порт для перенаправления", None, self)),
                "Switch2": (Switch, ("Перенаправлять IPv6 запросы DNS запросы на указанный IPv6", None, "disabled")),
                "Entry3": (Entry, ("IPv6 адрес для перенаправления", None, self)),
                "Entry4": (Entry, ("Порт для перенаправления", None, self)),
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
                "Entry4": (Entry, ("Значение IP ID", "Например, для дом.ру это значение равно 54321", self)),

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

            scrollable_frame = CTkFrame(canvas,width=800, fg_color='transparent')
            scrollable_frame.bind("<Configure>", lambda e: self.on_frame_configure(canvas))
            scrollable_frame.grid(row=0, column=0, padx=0, pady=0)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=700)
            canvas.grid(row=0, column=1, sticky="n", padx=0, pady=(30, 0))

            scrollbar = CTkScrollbar(self, orientation="vertical", command=canvas.yview, height=self.winfo_height())
            scrollbar.grid(row=0, column=3, sticky="ns")

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"), width=700, height=self.winfo_height())
            
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

    def add_label_and_combobox(self, row, parent, label_text, combobox_values, func=None):
        frame = CTkFrame(parent, width=700,height=ELEMENT_HEIGHT)
        frame.grid_propagate(False)
        frame.grid(row=row, column=0, pady=2, padx=0)

        label = CTkLabel(frame, text=label_text, font=(FONT, 15), height=ELEMENT_HEIGHT, width=420, fg_color="transparent", anchor="w")
        label.grid(row=0, column=0, padx=(20, 0), pady=0)

        combobox = CTkOptionMenu(frame, values=combobox_values, font=(FONT, 15), width=240, corner_radius=10, command=func)  # Закругленные углы
        combobox.grid(row=0, column=1, padx=(0, 20))

    def add_switch(self, row, parent, switch_text, command=None, var:Variable = None, info:str=None):
        frame = CTkFrame(parent, width=700,height=ELEMENT_HEIGHT)
        frame.grid_propagate(False)
        frame.grid(row=row, column=0, pady=2, padx=0)

        var = var if var else StringVar(value='On')

        label_frame = CTkFrame(frame, width=570, height=ELEMENT_HEIGHT, fg_color="transparent")
        label_frame.grid_propagate(False)
        label_frame.grid(row=0, column=0, pady=0, padx=(20, 0))
        height = ELEMENT_HEIGHT//2 if info else ELEMENT_HEIGHT

        label = CTkLabel(label_frame, text=switch_text, font=(FONT, 15), height=height, width=570, fg_color="transparent", anchor="w")
        label.grid(row=0, column=0, padx=(0, 0), pady=0)

        if info:
            label_info = CTkLabel(label_frame, text=info, font=(FONT, 12), height=height, width=570, fg_color="transparent", anchor="w")
            label_info.grid(row=1, column=0, padx=(0, 0), pady=0)


        stateLabel = CTkLabel(frame, text=var.get(), font=(FONT, 15), height=ELEMENT_HEIGHT, width=40, fg_color="transparent", anchor="w")
        stateLabel.grid(row=0, column=1, padx=(15, 0), pady=0)
        
        switch = CTkSwitch(frame, text='', variable=var, onvalue='On', offvalue='Off', width=40, fg_color="#1C1C1C", command=command, corner_radius=10)  # Закругленные углы
        switch.grid(row=0, column=2, padx=(0,20))

    def add_checkbox(self, row, parent, checkbox_text):
        frame = CTkFrame(parent,width=700, height=ELEMENT_HEIGHT)
        frame.grid_propagate(False)
        frame.grid(row=row, column=0, pady=2, padx=0)

        checkbox = CTkCheckBox(frame, text=checkbox_text, font=(FONT, 15), fg_color="#1C1C1C", corner_radius=10)  # Закругленные углы
        checkbox.grid(row=0, column=0)

    def add_label(self, row, parent, label_text):
        label = CTkLabel(parent, text=label_text, font=(FONT, 25), width=700, anchor='w', fg_color="transparent")
        label.grid(row=row, column=0, padx=0, pady=(0, 20))

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
        
    def switch_theme(self, value):
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
    app = SettingsApp()
    ApplyMica(windll.user32.FindWindowW(c_char_p(None), "Настройки"), True, False)
    app.mainloop()