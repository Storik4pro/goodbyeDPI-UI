from PySide6.QtCore import QObject, Signal, Slot


class MultiWindow(QObject):
    multi_window_init = Signal(str)
    multi_window_close = Signal(str)

    def __init__(self):
        super().__init__()
        self.windows = []

    @Slot(str)
    def init_window(self, window_id):
        print("INIT", window_id)
        if window_id not in self.windows:
            self.windows.append(window_id)
            self.multi_window_init.emit(window_id)
        else:
            self.multi_window_close.emit(window_id)

    @Slot(str)
    def close_window(self, window_id):
        print(window_id, self.windows)
        if window_id in self.windows:
            self.windows.remove(window_id)
            self.multi_window_close.emit(window_id)

    @Slot(str, result=bool)
    def check_window_init(self, window_id):
        if window_id in self.windows:
            return True
        return False
