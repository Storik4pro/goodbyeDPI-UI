import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery
import Qt.labs.platform as P

FramelessWindow {
    id: window
    property alias infoBarManager: infobar_manager
    property var tourSteps: []
    width: 1424
    height: 744
    minimumWidth: 484
    minimumHeight: 300
    visible: true
    fitsAppBarWindows: true
    launchMode: WindowType.SingleInstance
    windowEffect: Global.windowEffect
    autoDestroy: false
    appBar: AppBar{
        implicitHeight: 48
        windowIcon: Item{}
    }
    initialItem: resolvedUrl("res/qml/screen/MainScreen.qml")
    onNewInit:
        (argument)=>{
            if(argument.type===0){
                dialog_program_already.argsText = argument.args
                dialog_program_already.open()
            }
        }
    onCloseListener: function(event){
        WindowRouter.exit(0)
    }
    
    Component{
        id: comp_reveal
        CircularReveal{
            id: reveal
            target: window.contentItem
            anchors.fill: parent
            onAnimationFinished:{
                loader_reveal.sourceComponent = undefined
            }
            onImageChanged: {
                changeDark()
            }
        }
    }
    InfoBarManager{
        id: infobar_manager
        target: window.contentItem
        messageMaximumWidth: 380
    }
    AutoLoader{
        id:loader_reveal
        anchors.fill: parent
        z: 65535
    }
    function distance(x1,y1,x2,y2){
        return Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    }
    function handleDarkChanged(button){
        if(loader_reveal.sourceComponent){
            return
        }
        loader_reveal.sourceComponent = comp_reveal
        var target = window.contentItem
        var pos = button.mapToItem(target,0,0)
        var centerX = pos.x + button.width/2
        var centerY = pos.y + button.height/2
        var radius = Math.max(distance(centerX,centerY,0,0),distance(centerX,centerY,target.width,0),distance(centerX,centerY,0,target.height),distance(centerX,centerY,target.width,target.height))
        var reveal = loader_reveal.item
        reveal.start(reveal.width*Screen.devicePixelRatio,reveal.height*Screen.devicePixelRatio,Qt.point(centerX,centerY),radius,Theme.dark)
    }
    function changeDark(){
        if(Theme.dark){
            Theme.darkMode = FluentUI.Light
        }else{
            Theme.darkMode = FluentUI.Dark
        }
    }
   
    
}

