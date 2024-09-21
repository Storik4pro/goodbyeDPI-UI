from PySide6.QtCore import Signal, Property, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, Qt, QLinearGradient, QPen, QBrush
from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class TabBackgroundImpl(QQuickPaintedItem):
    radiusChanged = Signal()
    colorChanged = Signal()
    strokeColorChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__radius = 8
        self.__color = QColor()
        self.__strokeColor = QColor()
        self.radiusChanged.connect(lambda: self.update())
        self.colorChanged.connect(lambda: self.update())
        self.strokeColorChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self.__strokeColor)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.__color))
        path = QPainterPath()
        path.moveTo(self.__radius, self.__radius)
        path.arcTo(QRectF(self.__radius, 0, 2 * self.__radius, 2 * self.__radius), 180, -90)
        path.lineTo(self.width() - self.__radius * 2, 0)
        path.arcTo(QRectF(self.width() - 3 * self.__radius, 0, 2 * self.__radius, 2 * self.__radius), 90, -90)
        path.lineTo(self.width() - self.__radius, self.height() - self.__radius)
        path.arcTo(QRectF(self.width() - self.__radius, self.height() - 2 * self.__radius, 2 * self.__radius,
                          2 * self.__radius), 180, 90)
        path.lineTo(0, self.height())
        path.arcTo(QRectF(-self.__radius, self.height() - 2 * self.__radius, 2 * self.__radius, 2 * self.__radius), -90,
                   90)
        path.closeSubpath()
        painter.drawPath(path)
        pen.setColor(self.__color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(5, int(self.height()), int(self.width() - 5), int(self.height()))
        painter.restore()

    @Property(QColor, notify=strokeColorChanged)
    def strokeColor(self):
        return self.__strokeColor

    @strokeColor.setter
    def strokeColor(self, value):
        if self.__strokeColor == value:
            return
        self.__strokeColor = value
        self.strokeColorChanged.emit()

    @Property(int, notify=radiusChanged)
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
