from PySide6.QtCore import QObject, Signal, Property, QFileSystemWatcher
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class FileWatcher(QObject):
    pathChanged = Signal()
    fileChanged = Signal()

    @Property(str, notify=pathChanged)
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        if self.__path == value:
            return
        self.__path = value
        self.pathChanged.emit()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.__path: str = ""
        self.__watcher: QFileSystemWatcher = QFileSystemWatcher()

        self.__watcher.fileChanged.connect(lambda path: self.__onFileChanged())

        self.pathChanged.connect(lambda: self.__onPathChanged())
        if self.__path != "":
            self.__watcher.addPath(self.__path)

    def __onPathChanged(self):
        self.__clean()
        self.__bindFilePath(self.__path)

    def __onFileChanged(self):
        self.fileChanged.emit()
        self.__bindFilePath(self.__path)

    def __bindFilePath(self, path: str):
        if path and path.startswith("file:///"):
            query_index = path.find('?')
            if query_index != -1:
                path = path[:query_index]
            self.__watcher.addPath(path.replace("file:///", ""))

    def __clean(self):
        for item in self.__watcher.files():
            self.__watcher.removePath(item)
