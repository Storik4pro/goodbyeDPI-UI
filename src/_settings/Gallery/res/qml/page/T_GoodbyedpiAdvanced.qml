import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery
import QtQuick.Dialogs 

ScrollablePage {
    id: page
    header: Item{}
    title: backend.get_element_loc('advanced')

    ListModel {
        id: blacklistFilesModel
        onCountChanged: {
            generateCommandLine()
        }
    }

    InfoBarManager{
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }

    ColumnLayout {
        id: mainLayoutt
        anchors.margins: 20
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
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
                            text:backend.get_element_loc('advanced_attention')
                            font: Typography.body
                            wrapMode:WrapAnywhere
                        }
                        Button{
                            text: backend.get_element_loc('fixnow')
                            FluentUI.radius:0
                            onClicked:{
                                backend.toggleBool('GLOBAL', 'use_advanced_mode', true)
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
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    
                    Loader {
                        id: itemLoader
                        
                        anchors.fill: parent
                        sourceComponent: type === "blacklist" ? blacklistItemComponent : defaultItemComponent
                        property int itemIndex: index
                        property var modelData: model
                    }
                }
            }

            Label {
                text: backend.get_element_loc("custom_params")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            Rectangle {
                Layout.preferredHeight: 80
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
                                var allowedCharsRegex = /^[0-9a-zA-Z:"><\/\\.\-\_\s]*$/
                                if (!allowedCharsRegex.test(text)) {
                                    var cursorPosition = customParameters.cursorPosition - 1
                                    text = text.slice(0, cursorPosition) + text.slice(cursorPosition + 1)
                                    customParameters.cursorPosition = cursorPosition
                                    info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                } else {
                                    saveCustomParameters()
                                    generateCommandLine()
                                }
                                
                                 
                            }
                            
                            isInitializing = false

                        }
                        
                        Component.onCompleted: {
                            text = backend.getValue("GOODBYEDPI", "custom_parameters")
                            generateCommandLine()
                        }
                        function saveCustomParameters() {
                            var params = customParameters.text.trim()
                            backend.changeValue("GOODBYEDPI", "custom_parameters", params)
                        }
                        
                    }
                }
            }

            Label {
                text: backend.get_element_loc("output_prompt")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            Rectangle {
                id:rest
                Layout.preferredHeight: 80
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                color: "#1E1E1E"
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 0
                visible:true

                ScrollView {
                    anchors.fill: parent
                    anchors{
                        leftMargin:10
                        rightMargin:10
                        topMargin:10
                        bottomMargin:10
                    }
                    contentWidth: parent.width-20

                    CopyableText {
                        id: commandLineOutput
                        width:parent.width
                        text: command
                        wrapMode: Text.WordWrap
                        font.pixelSize: 14
                        font.family: "Cascadia Code"
                        color: "#D4D4D4"
                    }
                }
            }
        }
    
    }
    
    

    Component {
        id: defaultItemComponent
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
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
                                    backend.toggleBool("GOODBYEDPI", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                            }
                            Component.onCompleted: {
                                checked = backend.getBool("GOODBYEDPI", modelData.optionId)
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
                                            backend.changeValue("GOODBYEDPI", modelData.optionId + "_value", text)
                                            generateCommandLine()
                                        }
                                    }    
                                }
                                
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                if (modelData.type === "input") {
                                    text = backend.getValue("GOODBYEDPI", modelData.optionId + "_value")
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
                            FluentUI.radius:0
                            onCheckedChanged: {
                                if (!isInitializing) {
                                    settingsModel.setProperty(modelData.index, "checked", checked)
                                    backend.toggleBool("GOODBYEDPI", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                                isInitializing = false
                                console.log(isInitializing)
                            }
                            Component.onCompleted: {
                                checked = backend.getBool("GOODBYEDPI", modelData.optionId)
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
                        var filesString = backend.getValue("GOODBYEDPI", "blacklist_value")
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
        backend.changeValue("GOODBYEDPI", "blacklist_value", pathsString)
        return filesModel;
    }

    function blacklistFilesModelContains(filePath) {
        var allowedCharsRegex = /^[0-9a-zA-Z:"\/\\.\-\_\s]*$/
        console.log(allowedCharsRegex, filePath)
        if (!allowedCharsRegex.test(filePath)) {
            info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_file"), 3000)
            return true
        }
        for (var i = 0; i < blacklistFilesModel.count; i++) {
            if (blacklistFilesModel.get(i).path === filePath) {
                return true
            }
            
        }
        return false
    }

    Component.onCompleted: {
        if (!Qt.fontFamilies().contains("Cascadia Code")) {
            font.family = Qt.fontFamilies().filter(f => f.toLowerCase().indexOf("mono") !== -1)[0] || "Courier New"
        }
        text = backend.getValue("GOODBYEDPI", modelData.optionId + "_value")
        settingsModel.setProperty(itemIndex, "value", text)

        var filesString = backend.getValue("GOODBYEDPI", "blacklist_value")
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
                    backend.getValue("GOODBYEDPI", "blacklist_value")
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

