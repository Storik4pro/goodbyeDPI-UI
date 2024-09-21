from enum import IntFlag

from PySide6.QtCore import QFlag, QObject, Signal, Property
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlAttached, QmlElement, QmlAnonymous,QJSValue

QML_IMPORT_NAME = "FluentUI.Controls"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlAnonymous
class FluentStyleAttached(QObject):
    textColorChanged = Signal()
    highlightMoveDurationChanged = Signal()
    radiusChanged = Signal()
    minimumHeightChanged = Signal()
    primaryColorChanged = Signal()

    @Property(QJSValue, notify=primaryColorChanged)
    def primaryColor(self):
        return self.__primaryColor

    @primaryColor.setter
    def primaryColor(self, value):
        if self.__primaryColor == value:
                return
        self.__primaryColor = value
        self.primaryColorChanged.emit()


    def __init__(self, parent=None):
        super().__init__(parent)
        self.__radius = 4
        self.__highlightMoveDuration = 167
        self.__minimumHeight = 400
        self.__textColor = QColor(255, 255, 255, 255)
        self.__primaryColor = None

    @Property(int, notify=minimumHeightChanged)
    def minimumHeight(self):
        return self.__minimumHeight

    @minimumHeight.setter
    def minimumHeight(self, value):
        if self.__minimumHeight == value:
            return
        self.__minimumHeight = value
        self.minimumHeightChanged.emit()

    @Property(int, notify=radiusChanged)
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if self.__radius == value:
            return
        self.__radius = value
        self.radiusChanged.emit()

    @Property(int, notify=highlightMoveDurationChanged)
    def highlightMoveDuration(self):
        return self.__highlightMoveDuration

    @highlightMoveDuration.setter
    def highlightMoveDuration(self, value):
        if self.__highlightMoveDuration == value:
            return
        self.__highlightMoveDuration = value
        self.highlightMoveDurationChanged.emit()

    @Property(QColor, notify=textColorChanged)
    def textColor(self):
        return self.__textColor

    @textColor.setter
    def textColor(self, value):
        if self.__textColor == value:
            return
        self.__textColor = value
        self.textColorChanged.emit()


@QmlElement
@QmlAttached(FluentStyleAttached)
class FluentUI(QObject):
    class DarkMode(IntFlag):
        Light = 0x0000
        Dark = 0x0001
        System = 0x0002

    QFlag(DarkMode)

    def __init__(self, parent=None):
        super().__init__(parent)

    @staticmethod
    def qmlAttachedProperties(self, o):
        # noinspection PyCallingNonCallable
        return FluentStyleAttached(o)
