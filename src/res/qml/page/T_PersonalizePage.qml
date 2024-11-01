import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    title: backend.get_element_loc("personalize")
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
                    text: backend.get_element_loc("language")
                    horizontalAlignment: Qt.AlignHCenter
                    font: Typography.body
                }
            }

            Item {
                Layout.fillHeight: true
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 20
                }

                ComboBox {
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    model: [
                        "Russian",
                        "English",
                    ]
                    currentIndex: backend.getValue('GLOBAL', 'language') == 'RU' ? 0 : 1
                    onActivated: {
                        let selectedValue = model[currentIndex];
                        backend.changeValue('GLOBAL', 'language', currentIndex == 0 ? 'RU':'EN');
                        backend.changeLanguage();
                    }

                    focus: false
                    focusPolicy: Qt.NoFocus
                }
            }
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
                    text: backend.get_element_loc("mode")
                    horizontalAlignment: Qt.AlignHCenter
                    font: Typography.body
                }
            }

            Item {
                Layout.fillHeight: true
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 20
                }

                ComboBox {
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    model: [
                        backend.get_element_loc("mode_d"),
                        backend.get_element_loc("mode_l"),
                    ]
                    currentIndex: backend.getValue('APPEARANCE_MODE', 'mode') == 'dark' ? 0 : 1
                    onActivated: {
                        let selectedValue = model[currentIndex];
                        backend.changeValue('APPEARANCE_MODE', 'mode', currentIndex == 0 ? 'dark':'light');
                        Theme.darkMode = currentIndex == 0 ? FluentUI.Dark : FluentUI.Light;
                    }

                    focus: false
                    focusPolicy: Qt.NoFocus
                }
            }
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
                    text: backend.get_element_loc("mica")
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
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: backend.check_mica() ? backend.getBool('APPEARANCE_MODE', 'use_mica'):false
                    enabled: backend.check_mica()
                    onClicked: {
                        backend.toggleBool('APPEARANCE_MODE', 'use_mica', checked)
                        if (checked) {
                            Global.windowEffect = WindowEffectType.Mica;
                        } else {
                            Global.windowEffect = WindowEffectType.Normal;
                        }
                    }
                }
            }

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
                    text: backend.get_element_loc("animations")
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
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: backend.getBool('APPEARANCE_MODE', 'animations')
                    onClicked: {
                        backend.toggleBool('APPEARANCE_MODE', 'animations', checked)
                        if (!checked) {
                            Theme.fasterAnimationDuration = 0
                            Theme.fastAnimationDuration = 0
                            Theme.mediumAnimationDuration = 0
                            Theme.slowAnimationDuration = 0
                        } else {
                            Theme.fasterAnimationDuration = 83
                            Theme.fastAnimationDuration = 167
                            Theme.mediumAnimationDuration = 250
                            Theme.slowAnimationDuration = 358
                        }
                    }
                }
            }

        }

        Label {
            text: backend.get_element_loc("p_advanced")
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

            RowLayout {
                anchors.fill: parent
                anchors.margins: 0
                spacing: 10
                anchors{
                    rightMargin: 15
                    leftMargin: 20
                }
                
                Label {
                    Layout.fillWidth: true
                    text: backend.get_element_loc("p_advanced_GDPI")
                    horizontalAlignment: Text.AlignLeft
                    font: Typography.body
                    wrapMode: Text.Wrap
                }

                Switch {
                    Layout.preferredWidth: implicitWidth
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: backend.getBool('GLOBAL', 'use_advanced_mode')
                    onClicked: {
                        backend.toggleBool('GLOBAL', 'use_advanced_mode', checked)
                        process.update_preset()
                    }
                }
            }

        }
        

    }
    Component.onCompleted:{
        if (window.title !== title){
            multiWindow.close_window(title);
        }
    }
    Connections {
        target:multiWindow
        function onMulti_window_init(id) {
            if (id === title && window.title !== title) {
                page_router.go("/")
            }
        }
    }
}