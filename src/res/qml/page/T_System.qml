import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_SystemPage.qml"),singleton:true},
            "/components": resolvedUrl("res/qml/page/T_SystemComponentsPage.qml"),
        }
    }
    Component.onCompleted: {
        if (context.argument.info === 'Component'){
            router.go('/components')
        } else {
            router.go("/")
        }
    }
}