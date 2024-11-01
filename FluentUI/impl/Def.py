from enum import IntFlag

from PySide6.QtCore import QObject, QFlag
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class TabViewType(QObject):
    class TabWidthBehavior(IntFlag):
        Equal = 0x0000
        SizeToContent = 0x0001
        Compact = 0x0002

    QFlag(TabWidthBehavior)

    class CloseButtonVisibility(IntFlag):
        Never = 0x0000
        Always = 0x0001
        OnHover = 0x0002

    QFlag(CloseButtonVisibility)


@QmlElement
class WindowType(QObject):
    class LaunchMode(IntFlag):
        Standard = 0x0000
        SingleTask = 0x0001
        SingleInstance = 0x0002

    QFlag(LaunchMode)


@QmlElement
class WindowEffectType(QObject):
    class EffectMode(IntFlag):
        Normal = 0x0000
        Mica = 0x0001
        Acrylic = 0x0002

    QFlag(EffectMode)


@QmlElement
class NavigationViewType(QObject):
    class DisplayMode(IntFlag):
        Open = 0x0000
        Compact = 0x0001
        Minimal = 0x0002
        Auto = 0x0004
        Top = 0x0008

    QFlag(DisplayMode)


@QmlElement
class TimePickerType(QObject):
    class HourFormat(IntFlag):
        H = 0x0000
        HH = 0x0001

    QFlag(HourFormat)


@QmlElement
class DatePickerType(QObject):
    class DatePickerField(IntFlag):
        Day = 0x0000
        Month = 0x0001
        Year = 0x0002

    QFlag(DatePickerField)


@QmlElement
class NumberBoxType(QObject):
    class PlacementMode(IntFlag):
        Inline = 0x0000
        Compact = 0x0001

    QFlag(PlacementMode)


@QmlElement
class InfoBarType(QObject):
    class Severity(IntFlag):
        Info = 0x0000
        Warning = 0x0001
        Error = 0x0002
        Success = 0x0004

    QFlag(Severity)
