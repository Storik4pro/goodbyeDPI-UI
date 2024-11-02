import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    title: backend.get_element_loc('additional')
    id:page
    header:ColumnLayout{
    ColumnLayout {
        id:heade
        Layout.topMargin:48
        Layout.leftMargin:24
        Layout.rightMargin:24
        Layout.fillWidth: true

        Label {
            text: qsTr(backend.get_element_loc('pseudoconsole_title')).arg(execut)
            font:Typography.title
        }

        IconLabel {
            id: status_label
            text: qsTr(backend.get_element_loc('pseudoconsole_find'))
            font:Typography.subtitle
            icon.name:FluentIcons.graph_InfoSolid
            icon.width: 20
            icon.height: 15
            icon.color:Theme.accentColor.defaultBrushFor()
            spacing: 5
        }
    }
    }
    property bool output_ready: false
    property bool process_state: process.is_process_alive()
    property string execut: process.get_executable()
    property string output_str:  (process.get_output() === "") ? 
        "[DEBUG?] Yap, here want been flashlight animation. But, it's missing here. If you see it message, sorry" :
        process.get_output()

    ColumnLayout {
        spacing: 10
        ColumnLayout {
            id: contentLayout
            Layout.minimumHeight: 100
            Layout.preferredHeight: page.height - header.implicitHeight - qfooter.implicitHeight - 48 - 24
            Layout.fillWidth: true

            Rectangle {
                id: rest
                Layout.preferredWidth: page.width -48
                Layout.minimumWidth: 300
                Layout.alignment: Qt.AlignHCenter
                color: "#1E1E1E"
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 6
                visible: true
                Layout.preferredHeight: parent.height

                ScrollView {
                    id: scrollView
                    anchors.fill:parent
                    anchors.margins:10
                    Layout.fillHeight: true
                    Column {
                        width: parent.width
                        CopyableText {
                            id: commandLineOutput
                            width: parent.width
                            text: output_str
                            wrapMode: Text.Wrap
                            font.pixelSize: 14
                            font.family: "Cascadia Code"
                            color: "#D4D4D4"
                        }
                    }
                }
            }
        }
        Item{
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

    }


    ColumnLayout{
        id:qfooter
        RowLayout {
            Layout.fillWidth: true
            spacing: 24

            Button {
                id: copy_button
                text: qsTr(backend.get_element_loc('pseudoconsole_copy'))
                icon.name: FluentIcons.graph_Copy
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth:200
                spacing: 5
                onClicked: {
                    Qt.callLater(() => {
                        commandLineOutput.selectAll()
                        commandLineOutput.copy()
                    })
                }
            }

            Item { Layout.fillWidth: true } 

            IconButton {
                id: restart_button
                text: qsTr(backend.get_element_loc('get_help'))
                
                icon.name: FluentIcons.graph_FavoriteStar
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth:200
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
                Layout.preferredWidth:200
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
                            width:400
                            text: backend.get_element_loc("pseudoconsole_question")
                            wrapMode:Text.Wrap
                        }
                    }
                    footer: DialogButtonBox{
                    Button{
                        text: qsTr("OK")
                        onClicked: {
                            addOutput("\n[DEBUG] Initializing process stop\n")
                            var success = process.stop_process()
                            if (success) {
                                addOutput("\n[DEBUG] Initializing windrivert.sys stop\n")
                                process.stop_service()
                            } else {
                                addOutput("\n[DEBUG] Error while initializing windrivert.sys stop\n")
                            }
                            confirmationDialog.close()
                        }
                    }
                    Button{
                        text: backend.get_element_loc("cancel")
                        highlighted: true
                        onClicked: {
                            confirmationDialog.close()
                        }
                    }
                }
                }
                onClicked: confirmationDialog.open()
            }
        }
    }

    function addError(error){
        output_str += "[ERROR] " + error
    }

    function addOutput(output) {
        if (!output_ready) {
            output_ready = true
            output_str = "[DEBUG] Connecting to " + execut + "...\n\n"
        }
        if (output !== '') {
            output_str += output
        }
        if (output.includes("Internal error.")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_internal_error')))
            setIcon("error")

        } else if (output.includes("Error opening filter") || output.includes("unknown option") || 
                  output.includes("[PROXY] error creating listener:") || output.includes("[ERROR]")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_error')).arg(execut))
            setIcon("error")
        
        } else if (output.includes("process has been terminated by user")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_user_stop')).arg(execut))
            setIcon("info")
        } else if (output.includes("process has been terminated for unknown reason")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_uncn_stop')).arg(execut))
            setIcon("error")
        } 
    }

    function clearOutput() {
        if (output_str !== "") {
            output_str = ""
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

    Component.onCompleted:{
        addOutput(output_str);
        if (process_state) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success')).arg(execut))
            setIcon('sucess')
        } 
    }

    Connections {
        target: process
        function onOutput_added() {
            var _output = arguments[0];
            addOutput(_output);
        }
        function onError_happens() {
            var _output = arguments[0];
            addOutput(_output);
        }
        function onProcess_started(){
            Qt.callLater(updateStatus, qsTr(backend.get_element_loc('pseudoconsole_success')).arg(execut))
            Qt.callLater(setIcon, "sucess")
            output_str = ""
            toast.show_notification("#NOTF_SUC", process.get_executable(), backend.get_element_loc('process_run'))
        }
        function onProcess_stopped() {
            var reason = arguments[0];
            if (reason === 'by user') {
                updateStatus(qsTr(backend.get_element_loc('pseudoconsole_user_stop')).arg(execut))
                setIcon("info")
            } else {
                updateStatus(qsTr(backend.get_element_loc('pseudoconsole_uncn_stop')).arg(execut))
                setIcon("error")
                toast.show_error("#NOTF_FAI_pseudoconsoleOpen", process.get_executable(), qsTr(backend.get_element_loc('pseudoconsole_uncn_stop')).arg(execut),
                                 "open pseudoconsole", "")

            }
        }
        function onEngine_changed() {
            execut = process.get_executable()
        }
    }
    Connections {
        target:toast
        function onNotificationAction(notificationId, action) {
            if (notificationId === "#NOTF_FAI_pseudoconsoleOpen") {
                if (action === "user_not_dismissed") {

                }
            }
        }
    }
}