import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_ByedpiPage.qml"),singleton:true},
        }
    }
    Component.onCompleted: {
        router.go('/')
    }
}