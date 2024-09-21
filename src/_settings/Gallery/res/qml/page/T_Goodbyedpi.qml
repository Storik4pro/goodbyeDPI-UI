import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_GoodbyedpiSettings.qml"),singleton:true},
            "/goodbyedpiAdvanced":  resolvedUrl("res/qml/page/T_GoodbyedpiAdvanced.qml"),
        }
    }
    Component.onCompleted: {
        router.go(backend.getBool('GLOBAL', 'use_advanced_mode') ? "/goodbyedpiAdvanced":'/')
    }
}