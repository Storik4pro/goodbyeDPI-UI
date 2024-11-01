import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_SpoofdpiPage.qml"),singleton:true},
        }
    }
    Component.onCompleted: {
        router.go('/')
    }
}