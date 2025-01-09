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
    title: backend.get_element_loc('advanced')
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
            backend.save_preset('goodbyedpi', filePath)
            process.update_preset()
        }
    }


    FileDialog {
        id: fileDialogOpen
        title: backend.get_element_loc("choose_file")
        nameFilters: [
            backend.get_element_loc("all_files_tip")+" (*.json; *.bat; *.cmd)",
            backend.get_element_loc("json_files_tip")+" (*.json)",
            backend.get_element_loc("bat_files_tip")+" (*.bat; *.cmd)",
        ]
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            var result = backend.load_preset('goodbyedpi', filePath)

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

    

    ColumnLayout {
        id: mainLayoutt
        Layout.leftMargin:24
        Layout.rightMargin:24
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        Rectangle {
            id:rest11
            Layout.preferredHeight: Math.max(100, infoColumnLayout.implicitHeight + 20)
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 0
            visible: backend.getValue('GLOBAL', 'engine') === "goodbyeDPI" ? false : true 
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
                            FluentUI.radius:0
                            onClicked:{
                                process.change_engine("goodbyeDPI")
                                rest11.visible = false
                            }
                        }
                    }

                }
            }
        }
        Rectangle {
            id:rest1
            Layout.preferredHeight: 100
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 0
            visible: !backend.getBool('GLOBAL', 'use_advanced_mode')
            ColumnLayout{
                anchors.verticalCenter: parent.verticalCenter  
                RowLayout{
                    
                    spacing:10
                    height:20
                    anchors{
                        left: parent.left
                        leftMargin:10
                    }
                    Icon{
                        id: icon_info12
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
                            text:backend.get_element_loc('advanced_attention')
                            font: Typography.body
                            wrapMode:WrapAnywhere
                        }
                        Button{
                            text: backend.get_element_loc('fixnow')
                            FluentUI.radius:0
                            onClicked:{
                                
                                backend.toggleBool('GLOBAL', 'use_advanced_mode', true)
                                process.update_preset()
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

                ListElement { text: "-p  "; optionId: "blockPassiveDPI"; checked: false; type: "switch" }
                ListElement { text: "-q  "; optionId: "blockQUIC"; checked: false; type: "switch" }
                ListElement { text: "-r  "; optionId: "replaceHost"; checked: false; type: "switch" }
                ListElement { text: "-s  "; optionId: "removeSpace"; checked: false; type: "switch" }
                ListElement { text: "-m  "; optionId: "mixHostCase"; checked: false; type: "switch" }
                ListElement { text: "-n  "; optionId: "doNotWaitAck"; checked: false; type: "switch" }
                ListElement { text: "-a  "; optionId: "additionalSpace"; checked: false; type: "switch" }
                ListElement { text: "-w  "; optionId: "processAllPorts"; checked: false; type: "switch" }
                ListElement { text: "--allow-no-sni  "; optionId: "allowNoSNI"; checked: false; type: "switch" }
                ListElement { text: "--dns-verb  "; optionId: "dnsVerbose"; checked: false; type: "switch" }
                ListElement { text: "--wrong-chksum  "; optionId: "wrongChecksum"; checked: false; type: "switch" }
                ListElement { text: "--wrong-seq  "; optionId: "wrongSeq"; checked: false; type: "switch" }
                ListElement { text: "--native-frag  "; optionId: "nativeFrag"; checked: false; type: "switch" }
                ListElement { text: "--reverse-frag  "; optionId: "reverseFrag"; checked: false; type: "switch" }

                ListElement { text: "-f  "; optionId: "httpFragmentation"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "-k  "; optionId: "httpKeepAlive"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "-e  "; optionId: "httpsFragmentation"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "--max-payload"; optionId: "maxPayload"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "--port"; optionId: "additionalPort"; value: ""; placeholder: "Port"; type: "input" }
                ListElement { text: "--ip-id"; optionId: "ipId"; value: ""; placeholder: "ID"; type: "input" }
                ListElement { text: "--dns-addr"; optionId: "dns"; value: ""; placeholder: "IP addres"; type: "input" }
                ListElement { text: "--dns-port"; optionId: "dns_port"; value: ""; placeholder: "Port"; type: "input" }
                ListElement { text: "--dnsv6-addr"; optionId: "dnsv6"; value: ""; placeholder: "IPv6 addres"; type: "input" }
                ListElement { text: "--dnsv6-port"; optionId: "dnsv6_port"; value: ""; placeholder: "Port"; type: "input" }
                ListElement { text: "--blacklist"; optionId: "blacklist"; type: "blacklist" }
                ListElement { text: "--set-ttl"; optionId: "setTTL"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "--auto-ttl"; optionId: "autoTTL"; value: ""; placeholder: "a1-a2-m"; type: "input" }
                ListElement { text: "--min-ttl"; optionId: "minTTL"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "--fake-from-hex"; optionId: "fakeFromHex"; value: ""; placeholder: "HEX value"; type: "input" }
                ListElement { text: "--fake-gen"; optionId: "fakeGen"; value: ""; placeholder: "Digital value"; type: "input" }
                ListElement { text: "--fake-resend"; optionId: "fakeResend"; value: ""; placeholder: "Digital value"; type: "input" }

            }
            Repeater {
                model: settingsModel
                
                delegate: ColumnLayout {
                    Layout.preferredHeight: type === "blacklist" ? undefined : 40 
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    
                    Loader {
                        id: itemLoader
                        
                        Layout.preferredWidth:parent.width
                        Layout.preferredHeight:type === "blacklist" ? sourceComponent.implicitHeight: parent.height
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
                            text:process.get_config_name('goodbyedpi')
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
                                backend.return_to_default('goodbyedpi')
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
                radius: 0

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
                        FluentUI.radius:0
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
                            text = backend.get_from_config("GOODBYEDPI", "custom_parameters")
                            generateCommandLine()
                        }
                        function saveCustomParameters() {
                            var params = customParameters.text.trim()
                            backend.set_to_config("GOODBYEDPI", "custom_parameters", params)
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
                    radius: 0
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
    
    

    Component {
        id: defaultItemComponent
        Rectangle {
            color: modelData.index % 2 === 0 ? Theme.res.subtleFillColorSecondary : Theme.res.subtleFillColorTertiary
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 0

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Label {
                    text: backend.get_element_loc(modelData.optionId+"_text")
                    font: Typography.body
                    Layout.fillWidth: true
                    verticalAlignment: Text.AlignVCenter
                }

                Item {
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
                                    backend.set_to_config("GOODBYEDPI", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                            }
                            Component.onCompleted: {
                                checked = backend.get_bool_from_config("GOODBYEDPI", modelData.optionId)
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
                            visible: modelData.type === "input"
                            property bool isInitializing: true
                            FluentUI.radius:0

                            onTextChanged: {
                                if (!isInitializing) {
                                    if (modelData.type === "input") {
                                        var allowedCharsRegex = /^[0-9a-zA-Z:\/\\.\-\_\s]*$/
                                        if (!allowedCharsRegex.test(text)) {
                                            var cursorPosition = inputField.cursorPosition - 1
                                            text = text.slice(0, cursorPosition) + text.slice(cursorPosition + 1)
                                            inputField.cursorPosition = cursorPosition
                                            info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                        } else {
                                            settingsModel.setProperty(modelData.index, "value", text)
                                            backend.set_to_config("GOODBYEDPI", modelData.optionId + "_value", text)
                                            generateCommandLine()
                                        }
                                    }    
                                }
                                
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                if (modelData.type === "input") {
                                    text = backend.get_from_config("GOODBYEDPI", modelData.optionId + "_value")
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
                            Layout.rightMargin:10
                            onCheckedChanged: {
                                if (!isInitializing) {
                                    settingsModel.setProperty(modelData.index, "checked", checked)
                                    backend.set_to_config("GOODBYEDPI", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                                isInitializing = false
                                console.log(isInitializing)
                            }
                            Component.onCompleted: {
                                checked = backend.get_bool_from_config("GOODBYEDPI", modelData.optionId)
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

    Component {
        id: blacklistItemComponent
        
        Expander {
            id: expanderComp
            property bool isInitializing: true
            expanded: true 
            Layout.fillWidth: true 
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter 
            
            _radius:0
            _height:40
            
            FileDialog {
                id: fileDialog
                title: qsTr("Choose .txt file")
                nameFilters: ["Text files (*.txt)"]
                onAccepted: {
                    var filePath = urlReadyToSave("\""+selectedFile+"\"")
                    console.log(filePath)
                    if (!blacklistFilesModelContains(filePath)) {
                        blacklistFilesModel.append({ path: filePath })
                        saveBlacklistFiles()
                        generateCommandLine()
                    }
                }
            }
            header: Label {
                text: qsTr("--blacklist")
                font: Typography.body
                horizontalAlignment: Qt.AlignHCenter
                Layout.fillWidth: true
            }

            trailing:  Button {
                id: trl
                text: backend.get_element_loc("add_file")
                icon.name: FluentIcons.graph_OpenFile 
                height:30
                onClicked: {
                    fileDialog.open()
                }
                FluentUI.radius:0
            }

            content: ColumnLayout {
                id:cnt
                spacing: 5
                Layout.fillWidth: true

                Component.onCompleted: {
                    if (isInitializing) {
                        var filesString = backend.get_from_config("GOODBYEDPI", "blacklist_value")
                        if (filesString !== "") {
                            var filesArray = filesString.split(",")
                            for (var i = 0; i < filesArray.length; i++) {
                                var filePath = filesArray[i]
                                if (filePath !== "") {
                                    blacklistFilesModel.append({ path: filePath })
                                }
                            }
                        }
                        generateCommandLine()
                    }
                    isInitializing = false
                }

                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: 15
                }

                Rectangle {
                    width: parent.width
                    height: 10
                    Layout.bottomMargin: 5
                    opacity: 0.0
                }
                CopyableText {
                    text:backend.get_element_loc("file_info")
                    visible:0 === (blacklistFilesModel.count)
                }
                Repeater {
                    model: blacklistFilesModel

                    ColumnLayout {
                        spacing: 0
                        Layout.fillWidth: true
                        

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            CopyableText {
                                id:lbl
                                text: model.path
                                Layout.fillWidth:true
                            }

                            Button {
                                text: backend.get_element_loc("open")
                                FluentUI.radius:0
                                onClicked: {
                                    Qt.openUrlExternally(urlReady(model.path))
                                }
                            }

                            Button {
                                Layout.rightMargin: 25
                                text: backend.get_element_loc("delete")
                                FluentUI.radius:0
                                onClicked: {
                                    saveBlacklistFiles(index)
                                    Qt.callLater(function() {
                                        generateCommandLine()
                                    })
                                    blacklistFilesModel.remove(index)
                                    
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
                            visible: index < (blacklistFilesModel.count - 1)
                        }
                    }
                }
                Rectangle {
                    width: parent.width
                    height: 10
                    Layout.topMargin: 5
                    opacity: 0.0
                }

            }

            function urlReady(string){
                var modifiedString = "file:///" + string.slice(1, -1);
                return modifiedString;
            }

            function urlReadyToSave(string){
                var q_string = string.slice(1, -1);
                var modifiedString = "\"" + q_string.replace("file:///", "") + "\"";
                return modifiedString;
            }
            
        }
    }

    function saveBlacklistFiles(ind=-1) {
        var paths = []
        var filesModel = blacklistFilesModel;
        if (ind >= 0) filesModel.remove(ind)
        for (var i = 0; i < filesModel.count; i++) {
            paths.push(filesModel.get(i).path)
        }
        var pathsString = paths.join(",")
        console.log(pathsString)
        backend.set_to_config("GOODBYEDPI", "blacklist_value", pathsString)
        return filesModel;
    }

    function blacklistFilesModelContains(filePath) {
        for (var i = 0; i < blacklistFilesModel.count; i++) {
            if (blacklistFilesModel.get(i).path === filePath) {
                return true
            }
            
        }
        return false
    }

    Component.onCompleted: {
        text = backend.get_from_config("GOODBYEDPI", modelData.optionId + "_value")
        settingsModel.setProperty(itemIndex, "value", text)

        var filesString = backend.get_from_config("GOODBYEDPI", "blacklist_value")
        if (filesString !== "") {
            var filesArray = filesString.split(",")
            for (var i = 0; i < filesArray.length; i++) {
                var filePath = filesArray[i]
                if (filePath !== "") {
                    if (!blacklistFilesModelContains(filePath)) {
                        blacklistFilesModel.append({ path: filePath })
                    }
                }
            }
        }
        generateCommandLine()

        
    }

    function generateCommandLine(blacklist_values=blacklistFilesModel) {
        var command = "goodbyedpi.exe"

        for (var i = 0; i < settingsModel.count; i++) {
            var item = settingsModel.get(i)

            if (item.type === "switch" && item.checked) {
                switch (item.optionId) {
                    case "blockPassiveDPI":
                        command += " -p"
                        break
                    case "blockQUIC":
                        command += " -q"
                        break
                    case "replaceHost":
                        command += " -r"
                        break
                    case "removeSpace":
                        command += " -s"
                        break
                    case "mixHostCase":
                        command += " -m"
                        break
                    case "doNotWaitAck":
                        command += " -n"
                        break
                    case "additionalSpace":
                        command += " -a"
                        break
                    case "processAllPorts":
                        command += " -w"
                        break
                    case "allowNoSNI":
                        command += " --allow-no-sni"
                        break
                    case "dnsVerbose":
                        command += " --dns-verb"
                        break
                    case "wrongChecksum":
                        command += " --wrong-chksum"
                        break
                    case "wrongSeq":
                        command += " --wrong-seq"
                        break
                    case "nativeFrag":
                        command += " --native-frag"
                        break
                    case "reverseFrag":
                        command += " --reverse-frag"
                        break
                }
            } else if (item.type === "input" && item.checked && item.value.trim() !== "") {
                switch (item.optionId) {
                    case "httpFragmentation":
                        command += " -f " + item.value
                        break
                    case "httpKeepAlive":
                        command += " -k " + item.value
                        break
                    case "httpsFragmentation":
                        command += " -e " + item.value
                        break
                    case "maxPayload":
                        command += " --max-payload " + item.value
                        break
                    case "additionalPort":
                        command += " --port " + item.value
                        break
                    case "ipId":
                        command += " --ip-id " + item.value
                        break
                    case "dns":
                        command += " --dns-addr " + item.value
                        break
                    case "dns_port":
                        command += " --dns-port " + item.value
                        break
                    case "dnsv6":
                        command += " --dnsv6-addr " + item.value
                        break
                    case "dnsv6_port":
                        command += " --dnsv6-port " + item.value
                        break
                    case "blacklist":
                        command += " --blacklist " + item.value
                        break
                    case "setTTL":
                        command += " --set-ttl " + item.value
                        break
                    case "autoTTL":
                        command += " --auto-ttl " + item.value
                        break
                    case "minTTL":
                        command += " --min-ttl " + item.value
                        break
                    case "fakeFromHex":
                        command += " --fake-from-hex " + item.value
                        break
                    case "fakeGen":
                        command += " --fake-gen " + item.value
                        break
                    case "fakeResend":
                        command += " --fake-resend " + item.value
                        break
                }
            } else if (item.type === "blacklist") {
                
                if (blacklist_values.count > 0) {
                    backend.get_from_config("GOODBYEDPI", "blacklist_value")
                    for (var j = 0; j < blacklist_values.count; j++) {
                        var filePath = blacklist_values.get(j).path
                        command += ' --blacklist ' + filePath
                    }
                }
            }
        }

        if (customParameters.text.trim() !== "") {
            command += " " + customParameters.text.trim()
        }

        commandLineOutput.text = command
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
            if (id === title  && window.title !== title) {
                page_router.go("/")
            }
        }
    }
}
