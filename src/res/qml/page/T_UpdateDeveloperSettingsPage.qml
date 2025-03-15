import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Dialogs 
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI


ScrollablePage {
    title: backend.get_element_loc("developer_settings")
    id:page
    header:Item{}

    FileDialog {
        id: fileDialog
        title: "Select a .cdpipatch file"
        nameFilters: ["*.cdpipatch"]
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            apply_patch(filePath)
        }
    }

    InfoBarManager {
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }


    ColumnLayout {
        id: base_layout
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10
            ColumnLayout{
                spacing: 0
                Button {
                    Layout.minimumHeight: 68
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    FluentUI.radius:0

                    RowLayout {
                        anchors.fill: parent
                        anchors{
                            leftMargin: 20
                            rightMargin: 20
                        }
                        spacing: 10

                        Icon {
                            source: FluentIcons.graph_Page
                            width: 20
                            height: 20
                            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Label {
                                Layout.fillWidth: true
                                text: backend.get_element_loc("developer_install_local_patch")
                                horizontalAlignment: Text.AlignLeft
                                font: Typography.body
                                wrapMode: Text.Wrap
                            }
                            Label {
                                Layout.fillWidth: true
                                text: backend.get_element_loc("developer_install_local_patch_tip")
                                horizontalAlignment: Text.AlignLeft
                                font: Typography.caption
                                color: "#c0c0c0"
                                wrapMode: Text.Wrap
                            }
                        }

                        Button {
                            id: btn_icon
                            height: 30
                            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                            text: backend.get_element_loc("select_file")
                            onClicked: {
                                fileDialog.open()
                            }
                        }
                    }

                    onClicked: {
                        fileDialog.open()
                    }

                }
                Rectangle {
                    id:rest1
                    Layout.preferredHeight: Math.max(50, infoColumnLayout.implicitHeight + 20)
                    Layout.fillWidth: true
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    color: Theme.res.subtleFillColorTertiary
                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.0)
                    radius: 0
                    visible: false 
                    ColumnLayout{
                        id:infoColumnLayout
                        anchors.verticalCenter: parent.verticalCenter  
                        RowLayout{
                            spacing:10
                            height:20
                            Layout.leftMargin:20
                            ProgressRing {
                                id: progressBar
                                indeterminate: true
                                anchors {
                                    rightMargin: 15
                                    topMargin: 20
                                    bottomMargin: 20
                                }
                                Layout.preferredHeight:30
                                Layout.preferredWidth:30
                                strokeWidth:4
                                visible: false
                            }
                            Icon {
                                id: icon
                                source: FluentIcons.graph_StatusErrorFull
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                visible: true
                            }
                            ColumnLayout{
                                Label{
                                    id:patcherTipTitle
                                    text:backend.get_element_loc('getting_ready')
                                    font: Typography.bodyStrong
                                }
                                CopyableText{
                                    id:patcherTip
                                    Layout.preferredWidth:rest1.width - 130
                                    text:backend.get_element_loc('applying_tip')
                                    font: Typography.body
                                    wrapMode:Text.Wrap
                                }
                                HyperlinkButton {
                                    id:btn
                                    text: backend.get_element_loc("view_requirements")
                                    FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                                    Layout.preferredHeight:15
                                    font: Typography.caption
                                    Layout.preferredWidth:implicitWidth - 15
                                    flat: true
                                    background: Rectangle {
                                        implicitWidth: 100
                                        implicitHeight: 40
                                        color: Theme.accentColor.defaultBrushFor()
                                        opacity: 0.1
                                        visible:btn.hovered
                                        radius:2
                                    }
                                    onClicked:{
                                        patcher.open_requirements()
                                    }
                                }
                            }
                            Button {
                                id: installButton
                                text: backend.get_element_loc("install")
                                height: 30
                                onClicked: {
                                    installPatch()
                                }
                            }

                        }
                    }
                }
            }
            Label{
                text:"Router navigation"
                font: Typography.bodyStrong
            }
            RowLayout {
                Layout.fillWidth: true
                TextField{
                    id:routerText
                    Layout.preferredHeight:30
                    Layout.fillWidth:true
                    placeholderText: "/"
                }
                TextField{
                    id:argText
                    Layout.preferredHeight:30
                    placeholderText: "args"
                }
                Button{
                    icon.name: FluentIcons.graph_Send
                    width: 40
                    Layout.preferredHeight:30
                    icon.width: 20
                    icon.height: 20
                    display: Button.IconOnly
                    onClicked:{
                        page_router.go(routerText.text, {info:argText.text})
                    }
                }
            }
        }
    }

    function installPatch() {
        rest1.visible = true
        progressBar.visible = true
        installButton.visible = false
        btn.visible = false
        icon.visible = false
        patcherTipTitle.text = backend.get_element_loc('installing')
        patcherTip.text = backend.get_element_loc('installing_tip')
        patcher.get_ready_for_install()
        backend._update()
    }

    function apply_patch(filePath) {
        rest1.visible = true
        progressBar.visible = true
        btn.visible = false
        installButton.visible = false
        icon.visible = false
        patcherTipTitle.text = backend.get_element_loc('getting_ready')
        patcherTip.text = backend.get_element_loc('applying_tip')
        patcher.add_local_patch(filePath)
    }

    Connections {
        target: patcher
        function onErrorHappens(error) {
            rest1.visible = true
            progressBar.visible = false
            icon.source = FluentIcons.graph_StatusErrorFull
            icon.visible = true
            btn.visible = false
            installButton.visible = false
            if (error == "ERR_INVALID_PATCH") {
                patcherTip.text = backend.get_element_loc('patcher_file_error') + " - " + error
                patcherTipTitle.text = backend.get_element_loc('patcher_file_error_title')
            } else {
                patcherTip.text = error
            }
        }
        function onPatcherWorkFinished() {
            rest1.visible = true
            progressBar.visible = false
            btn.visible = true
            installButton.visible = true
            icon.source = FluentIcons.graph_Checkmark
            icon.visible = false
            patcherTipTitle.text = backend.get_element_loc('patcher_ready_to_install')
            patcherTip.text = backend.get_element_loc('patcher_ready_to_install_tip')
        }
    }

}