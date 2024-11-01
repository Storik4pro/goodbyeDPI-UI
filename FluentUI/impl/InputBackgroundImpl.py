from PySide6.QtCore import Signal, Property, QRectF, QPointF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, Qt, QLinearGradient
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class InputBackgroundImpl(QQuickPaintedItem):
    targetActiveFocusChanged = Signal()
    radiusChanged = Signal()
    offsetYChanged = Signal()
    endColorChanged = Signal()
    defaultColorChanged = Signal()
    borderWidthChanged = Signal()
    gradientHeightChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__targetActiveFocus = False
        self.__radius = 0
        self.__offsetY = 0
        self.__endColor = QColor()
        self.__defaultColor = QColor()
        self.__borderWidth = 0
        self.__gradientHeight = 0
        self.targetActiveFocusChanged.connect(lambda: self.update())
        self.radiusChanged.connect(lambda: self.update())
        self.offsetYChanged.connect(lambda: self.update())
        self.endColorChanged.connect(lambda: self.update())
        self.defaultColorChanged.connect(lambda: self.update())
        self.borderWidthChanged.connect(lambda: self.update())
        self.gradientHeightChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(0, 0, self.width(), self.height())
        gradient = QLinearGradient(0, self.height() - self.__gradientHeight, 0, self.height())
        gradient.setColorAt(0, self.__defaultColor)
        if self.__targetActiveFocus:
            gradient.setColorAt(0.01, self.__endColor)
        gradient.setColorAt(1, self.__endColor)
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, self.__radius, self.__radius)
        painter.drawPath(path)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
        painter.setBrush(Qt.GlobalColor.black)
        outerRadius = int((1.0 - self.__borderWidth / self.height()) * self.__radius)
        innerRect = QRectF(self.__borderWidth, self.__borderWidth, self.width() - 2 * self.__borderWidth,
                           self.height() - 2 * self.__borderWidth - self.__offsetY)
        innerPath = QPainterPath()
        innerPath.addRoundedRect(innerRect, outerRadius, outerRadius)
        painter.drawPath(innerPath)
        painter.restore()

    @Property(int, notify=gradientHeightChanged)
    def gradientHeight(self):
        return self.__gradientHeight

    @gradientHeight.setter
    def gradientHeight(self, value):
        if self.__gradientHeight == value:
            return
        self.__gradientHeight = value
        self.gradientHeightChanged.emit()

    @Property(int, notify=borderWidthChanged)
    def borderWidth(self):
        return self.__borderWidth

    @borderWidth.setter
    def borderWidth(self, value):
        if self.__borderWidth == value:
            return
        self.__borderWidth = value
        self.borderWidthChanged.emit()

    @Property(QColor, notify=defaultColorChanged)
    def defaultColor(self):
        return self.__defaultColor

    @defaultColor.setter
    def defaultColor(self, value):
        if self.__defaultColor == value:
            return
        self.__defaultColor = value
        self.defaultColorChanged.emit()

    @Property(QColor, notify=endColorChanged)
    def endColor(self):
        return self.__endColor

    @endColor.setter
    def endColor(self, value):
        if self.__endColor == value:
            return
        self.__endColor = value
        self.endColorChanged.emit()

    @Property(int, notify=offsetYChanged)
    def offsetY(self):
        return self.__offsetY

    @offsetY.setter
    def offsetY(self, value):
        if self.__offsetY == value:
            return
        self.__offsetY = value
        self.offsetYChanged.emit()

    @Property(bool, notify=targetActiveFocusChanged)
    def targetActiveFocus(self):
        return self.__targetActiveFocus

    @targetActiveFocus.setter
    def targetActiveFocus(self, value):
        if self.__targetActiveFocus == value:
            return
        self.__targetActiveFocus = value
        self.targetActiveFocusChanged.emit()

    @Property(int, notify=radiusChanged)
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if self.__radius == value:
            return
        self.__radius = value
        self.radiusChanged.emit()
