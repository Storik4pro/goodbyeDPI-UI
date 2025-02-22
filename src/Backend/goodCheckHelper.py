import glob
import os
import shutil


from _data import (
    configs,
    DEBUG_PATH,
    DIRECTORY,
    GOODCHECK_PATH,
    Settings,
)
import psutil
from PySide6.QtCore import (
    QFileSystemWatcher,
    QTimer,
    Signal,
)
from PySide6.QtCore import QObject, Slot
from utils import start_process

ENGINE = {"GoodbyeDPI": "gdpi", "Zapret": "zapret"}

CHECKLISTS = [
    "default - all",
    "default - googlevideo",
    "default - miscellaneous",
    "empty",
    "twitter",
]

goodbyeDPI_strategies = [  # noqa: N816
    "[basic functionality test]",
    "[IPv4] - [e1 + e2 + e4] - [LONG]",
    "[IPv4] - [e1 + e2 + e4] - [SHORT]",
    "[IPv4] - [e1] - [LONG]",
    "[IPv4] - [e1] - [SHORT]",
    "[IPv4] - [e2] - [LONG]",
    "[IPv4] - [e2] - [SHORT]",
    "[IPv4] - [e4] - [LONG]",
    "[IPv4] - [e4] - [SHORT]",
    "[IPv6] - [e1 + e2 + e4] - [LONG]",
    "[IPv6] - [e1 + e2 + e4] - [SHORT]",
    "[IPv6] - [e1] - [LONG]",
    "[IPv6] - [e1] - [SHORT]",
    "[IPv6] - [e2] - [LONG]",
    "[IPv6] - [e2] - [SHORT]",
    "[IPv6] - [e4] - [LONG]",
    "[IPv6] - [e4] - [SHORT]",
]
zapret_strategies = [
    "[IPv4] - [TCP] - [No wssize, NO syndata]",
    "[IPv4] - [UDP]",
    "[IPv6] - [UDP]",
]


class GoodCheckHelper(QObject):
    output_signal = Signal(str)
    process_finished_signal = Signal()
    started = Signal()
    process_stopped_signal = Signal()

    def __init__(self):
        super().__init__()
        self.settings = Settings(
            GOODCHECK_PATH + "/config.ini",
            space_around_delimiters=False,
        )
        self.process = None
        self.log_watcher = QFileSystemWatcher()
        self.log_file_path = None
        self.last_log_size = 0
        self.log_monitor_timer = QTimer()
        self.log_monitor_timer.setInterval(100)
        self.log_monitor_timer.timeout.connect(self.read_new_log_content)

    @Slot(int)
    def open_goodcheck_file(self, file):
        os.startfile(
            DEBUG_PATH + f"{GOODCHECK_PATH}/CheckLists/{CHECKLISTS[file] + '.txt'}",
        )

    @Slot(str, str, str)
    def set_value(self, group, key, value):
        print(key)
        self.settings.change_setting(group, key, value)
        self.settings.save_settings()

    @Slot(str, str, result=str)
    def get_value(self, group, key):
        return self.settings.get_value(group, key)

    @Slot(str, str, result=bool)
    def get_bool(self, group, key):
        return True if self.settings.get_value(group, key) == "true" else False

    @Slot()
    def start(self):
        self.settings.change_setting(
            "GoodbyeDPI",
            "GoodbyeDPIFolder",
            "..\\\\goodbyeDPI",
        )
        self.settings.change_setting(
            "GoodbyeDPI",
            "GoodbyeDPIExecutableName",
            "gdpi.exe",
        )
        self.settings.change_setting(
            "GoodbyeDPI",
            "GoodbyeDPIServiceNames",
            "goodbyedpi",
        )
        self.settings.change_setting("Zapret", "ZapretFolder", "..\\\\zapret")
        self.settings.change_setting("ByeDPI", "ByeDPIFolder", "..\\\\byedpi")

        if os.path.exists(DIRECTORY + "data/goodbyeDPI/x86_64/goodbyedpi.exe"):
            shutil.copy(
                DIRECTORY + "data/goodbyeDPI/x86_64/goodbyedpi.exe",
                DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe",
            )

        self.settings.save_settings()
        configs["goodcheck"].reload_config()

        log_pattern = os.path.join(
            GOODCHECK_PATH + "/Logs",
            "logfile_GoodCheckGoGo_*.log",
        )
        for log_file in glob.glob(log_pattern):
            try:
                os.remove(log_file)
            except Exception as e:
                print(f"Не удалось удалить файл {log_file}: {e}")

        if self.process is None:
            arguments = [
                "-q",
                "-f",
                ENGINE[configs["goodcheck"].get_value("engine")],
                "-m",
                configs["goodcheck"].get_value("curl").lower(),
                "-c",
                CHECKLISTS[configs["goodcheck"].get_value("check_list")] + ".txt",
                "-s",
                (
                    goodbyeDPI_strategies[configs["goodcheck"].get_value("strategies")]
                    if configs["goodcheck"].get_value("engine") == "GoodbyeDPI"
                    else zapret_strategies[configs["goodcheck"].get_value("strategies")]
                )
                + ".txt",
                "-p",
                str(configs["goodcheck"].get_value("p")),
            ]
            print(arguments)
            self.process = start_process(
                *arguments,
                execut="goodcheckgogo.exe",
                path=DEBUG_PATH + GOODCHECK_PATH + "/goodcheckgogo.exe",
                cwd=DEBUG_PATH + GOODCHECK_PATH,
            )

            self.started.emit()
            QTimer.singleShot(1000, self.find_new_log_file)

        else:
            pass

    def find_new_log_file(self):
        log_pattern = os.path.join(
            GOODCHECK_PATH + "/Logs",
            "logfile_GoodCheckGoGo_*.log",
        )
        log_files = glob.glob(log_pattern)
        if log_files:
            self.log_file_path = log_files[0]
            self.last_log_size = 0
            self.log_monitor_timer.start()
        else:
            QTimer.singleShot(1000, self.find_new_log_file)

    @Slot()
    def read_new_log_content(self):
        if self.log_file_path and os.path.exists(self.log_file_path):
            with open(self.log_file_path, "r", encoding="utf-8") as log_file:
                log_file.seek(self.last_log_size)
                new_content = log_file.read()
                self.last_log_size = log_file.tell()
                if new_content:
                    if "Exiting with an error..." in new_content:
                        self.log_monitor_timer.stop()
                        self.process.terminate()
                        self.process.kill()
                        self.process = None
                    self.output_signal.emit(new_content)
        else:
            self.log_monitor_timer.stop()

    @Slot()
    def stop_process(self):
        if self.process is not None:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["pid"] == self.process.pid:
                    try:
                        proc.terminate()
                        self.process = None
                        break
                    except psutil.NoSuchProcess:
                        pass

            self.process = None
            self.process_stopped_signal.emit()
            self.log_monitor_timer.stop()
            if os.path.exists(DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe"):
                os.remove(DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe")
        else:
            if os.path.exists(DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe"):
                os.remove(DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe")
            self.process_stopped_signal.emit()

    @Slot()
    def handle_finished(self):
        self.process_finished_signal.emit()
        self.process = None
        self.log_monitor_timer.stop()
        if os.path.exists(DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe"):
            os.remove(DIRECTORY + "data/goodbyeDPI/x86_64/gdpi.exe")
