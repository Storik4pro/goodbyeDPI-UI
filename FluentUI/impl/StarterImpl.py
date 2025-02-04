import json
import sys

from PySide6.QtCore import (
    QObject,
    QTimer,
    Signal,
    Slot,
    QByteArray,
    QDateTime,
    QSharedMemory,
    qCritical,
    QLocale,
    QTranslator,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, qjsEngine

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class StarterImpl(QObject):
    handleDataChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__shared_memory = QSharedMemory(self)
        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.handleData)
        self.__data = {}
        self.__translator = QTranslator()

    @Slot(str)
    def checkApplication(self, appId):
        self.__shared_memory.setKey(appId)
        if self.__shared_memory.create(1024, QSharedMemory.AccessMode.ReadWrite):
            self.writeData()
            self.__timer.start(500)
        else:
            self.writeData()
            sys.exit(1)

    @Slot()
    @Slot(QLocale)
    def init(self, locale=None):
        if locale is None:
            locale = QLocale.system()
        js_engine = qjsEngine(self.parent())
        js_function = (
            """(function (path) { return Qt.resolvedUrl(path,null).toString();})"""
        )
        function = js_engine.evaluate(js_function)
        js_engine.globalObject().setProperty("resolvedUrl", function)
        if self.__translator.load(f":/qt/qml/FluentUI/FluentUI_{locale.name()}.qm"):
            QGuiApplication.installTranslator(self.__translator)

    def handleData(self):
        self.__shared_memory.lock()
        shared_memory_data = memoryview(self.__shared_memory.data())
        shared_memory_bytes = shared_memory_data.tobytes()
        shared_memory_str = shared_memory_bytes.decode("utf-8").rstrip("\x00")
        self.__shared_memory.unlock()
        data = json.loads(shared_memory_str)
        if data.get("timestamp") != self.__data.get("timestamp"):
            self.handleDataChanged.emit(data["args"])
            self.__data = data

    def writeData(self):
        self.__shared_memory.attach()
        self.__shared_memory.lock()
        data = {
            "timestamp": str(QDateTime.currentMSecsSinceEpoch()),
            "args": "&".join(QGuiApplication.arguments()),
        }
        if not self.__data:
            self.__data = data
        byte_array = QByteArray(json.dumps(data).encode("utf-8"))
        if byte_array.size() > 1024:
            qCritical(
                f"Data size is {byte_array.size()} bytes, which exceeds the limit of 1024 bytes."
            )
            return
        data = self.__shared_memory.data()
        if data is not None:
            shared_memory_data = memoryview(self.__shared_memory.data())
            shared_memory_data[: self.__shared_memory.size()] = bytearray(
                self.__shared_memory.size()
            )
            shared_memory_data[0 : byte_array.size()] = byte_array
        self.__shared_memory.unlock()
