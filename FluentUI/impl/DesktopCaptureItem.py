from PySide6.QtCore import Signal, Property, QPoint, Slot, Qt
from PySide6.QtGui import QPainter, QImage, QColor
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickPaintedItem

from FluentUI.impl.Tools import Tools

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class DesktopCaptureItem(QQuickPaintedItem):
    desktopChanged = Signal()
    targetChanged = Signal()
    positionChanged = Signal()
    colorChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)
        self.setAcceptHoverEvents(True)
        self.__desktop = QImage()
        self.__target = QImage()
        self.__position = QPoint()
        self.__color = QColor()

    def paint(self, painter: QPainter):
        painter.save()
        painter.drawImage(0, 0, self.__desktop)
        painter.restore()

    def hoverMoveEvent(self, event):
        self.__updateTarget(event.position())

    def hoverEnterEvent(self, event):
        self.__updateTarget(event.position())

    def __updateTarget(self, point):
        self.position = point.toPoint()
        x = point.x() - 20
        y = point.y() - 20
        width = 40
        height = 40
        ratio = self.window().devicePixelRatio()
        self.target = self.__desktop.copy(int(x * ratio), int(y * ratio), int(width * ratio), int(height * ratio))
        color = self.__target.pixelColor(int(20 * ratio), int(20 * ratio))
        self.color = color

    @Slot()
    def capture(self):
        self.desktop = Tools().captureDesktop()
        self.update()

    @Property(QColor, notify=colorChanged)
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if self.__color == value:
            return
        self.__color = value
        self.colorChanged.emit()

    @Property(QPoint, notify=positionChanged)
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        if self.__position == value:
            return
        self.__position = value
        self.positionChanged.emit()

    @Property(QImage, notify=targetChanged)
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if self.__target == value:
            return
        self.__target = value
        self.targetChanged.emit()

    @Property(QImage, notify=desktopChanged)
    def desktop(self):
        return self.__desktop

    @desktop.setter
    def desktop(self, value):
        if self.__desktop == value:
            return
        self.__desktop = value
        self.desktopChanged.emit()
