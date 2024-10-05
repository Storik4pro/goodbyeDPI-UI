from customtkinter import *

COLOR_FRAME = '#0f0f0f'

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
            entry.red() 

        else:
            if not self.last_valid_value in entry_var.get():
               entry_var.set("") 
            else:
                entry_var.set(self.last_valid_value)
            entry.red() 
            if label_info: label_info.configure(text_color="red")

    def set_valid_value(self, entry_var:Variable,  entry, label_info:CTkLabel=None):
        entry_var.set(self.last_valid_value)
        entry.normal()
        if label_info: label_info.configure(text_color="#FFFFFF")

class EntryElement:
    def __init__(self, parent:CTkFrame|CTkCanvas, placeholder_text:str, label_element:CTkLabel=None, validate_function:ValidateValue=None, 
                 value="Value", width:int|str=240, window:CTk=None, function=None, padx=0, pady=0, state="normal") -> None:
        self.label_info = label_element
        self.validate_function = validate_function
        self.function = function
        self.entry_var = StringVar(value=validate_function.last_valid_value if validate_function else value)

        self.last_valid_value = self.entry_var.get()
        try:
            if self.validate_function:
                self.entry_var.trace_add("write", lambda *args :self.check_input())
        except Exception as ex:
            print(ex)
        self.entry = CTkEntry(master=parent, placeholder_text=placeholder_text, textvariable=self.entry_var,
                              width=width if type(width) == int else 240,
                              border_width=2, border_color=COLOR_FRAME)
        self.entry.configure(state=state)
        self.entry.pack(padx=padx, pady=pady, fill=width if type(width) == str else None)
        
        if self.validate_function:
            parent.bind("<Button-1>", lambda *args :self.mouse_press('parent'), add="+")
            if window: window.bind_all("<Button-1>", lambda *args :self.mouse_press('window'), add="+")
        
    
    def get(self):
        return self.entry_var.get()
    
    def red(self):
        self.entry.configure(border_color="red")

    def normal(self, valid_value=None):
        self.entry.configure(border_color=COLOR_FRAME)
        if valid_value: self.last_valid_value = valid_value

    def mouse_press(self, state):
        if state=='parent':
            self.check_input()
        else:
            if self.validate_function.last_valid_value != self.entry_var.get():
                self.validate_function.set_valid_value(self.entry_var, self, self.label_info)

    def check_input(self, *args):
        self.validate_function.validate(self.entry_var, self, self.label_info, self.last_valid_value)
        if self.function:
            self.function(self.validate_function.last_valid_value)
    
    def on_click(self, event):
        current_value = self.entry_var.get()

        if self.entry.cget("border_color") == "red":
            self.entry_var.set(self.last_valid_value)
            self.entry.configure(border_color=COLOR_FRAME)

    def pack(self, padx=0, pady=0, fill_mode=None):
        self.entry.pack(padx=padx, pady=pady, fill=fill_mode)

    def pack_forget(self):
        self.entry.pack_forget()