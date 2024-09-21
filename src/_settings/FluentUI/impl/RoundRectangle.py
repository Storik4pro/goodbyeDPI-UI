from PySide6.QtCore import Signal, Property, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, Qt, QLinearGradient
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class RoundRectangle(QQuickPaintedItem):
    colorChanged = Signal()
    radiusChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__color = QColor(255, 255, 255, 255)
        self.__radius = [0, 0, 0, 0]
        self.colorChanged.connect(lambda: self.update())
        self.radiusChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        rect = self.boundingRect()
        path.moveTo(rect.bottomRight() - QPointF(0, self.__radius[2]))
        path.lineTo(rect.topRight() + QPointF(0, self.__radius[1]))
        path.arcTo(QRectF(QPointF(rect.topRight() - QPointF(self.__radius[1] * 2, 0)),
                          QSize(self.__radius[1] * 2, self.__radius[1] * 2)),
                   0, 90)
        path.lineTo(rect.topLeft() + QPointF(self.__radius[0], 0))
        path.arcTo(QRectF(QPointF(rect.topLeft()), QSize(self.__radius[0] * 2, self.__radius[0] * 2)), 90, 90)
        path.lineTo(rect.bottomLeft() - QPointF(0, self.__radius[3]))
        path.arcTo(QRectF(QPointF(rect.bottomLeft() - QPointF(0, self.__radius[3] * 2)),
                          QSize(self.__radius[3] * 2, self.__radius[3] * 2)),
                   180, 90)
        path.lineTo(rect.bottomRight() - QPointF(self.__radius[2], 0))
        path.arcTo(QRectF(QPointF(rect.bottomRight() - QPointF(self.__radius[2] * 2, self.__radius[2] * 2)),
                          QSize(self.__radius[2] * 2, self.__radius[2] * 2)),
                   270, 90)
        painter.fillPath(path, self.__color)
        painter.restore()

    @Property(list, notify=radiusChanged)
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if self.__radius == value:
            return
        self.__radius = value
        self.radiusChanged.emit()

    @Property(QColor, notify=colorChanged)
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if self.__color == value:
            return
        self.__color = value
        self.colorChanged.emit()
