import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls
import FluentUI.Controls
import GoodbyeDPI_UI

Item {

    property var argument: Window.window.argument
    anchors.fill: parent
    Label{
        text: {
            if(argument){
                return JSON.stringify(argument)
            }
            return ""
        }
        anchors.centerIn: parent
        TapHandler{
            onTapped: {
                WindowRouter.go("/")
            }
        }
    }

}