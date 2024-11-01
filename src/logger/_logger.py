from datetime import datetime
import logging
import os
import platform
import sys
import tkinter.messagebox as messagebox

system_info = f"{platform.system()} {platform.win32_ver()[1]} {platform.architecture()[0]}"

error_placeholder = "{title}\n\
Application version: {version}\n\
System information: {system}\n\
Error type: {_type}\n\
Details:\n\
-----\n\
{info}\n\
-----\n\
Press CTRL+C to copy error output.\n\n\
If this error persists, please contact app support and report the issue."

er = "Unable to start application"
warn = ""
info = ""
class AppLogger:
    def __init__(self, version, utilname, log_level=logging.WARNING) -> None:
        self.__version__ = version
        self.utilname = utilname
        self.logs_folder = 'logs'
        self.log_file_path = os.path.join(self.logs_folder, f'{utilname}.log')
        self.logger = logging.getLogger(__name__)
        os.makedirs(self.logs_folder, exist_ok=True)
        try:
            logging.basicConfig(filename=self.log_file_path, level=log_level)
        except:
            pass

    def create_logs(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.info(f'[{_time}] {text}')

    def raise_warning(self, warning):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.warning(f'[{_time}] {warning}')
        self.show_warning_message(warning)

    def raise_error(self, error):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.error(f'[{_time}] {error}')
        self.show_error_message(error)

    def raise_critical(self, error):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.critical(f'[{_time}] {error}')
        self.show_criticalerror_message(error)

    def show_warning_message(self, info):
        messagebox.showwarning("GoodbyeDPI UI", error_placeholder.format(title=warn, version=self.__version__, system=system_info, _type="WARNING", info=info))

    def show_error_message(self, info):
        messagebox.showerror("GoodbyeDPI UI", error_placeholder.format(title=info,version=self.__version__, system=system_info, _type="ERROR", info=info))

    def show_criticalerror_message(self, info):
        messagebox.showerror("GoodbyeDPI UI", error_placeholder.format(title=er, version=self.__version__, system=system_info, _type="CRITICAL ERROR", info=info))
        sys.exit(-1)

    def create_debug_log(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.debug(f'[{_time}] {text}')

    def create_info_log(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.info(f'[{_time}] {text}')

    def create_warning_log(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.warning(f'[{_time}] {text}')

    def create_error_log(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.error(f'[{_time}] {text}')

    def create_critical_log(self, text):
        _time = datetime.now().strftime('%H:%M:%S')
        self.logger.critical(f'[{_time}] {text}')

    def cleanup_logs(self):
        if os.path.exists(self.log_file_path) and os.path.getsize(self.log_file_path) == 0:
            try:
                logging.shutdown()
                os.remove(self.log_file_path)
            except Exception as ex:
                print(ex)
                pass