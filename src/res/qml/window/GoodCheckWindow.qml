import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

FramelessWindow {
    property var argument
    property string execut: process.get_executable()
    id: window
    title: backend.get_element_loc("goodcheck_title")
    width: 800
    height: 500
    minimumWidth: 800
    minimumHeight: 500
    visible: true
    launchMode: WindowType.SingleInstance
    windowEffect: Global.windowEffect
    fitsAppBarWindows: true
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
    onCloseListener: function(event){
        WindowRouter.removeWindow(window)
        event.accepted = false
    }
    initialItem: resolvedUrl("res/qml/screen/GoodCheckScreen.qml")

    
    

}