import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_ZapretSettings.qml"),singleton:true},
        }
    }
    Component.onCompleted: {
        router.go('/')
    }
}