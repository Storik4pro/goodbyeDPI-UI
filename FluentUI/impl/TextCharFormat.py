from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtGui import QTextCharFormat, QFont, QColor, QBrush
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class TextCharFormat(QObject, QTextCharFormat):
    fontChanged = Signal()
    foregroundChanged = Signal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        QTextCharFormat.__init__(self)

    def getTextFont(self):
        return QTextCharFormat.font(self)

    def setTextFont(self, font):
        if font == QTextCharFormat.font(self):
            return
        QTextCharFormat.setFont(self, font)
        self.fontChanged.emit()

    def getForeground(self):
        return QTextCharFormat.foreground(self).color()

    def setForeground(self, foreground):
        if isinstance(foreground, QColor):
            QTextCharFormat.setForeground(self, QBrush(foreground))
            self.foregroundChanged.emit()

    font = Property(QFont, getTextFont, setTextFont, notify=fontChanged)
    foreground = Property(QColor, getForeground, setForeground, notify=foregroundChanged)
