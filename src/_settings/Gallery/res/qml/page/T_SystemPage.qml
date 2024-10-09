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
            text: backend.get_element_loc("autorun")
            font: Typography.bodyStrong
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
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 6
            Layout.minimumHeight: 68
            Layout.preferredHeight:lbl1.height+lbl2.height+20

            RowLayout {
                id:rwlay
                anchors.fill: parent
                anchors{
                    leftMargin: 20
                    rightMargin: 20
                    topMargin: 10
                    bottomMargin: 10
                }
                spacing: 10

                ColumnLayout {
                    id:clmn
                    Layout.fillWidth: true
                    spacing: 2

                    Label {
                        id:lbl1
                        Layout.fillWidth: true
                        text: backend.get_element_loc("engine")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.body
                        wrapMode: Text.Wrap
                    }

                    Label {
                        id:lbl2
                        Layout.fillWidth: true
                        text: backend.get_element_loc("engine_tip")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.caption
                        color: "#c0c0c0"
                        wrapMode: Text.Wrap
                    }
                }

                ComboBox {
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    Layout.preferredWidth: 300
                    Layout.fillWidth: false
                    model: [
                        backend.get_element_loc("engine_goodbyeDPI"),
                        backend.get_element_loc("engine_zapret")+ " (" + backend.get_element_loc("recommended") + ")",
                    ]
                    currentIndex: backend.getValue('GLOBAL', 'engine') == 'goodbyeDPI' ? 0 : 1
                    onCurrentIndexChanged: {
                        let selectedValue = model[currentIndex];
                        backend.changeValue('GLOBAL', 'engine', currentIndex == 0 ? 'goodbyeDPI':'zapret');
                    }

                    focus: false
                    focusPolicy: Qt.NoFocus
                }
            }
        }

    }
    
}

