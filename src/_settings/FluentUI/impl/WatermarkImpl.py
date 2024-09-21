from PySide6.QtCore import Signal, Property, QRectF, QPoint, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, Qt, QLinearGradient, QFont, QFontMetricsF
from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class WatermarkImpl(QQuickPaintedItem):
    textChanged = Signal()
    gapChanged = Signal()
    offsetChanged = Signal()
    textColorChanged = Signal()
    rotateChanged = Signal()
    textSizeChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__text = ""
        self.__gap = QPoint(100, 100)
        self.__offset = QPoint(int(self.__gap.x() / 2), int(self.__gap.y() / 2))
        self.__textColor = QColor(222, 222, 222, 222)
        self.__rotate = 22
        self.__textSize = 16
        self.textColorChanged.connect(lambda: self.update())
        self.gapChanged.connect(lambda: self.update())
        self.offsetChanged.connect(lambda: self.update())
        self.textChanged.connect(lambda: self.update())
        self.rotateChanged.connect(lambda: self.update())
        self.textSizeChanged.connect(lambda: self.update())

    def paint(self, painter: QPainter):
        font = QFont()
        font.setPixelSize(self.__textSize)
        painter.setFont(font)
        painter.setPen(self.__textColor)
        fontMetrics = QFontMetricsF(font)
        fontWidth = fontMetrics.horizontalAdvance(self.__text)
        fontHeight = fontMetrics.height()
        stepX = fontWidth + self.__gap.x()
        stepY = fontHeight + self.__gap.y()
        rowCount = int(self.width() / stepX) + 1
        colCount = int(self.height() / stepY) + 1
        for r in range(rowCount):
            for c in range(colCount):
                centerX = stepX * r + self.__offset.x() + fontWidth / 2.0
                centerY = stepY * c + self.__offset.y() + fontHeight / 2.0
                painter.save()
                painter.translate(centerX, centerY)
                painter.rotate(self.__rotate)
                painter.drawText(QRectF(-fontWidth / 2.0, -fontHeight / 2.0, fontWidth, fontHeight), self.__text)
                painter.restore()

    @Property(int, notify=textSizeChanged)
    def textSize(self):
        return self.__textSize

    @textSize.setter
    def textSize(self, value):
        if self.__textSize == value:
            return
        self.__textSize = value
        self.textSizeChanged.emit()

    @Property(int, notify=rotateChanged)
    def rotate(self):
        return self.__rotate

    @rotate.setter
    def rotate(self, value):
        if self.__rotate == value:
            return
        self.__rotate = value
        self.rotateChanged.emit()

    @Property(QColor, notify=textColorChanged)
    def textColor(self):
        return self.__textColor

    @textColor.setter
    def textColor(self, value):
        if self.__textColor == value:
            return
        self.__textColor = value
        self.textColorChanged.emit()

    @Property(QPoint, notify=offsetChanged)
    def offset(self):
        return self.__offset

    @offset.setter
    def offset(self, value):
        if self.__offset == value:
            return
        self.__offset = value
        self.offsetChanged.emit()

    @Property(QPoint, notify=gapChanged)
    def gap(self):
        return self.__gap

    @gap.setter
    def gap(self, value):
        if self.__gap == value:
            return
        self.__gap = value
        self.gapChanged.emit()

    @Property(str, notify=textChanged)
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        if self.__text == value:
            return
        self.__text = value
        self.textChanged.emit()
