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
    width: 1000
    height: 800
    minimumWidth: 500
    minimumHeight: 400
    visible: true
    windowEffect: Global.windowEffect
    onInit:
        (arg)=>{
            argument = arg
        }
    onNewInit:
        (arg)=>{
            argument = arg
        }
    initialItem: {
        if(argument){
            return resolvedUrl(argument.url)
        }
        return undefined
    }
    onArgumentChanged: {
        window.title = argument.title
        Qt.callLater(multiWindow.init_window, argument.title)
    }
    onCloseListener: function(event){
        multiWindow.close_window(window.title);
        WindowRouter.removeWindow(window)
        event.accepted = false
    }
    InfoBarManager{
        id: infobar_manager
        target: window.contentItem
        messageMaximumWidth: 380
    }
    Component.onCompleted: {
        Qt.callLater(multiWindow.init_window, argument.url)
    }
    Connections {
        target:multiWindow
        function onMulti_window_close(id) {
            console.log(id, window.title)
            if (id === window.title) {
                WindowRouter.removeWindow(window)
            }
        }
    }
    Connections {
        target:backend
        function onLanguage_change() {
            multiWindow.close_window(window.title);
            WindowRouter.removeWindow(window)
        }
    }
}