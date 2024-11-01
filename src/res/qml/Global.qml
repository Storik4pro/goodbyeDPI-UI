pragma Singleton

import QtQuick
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl

QtObject {
    id: control
    property var starter
    property int displayMode: NavigationViewType.Auto
    property int windowEffect: backend.check_mica() && backend.getBool('APPEARANCE_MODE', 'use_mica') ? WindowEffectType.Mica : WindowEffectType.Normal
}
