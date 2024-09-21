from enum import IntFlag

from PySide6.QtCore import QObject, QFlag


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


class WindowType(QObject):
    class LaunchMode(IntFlag):
        Standard = 0x0000
        SingleTask = 0x0001
        SingleInstance = 0x0002

    QFlag(LaunchMode)


class WindowEffectType(QObject):
    class EffectMode(IntFlag):
        Normal = 0x0000
        Mica = 0x0001
        Acrylic = 0x0002

    QFlag(EffectMode)


class NavigationViewType(QObject):
    class DisplayMode(IntFlag):
        Open = 0x0000
        Compact = 0x0001
        Minimal = 0x0002
        Auto = 0x0004
        Top = 0x0008

    QFlag(DisplayMode)


class TimePickerType(QObject):
    class HourFormat(IntFlag):
        H = 0x0000
        HH = 0x0001

    QFlag(HourFormat)


class DatePickerType(QObject):
    class DatePickerField(IntFlag):
        Day = 0x0000
        Month = 0x0001
        Year = 0x0002

    QFlag(DatePickerField)


class NumberBoxType(QObject):
    class PlacementMode(IntFlag):
        Inline = 0x0000
        Compact = 0x0001

    QFlag(PlacementMode)


class InfoBarType(QObject):
    class Severity(IntFlag):
        Info = 0x0000
        Warning = 0x0001
        Error = 0x0002
        Success = 0x0004

    QFlag(Severity)
