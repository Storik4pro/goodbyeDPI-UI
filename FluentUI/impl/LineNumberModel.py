from PySide6.QtCore import QAbstractListModel, Qt, Signal, Property, QModelIndex, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickTextDocument

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class LineNumberModel(QAbstractListModel):
    lineCountChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__lineCount = 0

    def lineCount(self):
        return self.__lineCount

    def setLineCount(self, lineCount):
        if lineCount < 0:
            print("lineCount must be greater than zero")
            return
        if self.__lineCount == lineCount:
            return
        if self.__lineCount < lineCount:
            self.beginInsertRows(QModelIndex(), self.__lineCount, lineCount - 1)
            self.__lineCount = lineCount
            self.endInsertRows()
        elif self.__lineCount > lineCount:
            self.beginRemoveRows(QModelIndex(), lineCount, self.__lineCount - 1)
            self.__lineCount = lineCount
            self.endRemoveRows()
        self.lineCountChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        return self.__lineCount

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not self.checkIndex(index) or role != Qt.ItemDataRole.DisplayRole:
            return None
        return index.row()

    @Slot(QQuickTextDocument, int, result=int)
    def currentLineNumber(self, textDocument: QQuickTextDocument, cursorPosition: int):
        td = textDocument.textDocument()
        if td is not None:
            tb = td.findBlock(cursorPosition)
            return tb.blockNumber()
        return -1

    lineCount = Property(int, lineCount, setLineCount, notify=lineCountChanged)
