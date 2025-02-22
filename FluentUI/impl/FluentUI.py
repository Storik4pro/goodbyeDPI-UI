from enum import IntFlag

from PySide6.QtCore import (
    QFlag,
    QObject,
    Signal,
    Property,
    QByteArray,
    QFile,
    QSettings,
)
from PySide6.QtGui import QColor
from PySide6.QtQml import QmlAttached, QmlElement, QmlAnonymous, QJSValue
import os

QML_IMPORT_NAME = "FluentUI.Controls"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class GlobalConfig:
    def __init__(self):
        self.radius = 4
        self.highlightMoveDuration = 167
        self.primaryColor = None
        self.textColor = QColor(255, 255, 255, 255)
        self.minimumHeight = 400


FluentUI_config = None


def resolveSetting(env, settings, name):
    value = QByteArray(os.getenv(env))
    if not value and settings:
        value = QByteArray(settings.value(name))
    return value


def getSettings(group):
    file_path = os.getenv("QT_QUICK_CONTROLS_CONF")
    if file_path and QFile.exists(file_path):
        settings = QSettings(file_path, QSettings.Format.IniFormat)
        if group:
            settings.beginGroup(group)
        return settings
    return None


def initGlobalConfig():
    global FluentUI_config
    FluentUI_config = GlobalConfig()
    settings = getSettings("FluentUI")
    radius_value = resolveSetting(
        "QT_QUICK_CONTROLS_FLUENTUI_RADIUS", settings, "Radius"
    )
    if radius_value:
        FluentUI_config.radius = int(radius_value.toStdString())
    primary_color_value = resolveSetting(
        "QT_QUICK_CONTROLS_FLUENTUI_PRIMARYCOLOR", settings, "PrimaryColor"
    )
    if primary_color_value:
        FluentUI_config.primaryColor = primary_color_value.toStdString()
    highlight_move_value = resolveSetting(
        "QT_QUICK_CONTROLS_FLUENTUI_HIGHLIGHTMOVE", settings, "HighlightMove"
    )
    if highlight_move_value:
        FluentUI_config.highlightMoveDuration = int(highlight_move_value.toStdString())
    min_height_value = resolveSetting(
        "QT_QUICK_CONTROLS_FLUENTUI_MINIMUMHEIGHT", settings, "MinimumHeight"
    )
    if min_height_value:
        FluentUI_config.minimumHeight = int(min_height_value.toStdString())


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

    def __init__(self, config: GlobalConfig, parent=None):
        super().__init__(parent)
        self.__radius = config.radius
        self.__highlightMoveDuration = config.highlightMoveDuration
        self.__minimumHeight = config.minimumHeight
        self.__textColor = config.textColor
        self.__primaryColor = config.primaryColor

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
        global FluentUI_config
        if FluentUI_config is None:
            initGlobalConfig()
        return FluentStyleAttached(FluentUI_config, o)
