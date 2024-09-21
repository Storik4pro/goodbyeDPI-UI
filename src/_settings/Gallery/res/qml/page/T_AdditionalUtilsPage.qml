import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery

ScrollablePage {
    title: backend.get_element_loc('additional')
    id:page
    header:Item{}
    ColumnLayout {
        width: parent.width
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter

        Button{
            Layout.preferredHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            ColumnLayout{
                spacing: 2
                anchors{
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: 20
                }
                Label{
                    text: backend.get_element_loc('see_output')
                    horizontalAlignment: Qt.AlignHCenter
                    font: Typography.body
                }
                Label {
                    text: backend.get_element_loc('see_output_tip')
                    horizontalAlignment: Qt.AlignHCenter
                    font: Typography.caption
                    color: "#c0c0c0"
                }
            }
            Item{
                implicitWidth: 50
                Layout.fillHeight: true
                anchors{
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 0
                }
                IconButton{
                    id: btn_icon
                    anchors.centerIn: parent
                    width: 30
                    height: 30
                    Icon{
                        anchors.centerIn: parent
                        source: FluentIcons.graph_OpenInNewWindow
                        width: 15
                        height: 15
                    }
                    onClicked: {
                        backend.open_pseudoconsole()
                    }
                }
            }
            
            onClicked: {
                backend.open_pseudoconsole()
            }
        }
    }
}