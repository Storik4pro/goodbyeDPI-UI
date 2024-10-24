import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery


ScrollablePage {
    title:backend.get_element_loc("system")
    id:page
    header:Item{}
    ColumnLayout {
        width: parent.width
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter
        Label {
            text: backend.get_element_loc("base")
            font: Typography.bodyStrong
        }
        Button {
            Layout.minimumHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter

            RowLayout {
                anchors.fill: parent
                anchors{
                    leftMargin: 20
                    rightMargin: 20
                }
                spacing: 10

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Label {
                        Layout.fillWidth: true
                        text: backend.get_element_loc("components")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.body
                        wrapMode: Text.Wrap
                    }
                    Label {
                        Layout.fillWidth: true
                        text: backend.get_element_loc("components_tip")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.caption
                        color: "#c0c0c0"
                        wrapMode: Text.Wrap
                    }
                }

                IconButton {
                    id: btn_icon
                    width: 30
                    height: 30
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    Icon {
                        anchors.centerIn: parent
                        source: FluentIcons.graph_ChevronRight
                        width: 15
                        height: 15
                    }
                    onClicked: {
                        context.router.go("/components")
                    }
                }
            }

            onClicked: {
                context.router.go("/components")
            }
        }
        Expander {
            id:exp
            expanded:true 
            Layout.fillWidth: true 
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter 

            header: Label {
                text: backend.get_element_loc("notifications")
                horizontalAlignment: Qt.AlignVCenter
                font: Typography.body  
            }
            subHeader: Label {
                text: backend.get_element_loc("notifications_tip")
                horizontalAlignment: Qt.AlignVCenter
                font: Typography.caption
                color: "#c0c0c0"
                width:exp.width - 30 - 20 - 50
                
                wrapMode:Text.Wrap
            }
            content: ColumnLayout{
                spacing:2
                width: parent.width 
                ColumnLayout {
                    spacing: 5
                    anchors {
                        verticalCenter: parent.verticalCenter
                        left: parent.left
                        leftMargin: 15
                    }

                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.bottomMargin: 5
                    }

                    RowLayout {
                        spacing: 10
                        CheckBox {
                            id:chkb1
                            topPadding: 10
                            text: backend.get_element_loc("notifications_suc_on")
                            checked: backend.getBool("NOTIFICATIONS", 'proc_on')
                            Layout.alignment: Qt.AlignVCenter
                            onClicked: {
                                backend.toggleBool("NOTIFICATIONS", 'proc_on', chkb1.checked)
                            }
                        }
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.leftMargin: -15
                        Layout.topMargin: 5
                        Layout.bottomMargin: 5
                        height: 3
                        color: Qt.rgba(0.0, 0.0, 0.0, 0.3)
                        opacity: 0.3
                    }
                    RowLayout {
                        spacing: 10
                        CheckBox {
                            id:chkb2
                            bottomPadding: 10
                            text: backend.get_element_loc("notifications_hide_to_tray")
                            checked: backend.getBool("NOTIFICATIONS", 'hide_in_tray')
                            Layout.alignment: Qt.AlignVCenter
                            onClicked: {
                                backend.toggleBool("NOTIFICATIONS", 'hide_in_tray', chkb2.checked)
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.topMargin: 5
                    }
                }

            }
            _height: 68
            
        }

        Label {
            text: backend.get_element_loc("autorun")
            font: Typography.bodyStrong
            Layout.topMargin: 15
        }
        Rectangle {
            Layout.preferredHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius:6

            ColumnLayout {
                spacing: 2
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: 20
                }

                Label {
                    text: backend.get_element_loc("autorun_tip")
                    horizontalAlignment: Qt.AlignHCenter
                    font: Typography.body
                }
            }

            Item {
                Layout.fillHeight: true
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 15
                }

                Switch {
                    property bool isInitializing: backend.getBool('GLOBAL', 'hide_to_tray') 
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: backend.getBool('GLOBAL', 'autorun')
                    onCheckedChanged: {
                        if (!isInitializing){
                            backend.toggleBool('GLOBAL', 'autorun', checked)
                            if (checked) {
                                backend.add_to_autorun()
                            } else {
                                backend.remove_from_autorun()
                            }
                        }
                        isInitializing = false
                    }
                }
            }
        }

        Label {
            text: backend.get_element_loc("system_q")
            font: Typography.bodyStrong
            Layout.topMargin: 15
        }
        Rectangle {
            Layout.preferredHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius:6

            ColumnLayout {
                spacing: 2
                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: 20
                }

                Label {
                    text: backend.get_element_loc("system_hide_to_tray")
                    horizontalAlignment: Qt.AlignHCenter
                    font: Typography.body
                }
            }

            Item {
                Layout.fillHeight: true
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 15
                }

                Switch {
                    property bool isInitializing: backend.getBool('GLOBAL', 'hide_to_tray') 
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: backend.getBool('GLOBAL', 'hide_to_tray')
                    onCheckedChanged: {
                        if (!isInitializing){
                            backend.toggleBool('GLOBAL', 'hide_to_tray', checked)
                        }
                        isInitializing = false
                    }
                }
            }
        }
    }
    
}

