from PySide6.QtCore import (Slot, Signal, Property, QPoint, QPropertyAnimation, QPointF, Qt, QSize, QEasingCurve,
                            SIGNAL, SLOT)
from PySide6.QtGui import QPainter, QImage, QPainterPath
from PySide6.QtQuick import QQuickPaintedItem, QQuickItem
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "Gallery"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class CircularReveal(QQuickPaintedItem):
    radiusChanged = Signal()
    imageChanged = Signal()
    animationFinished = Signal()
    targetChanged = Signal()

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)
        self.__target = None
        self.__radius: int = 0
        self.__source = QImage()
        self.__center = QPoint()
        self.__grabResult = None
        self.__dark = False
        self.setVisible(False)
        self.__anim = QPropertyAnimation(self, b"radius", self)
        self.__anim.setDuration(358)
        self.__anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.connect(self.__anim, SIGNAL("finished()"), self, SLOT("on_anima_finish()"))
        self.radiusChanged.connect(lambda: self.update())
        self.destroyed.connect(lambda: self.release())

    def release(self):
        self.__anim.deleteLater()
        del self.__grabResult
        del self.__source

    def on_anima_finish(self):
        self.update()
        self.setVisible(False)
        self.animationFinished.emit()

    @Property(int, notify=radiusChanged)
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if self.__radius == value:
            return
        self.__radius = value
        self.radiusChanged.emit()

    @Property(QQuickItem, notify=targetChanged)
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if self.__target == value:
            return
        self.__target = value
        self.targetChanged.emit()

    def paint(self, painter: QPainter):
        if self.__source is None:
            return
        painter.save()
        painter.drawImage(self.boundingRect(), self.__source)
        path = QPainterPath()
        path.moveTo(self.__center.x(), self.__center.y())
        path.addEllipse(QPointF(self.__center.x(), self.__center.y()), self.__radius, self.__radius)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        rect_path = QPainterPath()
        rect_path.addRect(0, 0, self.width(), self.height())
        if self.__dark:
            path = rect_path.subtracted(path)
        painter.fillPath(path, Qt.GlobalColor.black)
        painter.restore()

    @Slot()
    def handle_grab_result(self):
        self.__grabResult.data().image().swap(self.__source)
        self.update()
        self.setVisible(True)
        self.imageChanged.emit()
        self.__anim.start()

    @Slot(int, int, QPoint, int, bool)
    def start(self, w: int, h: int, center: QPoint, radius: int, dark: bool):
        if dark:
            self.__anim.setStartValue(radius)
            self.__anim.setEndValue(0)
        else:
            self.__anim.setStartValue(0)
            self.__anim.setEndValue(radius)
        self.__center = center
        self.__dark = dark
        self.__grabResult = self.__target.grabToImage(QSize(w, h))
        self.__grabResult.data().ready.connect(self.handle_grab_result)
