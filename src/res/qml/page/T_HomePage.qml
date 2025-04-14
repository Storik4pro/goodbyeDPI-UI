import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    title: backend.get_element_loc("home")
    id:page
    header:Item{}
    property string engine : backend.getValue('GLOBAL', 'engine')
    property string engine_version: backend.getValue('COMPONENTS', backend.getValue('GLOBAL', 'engine').toLowerCase()+"_version")
    property string preset: process.get_preset()
    property bool stopBtnEnabled: !goodCheck.is_process_alive()
    ColumnLayout {
        Layout.preferredWidth: Math.min(1000, parent.width)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignCenter
        RowLayout{
            IconLabel {
                icon.width: 15
                icon.height: 15
                spacing: 5
                icon.name: FluentIcons.graph_ClipboardList
                text: backend.get_element_loc("component_now")
                font: Typography.bodyStrong

            }
            Button{
                flat: true
                text: backend.get_element_loc("edit")
                icon.width: 15
                icon.height: 15
                spacing: 5
                icon.name: FluentIcons.graph_Edit
                onClicked:{
                    page_router.go("/system",{info:"Component"})
                }
            }
        }
        ColumnLayout{
            Layout.leftMargin:20
            Layout.bottomMargin:10
            RowLayout{
                Label {
                    text: backend.get_element_loc("component")
                }
                CopyableText{
                    text:engine
                    font: Typography.caption
                    color: "#c0c0c0"
                }
            }
            RowLayout{
                Label {
                    text: backend.get_element_loc("version")
                }
                CopyableText{
                    id:version
                    text:engine_version
                    font: Typography.caption
                    color: "#c0c0c0"
                }
            }
            RowLayout{
                Label {
                    text: backend.get_element_loc("preset")
                }
                CopyableText{
                    text:preset
                    font: Typography.caption
                    color: "#c0c0c0"
                }
            }
            

        }

        Rectangle {
            Layout.preferredHeight: 68
            Layout.fillWidth: true
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
                    text: backend.get_element_loc("on")
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
                    id: startSwitch
                    property bool isInitializing: process.is_process_alive()
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: process.is_process_alive()
                    enabled:!goodCheck.is_process_alive() && !systemProcessHelper.is_alive()
                    onClicked: {
                        if (!isInitializing){
                            if (checked) {
                                process.start_process()
                            } else {
                                var success = process.stop_process()
                                if (!success) {
                                    toast.show_error("#NOTF_FAI_retry", text.inAppText['error_title'],
                                                     backend.get_element_loc('close_error') + " " + 
                                                     process.get_executable() + " " + 
                                                     backend.get_element_loc('close_error2'),
                                                     backend.get_element_loc('retry'), "")
                                }
                            }
                        }
                        isInitializing = false
                    }
                }
            }
        }
        Rectangle {
            id:rest1
            Layout.preferredHeight: Math.max(60, infoColumnLayout.implicitHeight + 20)
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            radius: 6
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)

            visible: true 
            ColumnLayout{
                id:infoColumnLayout
                anchors.verticalCenter: parent.verticalCenter  
                RowLayout{    
                    spacing:10
                    height:20
                    Layout.leftMargin:10
                    
                    Icon{
                        id: icon_info
                        Layout.preferredHeight:20
                        source:FluentIcons.graph_Lightbulb
                        color:Theme.accentColor.defaultBrushFor()
                    }
                    ColumnLayout{
                        id:clmn
                        Label{
                            text:backend.get_element_loc('fact')
                            font: Typography.bodyStrong
                        }
                        Label{
                            Layout.preferredWidth:rest1.width - 100
                            text:backend.get_fact()
                            font: Typography.body
                            wrapMode:Text.Wrap
                        }
                    }
                    IconButton{
                        text: "Close"
                        icon.name: FluentIcons.graph_ChromeClose
                        width: 15
                        height: 15
                        icon.width: 14
                        icon.height: 14
                        display: IconButton.IconOnly
                        Layout.alignment:Qt.AlignTop
                        onClicked:{
                            rest1.visible = false
                        }
                    }

                }
            }
        }

        Expander{
            Layout.fillWidth: true
            expanded: true
            header: Label {
                text: backend.get_element_loc("quick_settings")
                horizontalAlignment: Qt.AlignVCenter
                font: Typography.body  
            }
            content: ColumnLayout{
                ColumnLayout{
                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.bottomMargin: 5
                    }
                    IconLabel {
                        icon.width: 15
                        icon.height: 15
                        spacing: 5
                        icon.name: FluentIcons.graph_Personalize
                        text: backend.get_element_loc("personalize")
                        font: Typography.bodyStrong
                        Layout.leftMargin: 10
                    }
                    RowLayout{
                        Layout.fillWidth: true

                        ColumnLayout{
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 10 
                            Layout.rightMargin: 5
                            Button{
                                Layout.fillWidth: true
                                text: backend.get_element_loc("toggle_mode")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                checked:backend.getValue('APPEARANCE_MODE', 'mode') === 'dark'
                                onClicked:{
                                    if (checked) {
                                        checked = false
                                    } else {
                                        checked = true
                                    }
                                    backend.changeValue('APPEARANCE_MODE', 'mode', checked ? 'dark':'light');
                                    handleDarkChanged(this)
                                }
                            }
                        }
                        ColumnLayout{
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 5
                            Layout.rightMargin: 10
                            Button{
                                Layout.fillWidth: true
                                text: "Language" 
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                onClicked:{
                                    page_router.go("/personalize")
                                }
                            }
                        }
                    }
                    IconLabel {
                        icon.width: 15
                        icon.height: 15
                        spacing: 5
                        icon.name: FluentIcons.graph_System
                        text: backend.get_element_loc("system")
                        font: Typography.bodyStrong
                        Layout.leftMargin: 10
                    }
                    RowLayout{
                        id: rw
                        width: parent.width

                        ColumnLayout{
                            Layout.fillWidth: true
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 10
                            Layout.rightMargin: 5
                            Button{
                                Layout.fillWidth: true
                                text: checked ? backend.get_element_loc("autorun_out"):backend.get_element_loc("add_to_autorun")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                checked:backend.getBool('GLOBAL', 'autorun')
                                onClicked:{
                                    if (checked) {
                                        checked = false
                                        backend.remove_from_autorun()
                                    } else {
                                        checked = true
                                        backend.add_to_autorun()
                                    }
                                    backend.toggleBool('GLOBAL', "autorun", checked)
                                }
                            }
                        }
                        ColumnLayout{
                            Layout.fillWidth: true
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 5
                            Layout.rightMargin: 10
                            Button{
                                Layout.fillWidth: true
                                text: backend.get_element_loc("check_updates")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                onClicked:{
                                    page_router.go("/update")
                                }
                                
                            }
                        }
                    }
                    IconLabel {
                        icon.width: 15
                        icon.height: 15
                        spacing: 5
                        icon.name: FluentIcons.graph_Package
                        text: backend.get_element_loc("additional")
                        font: Typography.bodyStrong
                        Layout.leftMargin: 10
                    }
                    RowLayout{
                        Layout.fillWidth: true

                        ColumnLayout{
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 10 
                            Layout.rightMargin: 5
                            Button{
                                enabled: backend.check_winpty()
                                Layout.fillWidth: true
                                text: backend.get_element_loc("see_output")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                onClicked:{
                                    WindowRouter.go("/pseudoconsole")
                                }
                            }
                        }
                        ColumnLayout{
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 5
                            Layout.rightMargin: 10
                            Button{
                                id:stop
                                enabled:stopBtnEnabled
                                Layout.fillWidth: true
                                LayoutMirroring.enabled: true
                                text: backend.get_element_loc("pseudoconsole_stop")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
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
                                            width:400
                                            text: backend.get_element_loc("pseudoconsole_question")
                                            wrapMode:Text.Wrap
                                        }
                                    }
                                    footer: DialogButtonBox{
                                    Button{
                                        text: qsTr("OK")
                                        onClicked: {
                                            var success = process.stop_process()
                                            if (success) {
                                                process.stop_service()
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

                    IconLabel {
                        icon.width: 15
                        icon.height: 15
                        spacing: 5
                        icon.name: FluentIcons.graph_OpenInNewWindow
                        text: backend.get_element_loc("FAQ")
                        font: Typography.bodyStrong
                        Layout.leftMargin: 10
                    }
                    RowLayout{
                        Layout.fillWidth: true

                        ColumnLayout{
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 10 
                            Layout.rightMargin: 5
                            Button{
                                Layout.fillWidth: true
                                text: backend.get_element_loc("report_bug")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                onClicked:{
                                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/issues");
                                }
                            }
                        }
                        ColumnLayout{
                            Layout.preferredWidth: parent.width / 2
                            Layout.leftMargin: 5
                            Layout.rightMargin: 10
                            Button{
                                Layout.fillWidth: true
                                LayoutMirroring.enabled: true
                                text: backend.get_element_loc("send_ideas")
                                contentItem: Label {
                                    anchors.fill: parent
                                    anchors.leftMargin: 7
                                    anchors.rightMargin: 7
                                    text: parent.text
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                onClicked:{
                                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/discussions/categories/ideas");
                                }
                            }
                        }
                    }
                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.bottomMargin: 5
                    }
                }
            }
            _height: 35
        }

    }
    function callback() {
        console.log("test")
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
    Connections {
        target:goodCheck
        function onStarted(){
            startSwitch.enabled = false;
            stopBtnEnabled = false;
        }
        function onProcess_finished_signal(){
            startSwitch.enabled = true;
            stopBtnEnabled = true;
        }
    }
    Connections{
        target:systemProcessHelper
        function onProcessCheckedStarted(){
            startSwitch.enabled = false;
            stopBtnEnabled = false;
        }
        function onProcessCheckedStopped(){
            startSwitch.enabled = true;
            stopBtnEnabled = true;
        }
    }
    Connections {
        target:process
        function onEngine_changed() {
            var _engine = arguments[0];
            engine = _engine
            engine_version = backend.getValue('COMPONENTS', engine.toLowerCase()+"_version")

        }
        function onPreset_changed() {
            preset = process.get_preset()
        }
        function onError_happens() {
            startSwitch.checked = false
        }
        function onProcess_started() {
            startSwitch.checked = true
        }
        function onProcess_stopped() {
            startSwitch.checked = false
        }
    }
    Connections {
        target:toast
        function onNotificationAction(notificationId, action) {
            if (notificationId === "#NOTF_FAI_retry" && action === 'user_not_dismissed') {
                var success = process.stop_process()
                if (!success) {
                    toast.show_error("#NOTF_FAI_retry", text.inAppText['error_title'],
                                        backend.get_element_loc('close_error') + " " + 
                                        process.get_executable() + " " + 
                                        backend.get_element_loc('close_error2'),
                                        backend.get_element_loc('retry'), "")
                }
            }
        }
    }
    
}