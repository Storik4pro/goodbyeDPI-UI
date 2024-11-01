import QtQuick
import QtQuick.Controls
import FluentUI.Controls
import GoodbyeDPI_UI

Starter {
    id: starter
    appId: "GoodbyeDPI UI"
    singleton: true
    windowIcon: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/logo.png"
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
    
    function test(){
        console.log("test");
    }
    
    Component.onCompleted: {
        Global.starter = starter
        Theme.darkMode = backend.getValue('APPEARANCE_MODE', 'mode') == 'dark' ? 1 : 0
        if (!backend.getBool('APPEARANCE_MODE', 'animations')){
            Theme.fasterAnimationDuration = 0
            Theme.fastAnimationDuration = 0
            Theme.mediumAnimationDuration = 0
            Theme.slowAnimationDuration = 0
        }
        WindowRouter.routes = {
            "/": resolvedUrl("res/qml/window/MainWindow.qml"),
            "/pseudoconsole": resolvedUrl("res/qml/window/PseudoConsoleWindow.qml"),
            "/page": resolvedUrl("res/qml/window/PageWindow.qml"),
            "/goodcheck": resolvedUrl("res/qml/window/GoodCheckWindow.qml"),
            "/quickstart": resolvedUrl("res/qml/window/AfterUpdateWindow.qml"),
        }
        if (appArguments.indexOf("--after-update") !== -1) {
            WindowRouter.go("/quickstart")
        } else {
            WindowRouter.go("/")
        }
        
    }
}
