import asyncio
import ctypes
import queue
import re
import subprocess
import sys
import threading
import time
import winpty
from customtkinter import *
from _data import FONT, DIRECTORY, settings
from PIL import Image
import sched, time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit(0)

class GoodbyedpiApp(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('800x500')
        self.title(f'goodbyeDPI listen')
        self.minsize(800, 500)

        self.stop = False
        self.stop_func = None

        self.content_frame = CTkFrame(self, width=400)
        self.status_text = "Идет подготовка к запуску ... "

        self.header_frame = CTkFrame(self.content_frame)
        self.logo = CTkImage(light_image=Image.open(DIRECTORY+"data/terminal.ico"), size=(40, 40))
        self.logo_label = CTkLabel(self.header_frame, image=self.logo, text="")
        self.logo_label.pack(side="left", pady=10, padx=(10, 5))

        self.header_text_frame = CTkFrame(self.header_frame, fg_color='transparent')
        
        self.header_text = CTkLabel(self.header_text_frame, text="Чтение вывода goodbyedpi.exe", anchor="w", font=(FONT, 18, "bold"))
        self.header_text.pack(pady=(10, 0), padx=(5, 10), fill="x", expand=True)

        self.status_label = CTkLabel(self.header_text_frame, text=self.status_text, anchor="w", justify='left', font=(FONT, 14))
        self.status_label.pack(side="bottom",padx=(5, 10), pady=(0, 10), fill="x", expand=True)

        self.header_text_frame.pack(fill='x')
        
        self.header_frame.pack(fill="x",pady=(10, 0), padx=10)

        self.output_textbox = CTkTextbox(self.content_frame, wrap="word", width=700, height=250, font=('Cascadia Mono', 15))
        self.output_textbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.output_textbox.insert("1.0", '[DEBUG] Идет подключение к goodbyedpi.exe ...\n\n')
        self.output_textbox.configure(state="disabled")

        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.button_frame = CTkFrame(self.content_frame, fg_color='transparent')

        self.copy_icon = CTkImage(light_image=Image.open(DIRECTORY+"data/copy_icon.png"), size=(20, 20))
        self.copy_button = CTkButton(self.button_frame, image=self.copy_icon, text="копировать вывод",fg_color="transparent",border_width=2, font=(FONT, 15), width=200, command=self.copy_output)
        self.copy_button.pack(side="left", padx=(10, 5),pady=10)

        self.stop_button = CTkButton(self.button_frame, text="остановить службу", font=(FONT, 15), width=200, command=self.stop_service)
        self.stop_button.pack(side="right", padx=(5, 10),pady=10)

        self.restart_button = CTkButton(self.button_frame, text="перезапустить процесс", font=(FONT, 15), width=200, command=self.restart_service)
        self.restart_button.pack(side="right", padx=(5, 10),pady=10)

        self.button_frame.pack(fill="x")

        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

    def clear_output(self):
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

    def add_output(self, output):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert(END, f'{output}')
        self.output_textbox.configure(state="disabled")
        self.output_textbox.see(END)
        
        if "Filter activated" in output:
            self.update_status("процесс goodbyedpi.exe успешно запущен и работает без ошибок")
        elif "Error opening filter" in output:
            self.update_status("процесс goodbyedpi.exe завершил работу с ошибкой")
        elif "[DEBUG] The goodbyedpi.exe process has been terminated" in output:
            self.update_status("процесс goodbyedpi.exe был остановлен по неизвесной причине")

    def update_status(self, status_text):
        self.status_label.configure(text=status_text)

    def copy_output(self):
        self.clipboard_clear()
        self.clipboard_append(self.output_textbox.get("1.0", "end-1c"))

    def connect_func(self, stop_func):
        self.stop_func = stop_func

    def stop_service(self):
        if self.stop_func:self.stop_func()
        self.stop = True
        self.add_output("[INFO] Служба остановлена.\n")


    def restart_service(self):
        if self.stop_func:self.stop_func()
        self.add_output("[INFO] Перезапуск процесса...\n")

app = GoodbyedpiApp()

def remove_ansi_sequences(text):
    stage1 = re.sub(r'\w:\\[^ ]+', '', text)
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE

    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])|\]0;')
    stage2 = ansi_escape.sub('', stage1)
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print("") # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    stage2 = stage2.replace("https://github.com/ValdikSS/GoodbyeDPI", "https://github.com/ValdikSS/GoodbyeDPI\n\n")
    return stage2

class GoodbyedpiProcess:
    def __init__(self, path, app:GoodbyedpiApp = None) -> None:
        self.path = path
        self.app = app
        self.args = ''
        self.output = ''
        self.pty=None
        self.goodbyedpi_thread = None
        self.stop_event = threading.Event()
        self.pty_process = None
        self.queue = queue.Queue()
        self.proc = None

    def start_goodbyedpi_thread(self, *args):
        command = [str(self.path + 'goodbyedpi.exe')]
        command.extend(*args)
        print(command)

        self.proc=subprocess.Popen(command, cwd=self.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.pty_process = winpty.PtyProcess.spawn(command, cwd=self.path)


        self.output = []

        while not self.stop_event.is_set():
            if self.pty_process.isalive():
                try:
                    data = self.pty_process.read(1024) 
                    print("data2")
                    if not data:
                        pass
                    data = remove_ansi_sequences(data)
                    self.queue.put(data)
                    self.output.append(data)
                except OSError as e:
                    print(e)
                    break
            else: break

        self.cleanup()

        return

    def cleanup(self):
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except:pass
        self.pty_process = None
        self.queue.put('\n[DEBUG] The goodbyedpi.exe process has been terminated\n')

    def check_process_status(self):
        print("call")
        if self.proc and self.proc.poll() is not None:
            self.stop_goodbyedpi()
            print(self.pty_process.isalive())
        elif not self.goodbyedpi_thread.is_alive():
            self.cleanup()
        else:
            if self.app: 
                self.app.after(5000, self.check_process_status)

    def start_goodbyedpi(self, *args):
        if not self.goodbyedpi_thread or not self.goodbyedpi_thread.is_alive():
            self.stop_event.clear()
            self.goodbyedpi_thread = threading.Thread(target=lambda: self.start_goodbyedpi_thread(*args))
            self.goodbyedpi_thread.start()

            self.check_queue()
        else:
            return False
        
    def stop_goodbyedpi(self):
        print('stopping ...')
        self.stop_event.set()
        if self.pty_process:
            self.pty_process.close(True)
        if self.goodbyedpi_thread:
            self.goodbyedpi_thread.join(timeout=5)
            if self.goodbyedpi_thread.is_alive():
                print('Forsing terminating')

    def check_queue(self):
        while not self.queue.empty():
            data = self.queue.get()
            if self.app:
                self.app.add_output(data)

        if self.goodbyedpi_thread.is_alive():
            self.app.after(100, self.check_queue)  # Проверка снова через 100ms

    def connect_app(self, app:GoodbyedpiApp):
        self.app = app
        self.app.add_output(self.output)

    def disconnect_app(self):
        if self.app:
            try:self.app.destroy()
            except:pass
            self.app = None
            


process = GoodbyedpiProcess('C://Users\serst\Documents\goodbyeDPI_UI\goodbyeDPI-UI\data\goodbyeDPI//x86_64/',app)
process.start_goodbyedpi(settings.settings['COMMANDS']['russia_blacklist_dnsredir'].split(', '))
app.connect_func(process.stop_goodbyedpi)
app.mainloop()
process.disconnect_app()

print('end')
