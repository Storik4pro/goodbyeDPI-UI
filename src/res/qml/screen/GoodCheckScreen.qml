import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    id: page
    title: backend.get_element_loc('additional')

    header: ColumnLayout {
    ColumnLayout {
        id:heade
        Layout.topMargin: 48
        Layout.leftMargin: 24
        Layout.rightMargin: 24
        Layout.fillWidth: true
        IconLabel {
            id: status_label
            text: qsTr(backend.get_element_loc('pseudoconsole_find'))
            font: Typography.subtitle
            icon.name: FluentIcons.graph_InfoSolid
            icon.width: 20
            icon.height: 15
            icon.color: Theme.accentColor.defaultBrushFor()
            spacing: 5
        }
    }
    }

    property bool output_ready: false
    property bool process_state: false
    property string execut: "goodcheckgogo.exe" 
    property string output_str: ""

    ColumnLayout {
        spacing: 10
        ColumnLayout {
            id: contentLayout
            Layout.minimumHeight: 100
            Layout.preferredHeight: page.height - header.implicitHeight - qfooter.implicitHeight - autoscroll.implicitHeight - 48 - 24
            Layout.fillWidth: true

            Rectangle {
                id: rest
                Layout.preferredWidth: page.width - 48
                Layout.minimumWidth: 300
                Layout.alignment: Qt.AlignHCenter
                color: "#1E1E1E"
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 6
                visible: true
                Layout.preferredHeight: parent.height

                ScrollView {
                    id: scrollView
                    anchors.fill: parent
                    anchors.margins: 10
                    Layout.fillHeight: true
                    ScrollBar.vertical.policy: ScrollBar.AlwaysOn
                    Column {
                        width: rest.width - 20
                        CopyableText {
                            id: commandLineOutput
                            width: rest.width - 20
                            text: output_str
                            wrapMode: Text.Wrap
                            font.pixelSize: 14
                            font.family: "Cascadia Code"
                            color: "#D4D4D4"
                            onTextChanged: {
                                if (autoscroll.checked) {
                                    scrollView.ScrollBar.vertical.position = scrollView.contentHeight
                                }
                            }
                        }
                    }
                }
            }
        }
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }

    CheckBox {
        id:autoscroll
        checked:true
        Layout.alignment:Qt.AlignRight
        text:backend.get_element_loc("autoscroll")
        Layout.topMargin: -7
        Layout.bottomMargin:7
    }

    ColumnLayout {
        id: qfooter
        RowLayout {
            Layout.fillWidth: true
            Layout.bottomMargin: -15
            spacing: 24

            Button {
                id: copy_button
                text: qsTr(backend.get_element_loc('pseudoconsole_copy'))
                icon.name: FluentIcons.graph_Copy
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth: 200
                spacing: 5
                onClicked: {
                    commandLineOutput.selectAll()
                    commandLineOutput.copy()
                }
            }

            Item { Layout.fillWidth: true }

            IconButton {
                id: restart_button
                text: qsTr(backend.get_element_loc('get_help'))
                display: IconButton.IconOnly
                icon.name: FluentIcons.graph_FavoriteStar
                icon.width: 18
                icon.height: 18
                onClicked: {
                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/discussions")
                }
            }

            Button {
                id: stop_button
                text: qsTr(backend.get_element_loc('pseudoconsole_stop'))
                icon.name: FluentIcons.graph_Delete
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth: 200
                onClicked: confirmationDialog.open()
                ToolTip.visible: hovered
                ToolTip.delay: 500
                ToolTip.text: qsTr(backend.get_element_loc('pseudoconsole_stop'))
            }
            Button {
                id: close_button
                text: qsTr(backend.get_element_loc('close_tool'))
                icon.name: FluentIcons.graph_Cancel
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth: 200
                spacing: 5
                onClicked: {
                    goodCheck.close_console()
                }
            }
        }
    }

    Dialog {
        id: confirmationDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        parent: Overlay.overlay
        modal: true
        title: backend.get_element_loc("pseudoconsole_question_title")
        Column {
            spacing: 20
            Label {
                width: 400
                text: backend.get_element_loc("goodcheck_question")
                wrapMode: Text.Wrap
            }
            Row {
                spacing: 10
                Button {
                    text: qsTr("OK")
                    onClicked: {
                        addOutput("\n[DEBUG] Initializing process stop\n")
                        goodCheck.stop_process()
                        confirmationDialog.close()
                    }
                }
                Button {
                    text: backend.get_element_loc("cancel")
                    highlighted: true
                    onClicked: {
                        confirmationDialog.close()
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        addOutput(goodCheck.get_output())
    }

    property string inputPrompt: ""

    function addOutput(output) {
        if (!output_ready) {
            output_ready = true
            output_str = "[DEBUG] Connecting to GoodCheck...\n\n"
        }
        if (output !== '') {
            output_str += output
        }
        if (output.includes("Exiting with an error...")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_error')).arg(execut))
            setIcon("error")
        } else if (output.includes("All Done")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success_end')).arg(execut))
            setIcon("success")
            stop_button.enabled = false
        } 
    }
    function updateStatus(text) {
        status_label.text = text
    }
    function setIcon(type) {
        if (type === "info") {
            status_label.icon.name = FluentIcons.graph_InfoSolid
            status_label.icon.color = Theme.accentColor.defaultBrushFor()
        } else if (type === "error") {
            status_label.icon.name = FluentIcons.graph_StatusErrorFull
            status_label.icon.color = Theme.res.systemFillColorCritical
        } else {
            status_label.icon.name = FluentIcons.graph_CompletedSolid
            status_label.icon.color = Theme.res.systemFillColorSuccess
        }
    }

    Connections {
        target: goodCheck
        function onOutput_signal (output_signal) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success')).arg(execut))
            setIcon("success")
            addOutput(output_signal)
        }
        function onProcess_finished_signal () {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success_end')).arg(execut))
            setIcon("success")
        }
        function onProcess_stopped_signal() {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_user_stop')).arg(execut))
            setIcon("info")
        }
    }
}