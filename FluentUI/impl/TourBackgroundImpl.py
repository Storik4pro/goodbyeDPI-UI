from PySide6.QtCore import Signal, Property, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, Qt
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


def drawRoundedRect(painter, rect, radius):
    path = QPainterPath()
    path.moveTo(rect.bottomRight() - QPointF(0, radius))
    path.lineTo(rect.topRight() + QPointF(0, radius))
    path.arcTo(QRectF(QPointF(rect.topRight() - QPointF(radius * 2, 0)), QSize(radius * 2, radius * 2)), 0, 90)
    path.lineTo(rect.topLeft() + QPointF(radius, 0))
    path.arcTo(QRectF(QPointF(rect.topLeft()), QSize(radius * 2, radius * 2)), 90, 90)
    path.lineTo(rect.bottomLeft() - QPointF(0, radius))
    path.arcTo(QRectF(QPointF(rect.bottomLeft() - QPointF(0, radius * 2)), QSize(radius * 2, radius * 2)), 180, 90)
    path.lineTo(rect.bottomRight() - QPointF(radius, 0))
    path.arcTo(QRectF(QPointF(rect.bottomRight() - QPointF(radius * 2, radius * 2)), QSize(radius * 2, radius * 2)),
               270, 90)
    painter.fillPath(path, Qt.GlobalColor.black)


@QmlElement
class TourBackgroundImpl(QQuickPaintedItem):
    targetXChanged = Signal()
    targetYChanged = Signal()
    targetWidthChanged = Signal()
    targetHeightChanged = Signal()
    colorChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__targetX = 0
        self.__targetY = 0
        self.__targetWidth = 0
        self.__targetHeight = 0
        self.__color = QColor(0, 0, 0, int(0.3 * 255))
        self.targetXChanged.connect(lambda: self.update())
        self.targetYChanged.connect(lambda: self.update())
        self.targetWidthChanged.connect(lambda: self.update())
        self.targetHeightChanged.connect(lambda: self.update())
        self.colorChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.boundingRect(), self.__color)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        targetRect = QRectF(self.__targetX, self.__targetY, self.__targetWidth, self.__targetHeight)
        drawRoundedRect(painter, targetRect, 4)
        painter.restore()

    @Property(QColor, notify=colorChanged)
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if self.__color == value:
            return
        self.__color = value
        self.colorChanged.emit()

    @Property(int, notify=targetHeightChanged)
    def targetHeight(self):
        return self.__targetHeight

    @targetHeight.setter
    def targetHeight(self, value):
        if self.__targetHeight == value:
            return
        self.__targetHeight = value
        self.targetHeightChanged.emit()

    @Property(int, notify=targetWidthChanged)
    def targetWidth(self):
        return self.__targetWidth

    @targetWidth.setter
    def targetWidth(self, value):
        if self.__targetWidth == value:
            return
        self.__targetWidth = value
        self.targetWidthChanged.emit()

    @Property(int, notify=targetYChanged)
    def targetY(self):
        return self.__targetY

    @targetY.setter
    def targetY(self, value):
        if self.__targetY == value:
            return
        self.__targetY = value
        self.targetYChanged.emit()

    @Property(int, notify=targetXChanged)
    def targetX(self):
        return self.__targetX

    @targetX.setter
    def targetX(self, value):
        if self.__targetX == value:
            return
        self.__targetX = value
        self.targetXChanged.emit()
