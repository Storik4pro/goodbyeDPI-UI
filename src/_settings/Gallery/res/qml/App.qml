import QtQuick
import QtQuick.Controls
import FluentUI.Controls
import Gallery

Starter {
    id: starter
    appId: "GoodbyeDPI UI"
    singleton: true
    windowIcon: "qrc:/qt/qml/Gallery/res/image/logo.png"
    onActiveApplicationChanged:
        (args)=> {
            WindowRouter.go("/",{type:0,args:args})
        }
    Connections{
        target: Theme
        function onDarkModeChanged(){
            SettingsHelper.saveDarkMode(Theme.darkMode)
        }
    }
    Component.onCompleted: {
        Global.starter = starter
        Theme.darkMode = SettingsHelper.getDarkMode()
        if (!backend.getBool('APPEARANCE_MODE', 'animations')){
            Theme.fasterAnimationDuration = 0
            Theme.fastAnimationDuration = 0
            Theme.mediumAnimationDuration = 0
            Theme.slowAnimationDuration = 0
        }
        WindowRouter.routes = {
            "/": resolvedUrl("res/qml/window/MainWindow.qml"),
        }
        WindowRouter.go("/")
    }
}
