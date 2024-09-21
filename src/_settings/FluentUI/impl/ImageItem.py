from PySide6.QtCore import Signal, Property
from PySide6.QtGui import QPainter, QImage
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class ImageItem(QQuickPaintedItem):
    sourceChanged = Signal()

    @Property(QImage, notify=sourceChanged)
    def source(self):
        return self.__source

    @source.setter
    def source(self, value):
        if self.__source == value:
            return
        self.__source = value
        self.sourceChanged.emit()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__source = QImage()
        self.sourceChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        painter.save()
        painter.drawImage(self.boundingRect(), self.__source)
        painter.restore()
