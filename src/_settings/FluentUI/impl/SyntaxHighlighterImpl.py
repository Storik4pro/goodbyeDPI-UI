from PySide6.QtCore import Signal, Property, Slot, QObject
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class SyntaxHighlighterImpl(QSyntaxHighlighter):
    textDocumentChanged = Signal()
    highlightBlockChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__textDocument = None

    def highlightBlock(self, text):
        self.highlightBlockChanged.emit(text)

    @Slot(int, int, QObject)
    def setFormat(self, start, count, _format):
        if isinstance(_format, QTextCharFormat):
            super().setFormat(start, count, _format)
        elif isinstance(_format, QColor):
            char_format = QTextCharFormat()
            char_format.setForeground(_format)
            super().setFormat(start, count, char_format)
        elif isinstance(_format, QFont):
            char_format = QTextCharFormat()
            char_format.setFont(_format)
            super().setFormat(start, count, char_format)

    @Property("QVariant", notify=textDocumentChanged)
    def textDocument(self):
        return self.__textDocument

    @textDocument.setter
    def textDocument(self, value):
        if self.__textDocument == value:
            return
        self.__textDocument = value
        if self.__textDocument is None:
            self.setDocument(None)
        else:
            doc = self.__textDocument.textDocument()
            self.setDocument(doc)
        self.textDocumentChanged.emit()
