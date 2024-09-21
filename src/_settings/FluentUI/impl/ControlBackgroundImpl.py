from PySide6.QtCore import Signal, Property, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, Qt, QLinearGradient
from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class ControlBackgroundImpl(QQuickPaintedItem):
    radiusChanged = Signal()
    borderWidthChanged = Signal()
    defaultColorChanged = Signal()
    secondaryColorChanged = Signal()
    endColorChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__radius = 0
        self.__defaultColor = QColor()
        self.__secondaryColor = QColor()
        self.__endColor = QColor()
        self.__borderWidth = 0
        self.radiusChanged.connect(lambda: self.update())
        self.borderWidthChanged.connect(lambda: self.update())
        self.defaultColorChanged.connect(lambda: self.update())
        self.secondaryColorChanged.connect(lambda: self.update())
        self.endColorChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(0, 0, self.width(), self.height())
        gradient = QLinearGradient(0, self.height() - 3, 0, self.height())
        gradient.setColorAt(0, self.__defaultColor)
        gradient.setColorAt(1, self.__endColor)
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, self.__radius, self.__radius)
        painter.drawPath(path)
        outerRadius = int((1.0 - self.__borderWidth / self.height()) * self.__radius)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
        painter.setBrush(Qt.GlobalColor.black)
        innerRect = QRectF(self.__borderWidth, self.__borderWidth, self.width() - 2 * self.__borderWidth,
                           self.height() - 2 * self.__borderWidth)
        innerPath = QPainterPath()
        innerPath.addRoundedRect(innerRect, outerRadius, outerRadius)
        painter.drawPath(innerPath)
        painter.restore()

    @Property(QColor, notify=endColorChanged)
    def endColor(self):
        return self.__endColor

    @endColor.setter
    def endColor(self, value):
        if self.__endColor == value:
            return
        self.__endColor = value
        self.endColorChanged.emit()

    @Property(QColor, notify=secondaryColorChanged)
    def secondaryColor(self):
        return self.__secondaryColor

    @secondaryColor.setter
    def secondaryColor(self, value):
        if self.__secondaryColor == value:
            return
        self.__secondaryColor = value
        self.secondaryColorChanged.emit()

    @Property(QColor, notify=defaultColorChanged)
    def defaultColor(self):
        return self.__defaultColor

    @defaultColor.setter
    def defaultColor(self, value):
        if self.__defaultColor == value:
            return
        self.__defaultColor = value
        self.defaultColorChanged.emit()

    @Property(int, notify=borderWidthChanged)
    def borderWidth(self):
        return self.__borderWidth

    @borderWidth.setter
    def borderWidth(self, value):
        if self.__borderWidth == value:
            return
        self.__borderWidth = value
        self.borderWidthChanged.emit()

    @Property(int, notify=radiusChanged)
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        self.__radius = value
        self.radiusChanged.emit()
