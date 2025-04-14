import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI
import QtQuick.Dialogs 

Page{
    id:page
    header: Item{}
    title: "SpoofDPI"
    padding: 0
    topPadding: 24

    InfoBarManager{
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }
Loader {
    id: pageLoader
    anchors.fill: parent
    sourceComponent: pageComponent

    FileDialog {
        id: fileDialogSave
        title: qsTr("Save File As")
        nameFilters: ["JSON Files (*.json)"]
        fileMode: FileDialog.SaveFile
        currentFolder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            backend.save_preset('spoofdpi', filePath)
            process.update_preset()
        }
    }


    FileDialog {
        id: fileDialogOpen
        title: "Choose JSON file..."
        nameFilters: ["JSON Files (*.json)"]
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            var result = backend.load_preset('spoofdpi', filePath)

            if (result === true) {
                pageLoader.sourceComponent = null
                pageLoader.sourceComponent = pageComponent
                process.update_preset()
            } else {
                info_manager_bottomright.show(InfoBarType.Error, "Error: Unknown error", 3000)
            }
        }
    }

    Component {
    id: pageComponent

ScrollablePage {
    topPadding: 0
    leftPadding: 0
    rightPadding: 0

    ListModel {
        id: blacklistFilesModel
        onCountChanged: {
            generateCommandLine()
        }
    }

    ColumnLayout{
        id:base_layout
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.leftMargin:24
        Layout.rightMargin:24
        Layout.alignment: Qt.AlignHCenter
        visible:!backend.getBool('COMPONENTS', 'spoofdpi')
        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter

            Flow {
                id: mainFlow
                Layout.fillWidth: true
                spacing: 20
                flow: Flow.LeftToRight

                RowLayout{
                    Item{
                        Layout.alignment: Qt.AlignLeft
                        Layout.preferredHeight:90 
                    }

                ColumnLayout {
                    id: contentColumn
                    Layout.minimumWidth: 100
                    Layout.maximumWidth: 700
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignLeft
                    

                    Label {
                        id:mainLabel
                        text: backend.get_element_loc("component_not_installed")
                        font: Typography.subtitle
                        wrapMode: Text.Wrap
                        Layout.alignment: Qt.AlignLeft
                        Layout.preferredWidth: Math.min(960, Math.max(300, base_layout.width - 20))
                        anchors.rightMargin: 20
                    }

                    ProgressBar {
                        id: progressBarDownload
                        indeterminate: false
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        anchors {
                            rightMargin: 15
                            topMargin: 20
                            bottomMargin: 20
                        }
                        visible: false
                    }

                    Label {
                        id: timeLabel
                        text: backend.get_element_loc("component_not_installed_tip")
                        font: Typography.body
                        wrapMode: Text.Wrap
                        Layout.preferredWidth: Math.min(960, Math.max(300, base_layout.width - 20))
                        Layout.alignment: Qt.AlignLeft
                        visible: true
                    }
                    CopyableText {
                        id: errorLabel
                        text: ""
                        font: Typography.body
                        color: "#666666"
                        Layout.alignment: Qt.AlignLeft
                        visible: false
                    }
                }
                }
            }
            RowLayout{
                Layout.alignment: Qt.AlignVCenter
                Layout.fillWidth: true
                Item{
                    Layout.alignment: Qt.AlignLeft
                    Layout.preferredHeight:mainLabel.width == timeLabel.width ? checkBtn.height:90 
                }
                Row{
                    height: 30
                    spacing: 10
                    ProgressRing {
                        id: progressBar
                        indeterminate: true
                        anchors {
                            rightMargin: 15
                            topMargin: 20
                            bottomMargin: 20
                        }
                        width:30
                        height:30
                        strokeWidth:4
                        visible: false
                    }

                }
                Button {
                    id: checkBtn
                    text: backend.get_element_loc("update_available_btn_t")
                    highlighted: true
                    enabled:!systemProcessHelper.is_alive()
                    Layout.minimumWidth: 50
                    Layout.alignment: Qt.AlignRight|Qt.AlignVCenter
                    
                    onClicked: {
                        download_component();
                    }
                }
                
                
            }
        }
    }

    ColumnLayout {
        width: parent.width
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignHCenter
        ColumnLayout {
            id: mainLayoutt
            spacing: 15
            Layout.leftMargin:24
            Layout.rightMargin:24
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            visible:backend.getBool('COMPONENTS', 'spoofdpi')
            Rectangle {
                id:rest1
                Layout.preferredHeight: Math.max(100, infoColumnLayout.implicitHeight + 20)
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.controlFillColorDefault
                radius: 6
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)

                visible: backend.getValue('GLOBAL', 'engine') === "spoofdpi" ? false : true 
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
                            source:FluentIcons.graph_InfoSolid
                            color:Theme.accentColor.defaultBrushFor()
                        }
                        ColumnLayout{
                            Label{
                                text:backend.get_element_loc('attention')
                                font: Typography.bodyStrong
                            }
                            Label{
                                Layout.preferredWidth:rest1.width - 100
                                text:backend.get_element_loc('warn1')
                                font: Typography.body
                                wrapMode:Text.Wrap
                            }
                            Button{
                                text: backend.get_element_loc('fixnow')
                                onClicked:{
                                    process.change_engine("spoofdpi")
                                    rest1.visible = false
                                }
                            }
                        }

                    }
                }
            }

            ColumnLayout {
                id: mainLayout
                anchors.margins: 20
                spacing: 3
                width: parent.width
                
                ListModel {
                    id: settingsModel

                    ListElement { text: "-debug"; optionId: "enableDebug"; checked: false; type: "switch" }
                    ListElement { text: "-enable-doh"; optionId: "enableDOH"; checked: false; type: "switch" }
                    ListElement { text: "-dns-ipv4-only"; optionId: "ipv4Only"; checked: false; type: "switch" }
                    ListElement { text: "-silent"; optionId: "silent"; checked: false; type: "switch" }
                    ListElement { text: "-system-proxy"; optionId: "systemProxy"; checked: false; type: "switch" }

                    ListElement { text: "-addr string"; optionId: "addr"; value: ""; placeholder: "IP addres"; type: "input" }
                    ListElement { text: "-dns-addr"; optionId: "dns"; value: ""; placeholder: "IP addres"; type: "input" }
                    ListElement { text: "-dns-port"; optionId: "dnsPort"; value: ""; placeholder: "Port"; type: "input" }
                    ListElement { text: "-port value"; optionId: "port"; value: ""; placeholder: "Port"; type: "input" }
                    ListElement { text: "-pattern value"; optionId: "pattern"; value: ""; placeholder: "Regex pattern"; type: "input" }
                    ListElement { text: "-timeout value"; optionId: "timeout"; value: ""; placeholder: "ms value"; type: "input" }
                    ListElement { text: "-window-size"; optionId: "windowSize"; value: ""; placeholder: "Digital value"; type: "input" }

                }
                Repeater {
                    model: settingsModel
                    
                    delegate: ColumnLayout {
                        Layout.preferredHeight: type === "blacklist" ? undefined : 45 
                        Layout.fillWidth: true
                        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                        Layout.minimumWidth: 300
                        Layout.maximumWidth: 1000
                        Layout.alignment: Qt.AlignHCenter
                        
                        Loader {
                            id: itemLoader
                            
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            sourceComponent: type === "blacklist" ? blacklistItemComponent : defaultItemComponent
                            property int itemIndex: index
                            property var modelData: model
                        }
                    }
                }

                Label {
                    text: backend.get_element_loc("config_settings")
                    font: Typography.bodyStrong
                    Layout.topMargin: 15
                }
                RowLayout{
                    enabled:advancedSwitch.checked
                    Layout.fillWidth:true
                    spacing: 10
                    ColumnLayout {
                        Layout.preferredWidth:mainLayoutt.width - clmn1.implicitWidth - 10
                        Label {
                            horizontalAlignment: Text.AlignLeft
                            Layout.preferredWidth:mainLayoutt.width - clmn1.implicitWidth
                            text: backend.get_element_loc("config_now_use") + ": "
                            wrapMode:Text.Wrap
                        }
                        CopyableText {
                            horizontalAlignment: Text.AlignLeft
                            Layout.preferredWidth:mainLayoutt.width - clmn1.implicitWidth
                            text:process.get_config_name('spoofdpi')
                            wrapMode:Text.Wrap
                        }

                    }
                    ColumnLayout{
                        id:clmn1
                        Layout.alignment: Qt.AlignRight
                        Layout.fillWidth:true
                        RowLayout{
                        Button {
                            text: backend.get_element_loc("load_config_file")
                            display: Button.IconOnly
                            icon.name: FluentIcons.graph_OpenFile 
                            icon.height: 20
                            icon.width:20
                            onClicked: {
                                fileDialogOpen.open()
                            }
                            ToolTip.visible: hovered
                            ToolTip.delay: 500
                            ToolTip.text: text
                        }
                        Button {
                            text: backend.get_element_loc("export_config_file")
                            display: Button.IconOnly
                            icon.name: FluentIcons.graph_SaveAs
                            icon.height: 20
                            icon.width:20
                            onClicked: {
                                fileDialogSave.open()
                            }
                            ToolTip.visible: hovered
                            ToolTip.delay: 500
                            ToolTip.text: text
                        }

                        Button {
                            text: backend.get_element_loc("reset_config")
                            display: Button.IconOnly
                            icon.name: FluentIcons.graph_Refresh
                            icon.height: 20
                            icon.width:20
                            onClicked: {
                                backend.return_to_default('spoofdpi')
                                process.update_preset()
                                pageLoader.sourceComponent = null
                                pageLoader.sourceComponent = pageComponent
                            }
                            ToolTip.visible: hovered
                            ToolTip.delay: 500
                            ToolTip.text: text
                        }
                        }

                    }
                }

                Label {
                    text: backend.get_element_loc("custom_params")
                    font: Typography.bodyStrong
                    Layout.topMargin: 15
                }
                Rectangle {
                    Layout.preferredHeight: customParameters.implicitHeight + 20
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    color: Theme.res.controlFillColorDefault
                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                    radius: 6

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 5

                        

                        TextArea  {
                            id: customParameters
                            placeholderText: backend.get_element_loc("custom_params_placeholder")
                            wrapMode: TextEdit.Wrap
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            FluentUI.radius:6
                            property bool isInitializing: false
                            onTextChanged: {
                                if (!isInitializing) {
                                    var cursorPosition = customParameters.cursorPosition
                                    var previousText = text
                                    var newText = text.replace(/[^0-9a-zA-Z:"><\/\\.\-_\s,=]/g, '')
                                    if (newText !== previousText) {
                                        var diff = previousText.length - newText.length
                                        text = newText
                                        customParameters.cursorPosition = cursorPosition - diff
                                        info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                    }
                                    saveCustomParameters()
                                    generateCommandLine()
                                }
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                text = backend.get_from_config("SPOOFDPI", "custom_parameters")
                                generateCommandLine()
                            }
                            function saveCustomParameters() {
                                var params = customParameters.text.trim()
                                var processedParams = params.replace(/=/g, ' ').replace(/"/g, '')
                                backend.set_to_config("SPOOFDPI", "custom_parameters", processedParams)
                            }
                        }


                    }
                }

                Label {
                    text: backend.get_element_loc("output_prompt")
                    font: Typography.bodyStrong
                    Layout.topMargin: 15
                }
                ColumnLayout {
                    id: contentLayout
                    Layout.minimumHeight:100
                    Layout.preferredHeight:commandLineOutput.implicitHeight + 20
                    
                    Rectangle {
                        id: rest
                        Layout.fillWidth: true
                        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                        Layout.minimumWidth: 300
                        Layout.maximumWidth: 1000
                        Layout.alignment: Qt.AlignHCenter
                        color: "#1E1E1E"
                        border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                        radius: 6
                        visible: true
                        Layout.preferredHeight:parent.height

                        CopyableText {
                            id: commandLineOutput
                            anchors.fill: parent
                            anchors.margins: 10
                            width: parent.width - 20
                            text: command
                            wrapMode: Text.Wrap
                            font.pixelSize: 14
                            font.family: "Cascadia Code"
                            color: "#D4D4D4"
                            height: implicitHeight
                        }
                    }
                }

            }
        }
    }
    
    
    

    Component {
        id: defaultItemComponent
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: itemLabel.height + 5
            color: modelData.index % 2 === 0 ? Theme.res.subtleFillColorSecondary : Theme.res.subtleFillColorTertiary
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 4

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                spacing: 10

                Label {
                    id:itemLabel
                    text: backend.get_element_loc(modelData.optionId+"_text")
                    font: Typography.body
                    wrapMode: Text.Wrap
                    Layout.maximumHeight:49
                    Layout.preferredWidth: parent.width - (modelData.type === "input" ? 
                                                           inputField.width+checkBoxControl.width+20 : 
                                                           switchControl.width)
                    verticalAlignment: Text.AlignVCenter
                }

                Item {
                    id:item
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter

                    RowLayout {
                        anchors{
                            right: parent.right
                            verticalCenter: parent.verticalCenter
                        }
                        spacing: 5

                        CheckBox {
                            id: checkBoxControl
                            checked: modelData.checked
                            visible: modelData.type === "input"
                            property bool isInitializing: true
                            FluentUI.radius:0

                            onCheckedChanged: {
                                if (!isInitializing) {
                                    settingsModel.setProperty(modelData.index, "checked", checked)
                                    if (modelData.type === "input") {
                                        inputField.enabled = checked
                                    }
                                    backend.set_to_config("SPOOFDPI", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                            }
                            Component.onCompleted: {
                                checked = backend.get_bool_from_config("SPOOFDPI", modelData.optionId)
                                settingsModel.setProperty(modelData.index, "checked", checked)
                                if (modelData.type === "input") {
                                    inputField.enabled = checked
                                }
                                isInitializing = false
                                generateCommandLine()
                            }
                        }

                        TextField {
                            id: inputField
                            text: modelData.value
                            placeholderText: modelData.placeholder
                            inputMethodHints: Qt.ImhDigitsOnly
                            enabled: modelData.checked
                            width: 100
                            Layout.rightMargin:10
                            visible: modelData.type === "input"
                            property bool isInitializing: true

                            onTextChanged: {
                                if (!isInitializing) {
                                    if (modelData.type === "input") {
                                        var allowedCharsRegex = /^[0-9a-zA-Z:\/\\.\-\_\s,]*$/
                                        if (!allowedCharsRegex.test(text)) {
                                            var cursorPosition = inputField.cursorPosition - 1
                                            text = text.slice(0, cursorPosition) + text.slice(cursorPosition + 1)
                                            inputField.cursorPosition = cursorPosition
                                            info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                        } else {
                                            settingsModel.setProperty(modelData.index, "value", text)
                                            backend.set_to_config("SPOOFDPI", modelData.optionId + "_value", text)
                                            generateCommandLine()
                                        }
                                    }    
                                }
                                
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                if (modelData.type === "input") {
                                    text = backend.get_from_config("SPOOFDPI", modelData.optionId + "_value")
                                }
                                settingsModel.setProperty(modelData.index, "value", text)
                                isInitializing = false
                                generateCommandLine()
                            }
                        }

                        Switch {
                            id: switchControl
                            checked: modelData.checked
                            visible: modelData.type === "switch"
                            property bool isInitializing : true
                            Layout.rightMargin:20
                            onCheckedChanged: {
                                if (!isInitializing) {
                                    settingsModel.setProperty(modelData.index, "checked", checked)
                                    backend.set_to_config("SPOOFDPI", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                                isInitializing = false
                                console.log(isInitializing)
                            }
                            Component.onCompleted: {
                                checked = backend.get_bool_from_config("SPOOFDPI", modelData.optionId)
                                settingsModel.setProperty(modelData.index, "checked", checked)
                                isInitializing = false
                                generateCommandLine()
                            }
                        }
                    }
                }
            
            }
        }
    }

    ColumnLayout{
        anchors.margins: 20
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        Layout.leftMargin:24
        Layout.rightMargin:24
        Label {
            text: backend.get_element_loc("linked_settings")
            font: Typography.bodyStrong
            Layout.topMargin: 15
        }
        IconButton{
            text: backend.get_element_loc("linked_open_component_url")
            icon.name: FluentIcons.graph_OpenInNewWindow
            icon.width: 18
            icon.height: 18
            spacing: 5
            LayoutMirroring.enabled: true
            onClicked: {
                Qt.openUrlExternally("https://github.com/xvzc/SpoofDPI")
            }
        }
        IconButton{
            text: backend.get_element_loc("linked_manage_components")
            icon.name: FluentIcons.graph_ChevronRight
            icon.width: 18
            icon.height: 18
            spacing: 5
            LayoutMirroring.enabled: true
            onClicked: {
                page_router.go("/system")
            }
        }
    }

    Component.onCompleted: {
        text = backend.get_from_config("SPOOFDPI", modelData.optionId + "_value")
        settingsModel.setProperty(itemIndex, "value", text)

        generateCommandLine()
        
    }

    function generateCommandLine(blacklist_values=blacklistFilesModel) {
        var command = "spoofdpi-windows-amd64.exe"
        for (var i = 0; i < settingsModel.count; i++) {
            var item = settingsModel.get(i)

            if (item.type === "switch" && item.checked) {
                switch (item.optionId) {
                    case "enableDebug":
                        command += " -debug"
                        break
                    case "enableDOH":
                        command += " -enable-doh"
                        break
                    case "ipv4Only":
                        command += " -dns-ipv4-only"
                        break
                    case "silent":
                        command += " -silent"
                        break
                    case "systemProxy":
                        command += " -system-proxy"
                        break
                }
            } else if (item.type === "input" && item.checked && item.value.trim() !== "") {
                switch (item.optionId) {
                    case "addr":
                        command += " -addr " + item.value
                        break
                    case "dns":
                        command += " -dns-addr " + item.value
                        break
                    case "dnsPort":
                        command += " -dns-port " + item.value
                        break
                    case "port":
                        command += " -port " + item.value
                        break
                    case "pattern":
                        command += " -pattern " + item.value
                        break
                    case "timeout":
                        command += " -timeout " + item.value
                        break
                    case "windowSize":
                        command += " -window-size " + item.value
                        break
                }
            }
        }
        if (customParameters.text.trim() !== "") {
            command += " " + customParameters.text.trim()
        }

        commandLineOutput.text = command
    }
    function download_component() {
        progressBar.visible = true;
        checkBtn.enabled = false;
        timeLabel.visible = false;
        mainLabel.text = backend.get_element_loc('component_not_installed_p');
        errorLabel.visible = true;
        errorLabel.text = "";
        process.stop_process()
        backend.download_component("spoofdpi", false);
    }
    Connections {
        target: backend
        onComponent_installing_finished: {
            var success = arguments[0];
            progressBar.visible = false;
            checkBtn.enabled = true;
            console.log(success);
            if (success === 'True') {
                pageLoader.sourceComponent = null;
                pageLoader.sourceComponent = pageComponent;
            } else {
                checkBtn.enabled = true;
                checkBtn.text = backend.get_element_loc("retry");
                errorLabel.visible = true;
                errorLabel.text = success;
                mainLabel.text = backend.get_element_loc('component_not_installed_e');
            }
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
Connections{
    target:systemProcessHelper
    function onProcessCheckedStarted(){
        checkBtn.enabled = false
    }
    function onProcessCheckedStopped(){
        checkBtn.enabled = true
    }
}
Connections {
        target:multiWindow
        function onMulti_window_init(id) {
            if (id === title  && window.title !== title) {
                page_router.go("/")
            }
        }
    }

}

