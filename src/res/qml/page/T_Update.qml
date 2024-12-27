import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_UpdatePage.qml"),singleton:true},
            "/developerSettings": {url: resolvedUrl("res/qml/page/T_UpdateDeveloperSettingsPage.qml")}
        }
    }
    Component.onCompleted: {
        router.go("/")
    }
}