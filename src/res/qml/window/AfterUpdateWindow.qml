import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

FramelessWindow {
    property var argument
    property alias infoBarManager: infobar_manager
    id: window
    fixSize: true
    width: 800
    height: 500
    minimumWidth: 800
    minimumHeight: 500
    visible: true
    windowEffect: Global.windowEffect
    launchMode: WindowType.SingleInstance
    onInit:
        (arg)=>{
            argument = arg
            window.show()
            window.raise()
            window.requestActivate()
        }
    onNewInit:
        (arg)=>{
            argument = arg
            window.show()
            window.raise()
            window.requestActivate()
        }
    initialItem:resolvedUrl("res/qml/screen/AfterUpdateScreen.qml")
    onCloseListener: function(event){
        event.accepted = false
    }
    InfoBarManager{
        id: infobar_manager
        target: window.contentItem
        messageMaximumWidth: 380
    }
    Connections {
        target:updateHelper
        function onUpdateComponentsCompleted() {
            WindowRouter.go("/");
            WindowRouter.removeWindow(window);
        }
    }

}