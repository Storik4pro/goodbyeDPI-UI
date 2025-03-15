import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_ProxySetupPage.qml")},
            "/proxyBasic": {url: resolvedUrl("res/qml/page/T_ProxyBasicPage.qml")},
            "/proxyUDP": {url: resolvedUrl("res/qml/page/T_ProxyUDPPage.qml")},
        }
    }
    Component.onCompleted: {
        router.go('/')
    }
}