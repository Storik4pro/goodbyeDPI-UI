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
    title: backend.get_element_loc("settings")+" zapret"

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
            visible: backend.getValue('GLOBAL', 'engine') === "zapret" ? false : true 
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
                            text:backend.get_element_loc('warn1')
                            font: Typography.body
                            wrapMode:WrapAnywhere
                        }
                        Button{
                            text: backend.get_element_loc('fixnow')
                            FluentUI.radius:0
                            onClicked:{
                                backend.changeValue('GLOBAL', 'engine', "zapret")
                                rest1.visible = false
                            }
                        }
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
                        text: backend.get_element_loc("preset")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.body
                        wrapMode: Text.Wrap
                    }

                    Label {
                        id:lbl2
                        Layout.fillWidth: true
                        text: backend.get_element_loc("preset_tip")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.caption
                        color: "#c0c0c0"
                        wrapMode: Text.Wrap
                    }
                }

                ComboBox {
                    Layout.preferredWidth: 300
                    Layout.fillWidth: false
                    model: [
                        "<separator>" + backend.get_element_loc("standart"),
                        "1. " + backend.get_element_loc("qpreset_1"),
                        "2. " + backend.get_element_loc("qpreset_2"),
                        "3. " + backend.get_element_loc("qpreset_3")+ " (" + backend.get_element_loc("recommended") + ")",
                        "4. " + backend.get_element_loc("qpreset_4")+ " (" + backend.get_element_loc("alt") + ")",
                    ]
                    currentIndex: backend.getInt("ZAPRET", "preset")
                    onCurrentIndexChanged: {
                        let selectedValue = model[currentIndex];
                        backend.zapret_update_preset(selectedValue);
                    }

                    focus: false
                    focusPolicy: Qt.NoFocus
                }
            }
        }

        Label {
            text: backend.get_element_loc("zapret_advansed")
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
                    text: backend.get_element_loc("zapret_manual_input")
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
                    property bool isInitializing: backend.getBool('ZAPRET', 'use_advanced_mode') 
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 0
                    }
                    text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                    checked: backend.getBool('ZAPRET', 'use_advanced_mode')
                    onCheckedChanged: {
                        if (!isInitializing){
                            backend.toggleBool('ZAPRET', 'use_advanced_mode', checked)
                        }
                        isInitializing = false
                    }
                }
            }
        }

        ColumnLayout {
            id: mainLayout
            anchors.margins: 20
            spacing: 3
            width: parent.width

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
                                var allowedCharsRegex = /^[0-9a-zA-Z:"><\/\\.\-\_\s,]*$/
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
                            text = backend.getValue("ZAPRET", "custom_parameters")
                            generateCommandLine()
                        }
                        function saveCustomParameters() {
                            var params = customParameters.text.trim()
                            backend.changeValue("ZAPRET", "custom_parameters", params)
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
                                    backend.toggleBool("ZAPRET", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                            }
                            Component.onCompleted: {
                                checked = backend.getBool("ZAPRET", modelData.optionId)
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
                                        var allowedCharsRegex = /^[0-9a-zA-Z:\/\\.\-\_\s,]*$/
                                        if (!allowedCharsRegex.test(text)) {
                                            var cursorPosition = inputField.cursorPosition - 1
                                            text = text.slice(0, cursorPosition) + text.slice(cursorPosition + 1)
                                            inputField.cursorPosition = cursorPosition
                                            info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                        } else {
                                            settingsModel.setProperty(modelData.index, "value", text)
                                            backend.changeValue("ZAPRET", modelData.optionId + "_value", text)
                                            generateCommandLine()
                                        }
                                    }    
                                }
                                
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                if (modelData.type === "input") {
                                    text = backend.getValue("ZAPRET", modelData.optionId + "_value")
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
                                    backend.toggleBool("ZAPRET", modelData.optionId, checked)
                                    generateCommandLine()
                                }
                                isInitializing = false
                                console.log(isInitializing)
                            }
                            Component.onCompleted: {
                                checked = backend.getBool("ZAPRET", modelData.optionId)
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


    Component.onCompleted: {
        if (!Qt.fontFamilies().contains("Cascadia Code")) {
            font.family = Qt.fontFamilies().filter(f => f.toLowerCase().indexOf("mono") !== -1)[0] || "Courier New"
        }
        text = backend.getValue("ZAPRET", modelData.optionId + "_value")
        settingsModel.setProperty(itemIndex, "value", text)

        generateCommandLine()
        
    }

    function generateCommandLine(blacklist_values=blacklistFilesModel) {
        var command = "winws.exe"

        if (customParameters.text.trim() !== "") {
            command += " " + customParameters.text.trim()
        }

        commandLineOutput.text = command
    }

}

