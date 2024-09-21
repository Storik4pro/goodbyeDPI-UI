import random
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import Slot, Signal, Property, QObject
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "Gallery"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class TreeDataGridController(QObject):
    dataChanged = Signal()
    loadDataStart = Signal()
    loadDataSuccess = Signal()

    @Property(list, notify=dataChanged)
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        if self.__data == value:
            return
        self.__data = value
        self.dataChanged.emit()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.__names = [self.tr("John"), self.tr("Alice"), self.tr("Michael"), self.tr("Sophia"), self.tr("David"),
                        self.tr("Emma"), self.tr("Chris"), self.tr("Olivia"), self.tr("Daniel"), self.tr("Isabella")]
        self.__addresses = [self.tr("123 Main St"), self.tr("456 Oak Ave"), self.tr("789 Pine Rd"),
                            self.tr("321 Maple Dr"), self.tr("654 Birch Ln")]
        self.__avatars = ["qrc:/qt/qml/Gallery/res/image/avatar_1.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_2.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_3.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_4.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_5.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_6.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_7.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_8.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_9.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_10.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_11.svg",
                          "qrc:/qt/qml/Gallery/res/image/avatar_12.svg"]
        self.__descriptions = [self.tr("A software engineer with a passion for coding."),
                               self.tr("Loves outdoor activities and traveling."),
                               self.tr("An artist who enjoys painting and sculpting."),
                               self.tr("A teacher dedicated to inspiring students."),
                               self.tr("A chef with a love for culinary experiments.")]
        self.__data = []

    def __dig(self, path, level):
        list_data = []
        for i in range(5):
            key = f"{path}-{i}"
            row_data = self.generateRowData()
            row_data["__key"] = key
            if level > 0:
                row_data["__children"] = self.__dig(key, level - 1)
            list_data.append(row_data)
        return list_data

    @Slot(result=dict)
    def generateRowData(self) -> dict:
        return {
            "name": self.__names[random.randint(0, len(self.__names) - 1)],
            "age": random.randint(20, 60),
            "address": self.__addresses[random.randint(0, len(self.__addresses) - 1)],
            "avatar": self.__avatars[random.randint(0, len(self.__avatars) - 1)],
            "description": self.__descriptions[random.randint(0, len(self.__descriptions) - 1)],
            "height": 48,
            "minimumHeight": 40,
            "maximumHeight": 240,
        }

    @Slot()
    @Slot(int)
    @Slot(int, int)
    def loadData(self, path="0", level=4):

        def __task():
            self.loadDataStart.emit()
            self.__data.clear()
            self.__data = self.__dig(path, level)
            self.loadDataSuccess.emit()

        self.executor.submit(__task)
