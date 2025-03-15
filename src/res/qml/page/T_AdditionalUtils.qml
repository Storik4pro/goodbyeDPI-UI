import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

StackPage {
    router: PageRouter{
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_AdditionalUtilsPage.qml"),singleton:true},
            "/goodcheck": {url: resolvedUrl("res/qml/page/T_AdditionalUtilsGoodCheckPage.qml"),}
        }
    }
    Component.onCompleted: {
        router.go("/")
        if (context) {
            if (context.argument.info === 'GoodCheck'){
                router.go('/goodcheck',{info:"results"})
            } else if (context.argument.info === 'GoodCheck:startNEW') {
                router.go('/goodcheck')
            }
        }
    }
}