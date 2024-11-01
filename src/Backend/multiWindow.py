from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from qasync import QEventLoop, asyncSlot
from toasted import ToastDismissReason

from utils import show_error, show_message
from _data import text

class MultiWindow(QObject):
    multi_window_init = Signal(str)
    multi_window_close = Signal(str)

    def __init__(self):
        super().__init__()
        self.windows = []

    @Slot(str)
    def init_window(self, windowId):
        print("INIT", windowId)
        if not windowId in self.windows:
            self.windows.append(windowId)
            self.multi_window_init.emit(windowId)
        else: 
            self.multi_window_close.emit(windowId)

    @Slot(str)
    def close_window(self, windowId):
        print(windowId, self.windows)
        if windowId in self.windows:
            self.windows.remove(windowId)
            self.multi_window_close.emit(windowId)

    @Slot(str, result=bool)
    def check_window_init(self, windowId):
        if windowId in self.windows:
            return True
        else: return False
