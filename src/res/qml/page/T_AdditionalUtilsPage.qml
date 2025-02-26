import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    title: backend.get_element_loc('additional')
    id:page
    header:Item{}
    property var goodbyeDPI_model: [
        "[basic functionality test]",
        "[IPv4] - [e1 + e2 + e4] - [LONG]",
        "[IPv4] - [e1 + e2 + e4] - [SHORT]",
        "[IPv4] - [e1] - [LONG]",
        "[IPv4] - [e1] - [SHORT]",
        "[IPv4] - [e2] - [LONG]",
        "[IPv4] - [e2] - [SHORT]",
        "[IPv4] - [e4] - [LONG]",
        "[IPv4] - [e4] - [SHORT]",
        "[IPv6] - [e1 + e2 + e4] - [LONG]",
        "[IPv6] - [e1 + e2 + e4] - [SHORT]",
        "[IPv6] - [e1] - [LONG]",
        "[IPv6] - [e1] - [SHORT]",
        "[IPv6] - [e2] - [LONG]",
        "[IPv6] - [e2] - [SHORT]",
        "[IPv6] - [e4] - [LONG]",
        "[IPv6] - [e4] - [SHORT]",
        ]
    property var zapret_model: [
        "[IPv4] - [TCP] - [No wssize, NO syndata]",
        "[IPv4] - [UDP]",
        "[IPv6] - [UDP]",
    ]
    Dialog {
        id: goodCheckDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: Math.max(500, Math.ceil(parent.width / 3)) 
        contentHeight: parent.height < 500 ? Math.ceil(parent.height / 1.5) :parent.height - 300
        parent: Overlay.overlay
        modal: true
        title: "GoodCheck by Ori"
        Flickable {
            id: flickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: column.implicitHeight
            ColumnLayout {
                id:column
                anchors.fill: parent
                anchors.rightMargin:10
                anchors.leftMargin:10
                spacing: 5
                width:400
                Rectangle {
                    id:rest1
                    Layout.preferredHeight: Math.max(60, infoColumnLayout.implicitHeight + 20)
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    color: Theme.res.controlFillColorDefault
                    radius: 6
                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)

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
                                    text:backend.get_element_loc('beta')
                                    font: Typography.body
                                    wrapMode:Text.Wrap
                                }
                            }

                        }
                    }
                }

                Label {
                    Layout.preferredWidth:column.width-10
                    text: backend.get_element_loc("goodcheck_info")
                    wrapMode:Text.Wrap
                }
                Label {
                    Layout.preferredWidth:column.width-10
                    text: backend.get_element_loc("goodcheck_start_settins")
                    font:Typography.bodyLarge
                    wrapMode:Text.Wrap
                }
                Label {
                    text: backend.get_element_loc("engine")
                    font: Typography.bodyStrong
                    Layout.fillWidth:true
                    wrapMode: Text.Wrap
                    height:20
                    Layout.maximumHeight:20
                    Layout.preferredWidth: parent.width
                }
                ComboBox{
                    id: engine
                    Layout.preferredWidth:column.width
                    model: ["GoodbyeDPI", "Zapret"]
                    currentIndex: backend.get_from_config("GOODCHECK", "engine") === "GoodbyeDPI" ? 0:1
                    onActivated: {
                        let selectedValue = model[currentIndex];
                        backend.set_to_config("GOODCHECK", "engine", selectedValue)
                    }
                }
                Label {
                    text: backend.get_element_loc("curl")
                    font: Typography.bodyStrong
                    Layout.fillWidth:true
                    wrapMode: Text.Wrap
                    height:20
                    Layout.maximumHeight:20
                    Layout.preferredWidth: parent.width
                }
                ComboBox{
                    Layout.preferredWidth:column.width
                    model: ["Native", "Curl"]
                    currentIndex: backend.get_from_config("GOODCHECK", "curl") === "Native" ? 0:1
                    onActivated: {
                        let selectedValue = model[currentIndex];
                        backend.set_to_config("GOODCHECK", "curl", selectedValue)
                    }
                }
                Label {
                    text: backend.get_element_loc("check_list")
                    font: Typography.bodyStrong
                    Layout.fillWidth:true
                    wrapMode: Text.Wrap
                    height:20
                    Layout.maximumHeight:20
                    Layout.preferredWidth: parent.width
                }
                RowLayout{
                    spacing:0
                    ComboBox{
                        id:cmbox
                        Layout.preferredWidth:column.width - height - 5
                        model: [backend.get_element_loc("goodcheck_all"), backend.get_element_loc("goodcheck_googlevideo"), 
                        backend.get_element_loc("goodcheck_miscellaneous"), backend.get_element_loc("goodcheck_nothing"), backend.get_element_loc("goodcheck_twitter")]
                        currentIndex: backend.get_int_from_config("GOODCHECK", "check_list")
                        onActivated: {
                            let selectedValue = model[currentIndex];
                            backend.set_to_config("GOODCHECK", "check_list", currentIndex)
                        }
                    }
                    Button {
                        text: backend.get_element_loc("edit")
                        icon.name:FluentIcons.graph_Edit
                        icon.height:20
                        icon.width:20
                        Layout.preferredHeight:cmbox.height
                        Layout.preferredWidth:cmbox.height
                        Layout.leftMargin:5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text

                        display:Button.IconOnly
                        onClicked: {
                            goodCheck.open_goodcheck_file(cmbox.currentIndex);
                        }
                    }
                }
                Label {
                    text: backend.get_element_loc("strategies")
                    font: Typography.bodyStrong
                    Layout.fillWidth:true
                    wrapMode: Text.Wrap
                    height:20
                    Layout.maximumHeight:20
                    Layout.preferredWidth: parent.width
                }
                ComboBox{
                    Layout.preferredWidth:column.width
                    model: engine.currentIndex === 0 ? goodbyeDPI_model : zapret_model
                    currentIndex: backend.get_int_from_config("GOODCHECK", "strategies")
                    onActivated: {
                        let selectedValue = model[currentIndex];
                        backend.set_to_config("GOODCHECK", "strategies", currentIndex)
                    }
                }


                Label {
                    Layout.preferredWidth:column.width-10
                    text: backend.get_element_loc("goodcheck_settins")
                    font:Typography.bodyLarge
                    wrapMode:Text.Wrap
                }

                ListModel {
                    id: settingsModel

                    ListElement { text: "ConnectionTimeout"; optionId: "ConnectionTimeout"; optionGroup: "General"; value: "1"; placeholder: ""; type: "input" }
                    ListElement { text: "AutomaticGoogleCacheTest"; optionId: "AutomaticGoogleCacheTest"; optionGroup: "General"; checked: true; type: "switch" }
                    ListElement { text: "UseDoH"; optionId: "UseDoH"; optionGroup: "Resolvers"; checked: true; type: "switch" }
                    ListElement { text: "DoHResolvers"; optionId: "DoHResolvers"; optionGroup: "Resolvers"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeSNI"; optionId: "FakeSNI"; optionGroup: "Fakes"; value: "fonts.google.com"; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexStreamTCP"; optionId: "FakeHexStreamTCP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexStreamUDP"; optionId: "FakeHexStreamUDP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexBytesTCP"; optionId: "FakeHexBytesTCP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexBytesUDP"; optionId: "FakeHexBytesUDP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "AutomaticConnectivityTest"; optionId: "AutomaticConnectivityTest"; optionGroup: "Advanced"; checked: true; type: "switch" }
                    ListElement { text: "ConnectivityTestURL"; optionId: "ConnectivityTestURL"; optionGroup: "Advanced"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "SkipCertVerify"; optionId: "SkipCertVerify"; optionGroup: "Advanced"; checked: false; type: "switch" }
                    ListElement { text: "GoogleCacheMappingURLs"; optionId: "GoogleCacheMappingURLs"; optionGroup: "Advanced"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "InternalTimeoutMs"; optionId: "InternalTimeoutMs"; optionGroup: "Advanced"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "ResolverNativeTimeout"; optionId: "ResolverNativeTimeout"; optionGroup: "Advanced"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "ResolverNativeRetries"; optionId: "ResolverNativeRetries"; optionGroup: "Advanced"; value: ""; placeholder: ""; type: "input" }


                }
                Repeater {
                    model: settingsModel
                    
                    delegate: ColumnLayout {
                        height:40
                        Layout.fillWidth: true
                        Layout.preferredWidth: column.width
                        Layout.alignment: Qt.AlignHCenter
                        
                        Loader {
                            id: itemLoader
                            
                            Layout.preferredWidth: column.width
                            Layout.preferredHeight: modelData.type === "switch" ? 35:60
                            sourceComponent: defaultItemComponent
                            property int itemIndex: index
                            property var modelData: model
                        }
                    }
                }
            
                
            }
            ScrollBar.vertical: ScrollBar {
                id: verticalScrollBar
                orientation: Qt.Vertical
                
                visible:true
                anchors.top: flickable.top
                anchors.bottom: flickable.bottom
                
            }


        }
        footer: DialogButtonBox{
        Button{
            text: backend.get_element_loc("start")
            highlighted: true
            onClicked: {
                var success = process.stop_process()
                //process.stop_service()
                goodCheck.start()
                goodCheckDialog.close()
            }
        }
        Button{
            text: backend.get_element_loc("cancel")
            onClicked: {
                goodCheckDialog.close()
            }
        }
        }
    }
    Component {
        id: defaultItemComponent
        Rectangle {
            id:rest
            Layout.fillWidth: true
            Layout.preferredHeight: itemLabel.height + 5
            color: Qt.rgba(0, 0, 0, 0.0)
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.0)
            radius: 4

            ColumnLayout {
                anchors.fill: parent
                spacing: modelData.type !== "switch" ? 5 : 0

                Label {
                    id:itemLabel
                    text: backend.get_element_loc(modelData.optionId+"_text")
                    font: Typography.bodyStrong
                    Layout.fillWidth:true
                    wrapMode: Text.Wrap
                    height:20
                    Layout.maximumHeight:20
                    Layout.preferredWidth: parent.width
                    visible:modelData.type !== "switch"
                }

                Item {
                    id:item
                    Layout.preferredWidth: rest.width
                    Layout.fillHeight:true
                    Layout.alignment: Qt.AlignLeft
                    Layout.leftMargin: 10

                    ColumnLayout {
                        TextField {
                            id: inputField
                            text: modelData.value
                            placeholderText: modelData.placeholder
                            inputMethodHints: Qt.ImhDigitsOnly
                            enabled: true
                            Layout.preferredWidth: rest.width
                            Layout.leftMargin:-10
                            visible: modelData.type === "input"
                            property bool isInitializing: true

                            onTextChanged: {
                                if (!isInitializing) {
                                    if (modelData.type === "input") {
                                        settingsModel.setProperty(modelData.index, "value", text)
                                        goodCheck.set_value(modelData.optionGroup, modelData.optionId, text)
                                    }    
                                }
                                
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                if (modelData.type === "input") {
                                    text = goodCheck.get_value(modelData.optionGroup, modelData.optionId)
                                }
                                settingsModel.setProperty(modelData.index, "value", text)
                                isInitializing = false
                            }
                        }

                        CheckBox {
                            id: switchControl
                            checked: modelData.checked 
                            text: backend.get_element_loc(modelData.optionId+"_text")
                            font:Typography.bodyStrong
                            visible: modelData.type === "switch"
                            property bool isInitializing : false
                            Layout.rightMargin:20
                            onClicked: {
                                if (!isInitializing) {
                                    settingsModel.setProperty(modelData.index, "checked", checked)
                                    goodCheck.set_value(modelData.optionGroup, modelData.optionId, checked)
                                }
                                isInitializing = false
                            }
                            Component.onCompleted: {
                                checked = goodCheck.get_bool(modelData.optionGroup, modelData.optionId)
                                settingsModel.setProperty(modelData.index, "checked", checked)
                                isInitializing = false
                            }
                        }
                    }
                }
            
            }
        }
    }
    ColumnLayout {
        Layout.fillWidth: true
        
        Layout.alignment: Qt.AlignHCenter

        Button{
            id:btn1
            Layout.preferredHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            enabled: backend.check_winpty()
            RowLayout{
                anchors.fill: parent
                anchors{
                    leftMargin: 20
                    rightMargin: 20
                }
                spacing: 10
                ColumnLayout{
                    Layout.fillWidth: true
                    spacing: 2
                    Label{
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignLeft
                        text: backend.get_element_loc('see_output')
                        font: Typography.body
                        wrapMode:Text.Wrap
                    }
                    Label {
                        Layout.fillWidth:true
                        text: backend.get_element_loc('see_output_tip')
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.caption
                        color: "#c0c0c0"
                        wrapMode:Text.Wrap
                    }
                }
                IconButton {
                    id: btn_icon
                    width: 30
                    height: 30
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    Icon {
                        anchors.centerIn: parent
                        source: FluentIcons.graph_OpenInNewWindow
                        width: 15
                        height: 15
                    }
                    onClicked: {
                        WindowRouter.go("/pseudoconsole")
                    }
                }
            }
            
            onClicked: {
                WindowRouter.go("/pseudoconsole")
            }
        }
        Button{
            Layout.preferredHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            enabled: true
            RowLayout{
                anchors.fill: parent
                anchors{
                    leftMargin: 20
                    rightMargin: 20
                }
                spacing: 10
                ColumnLayout{
                    Layout.fillWidth: true
                    spacing: 2
                    Label{
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignLeft
                        text: backend.get_element_loc('proxy_setup')
                        font: Typography.body
                        wrapMode:Text.Wrap
                    }
                    Label {
                        Layout.fillWidth:true
                        text: backend.get_element_loc('proxy_setup_tip')
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.caption
                        color: "#c0c0c0"
                        wrapMode:Text.Wrap
                    }
                }
                Button {
                    width: 30
                    height: 30
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    text: backend.get_element_loc("setup_btn")
                    onClicked: {
                        page_router.go("/proxy")
                    }
                }
            }
            
            onClicked: {
                page_router.go("/proxy")
            }
        }
        Button{
            id:btn2
            Layout.preferredHeight: 68
            Layout.fillWidth:true
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            visible: backend.getBool('GLOBAL', 'usebetafeatures')
            RowLayout{
                anchors.fill: parent
                anchors{
                    leftMargin: 20
                    rightMargin: 20
                }
                spacing: 10
                ColumnLayout{
                    Layout.fillWidth: true
                    spacing: 2
                    Label{
                        Layout.fillWidth: true
                        text: backend.get_element_loc('chk_preset')
                        horizontalAlignment: Text.AlignLeft
                        wrapMode:Text.Wrap
                        font: Typography.body
                    }
                    Label {
                        text: backend.get_element_loc('chk_preset_tip')
                        Layout.fillWidth: true
                        font: Typography.caption
                        color: "#c0c0c0"
                        horizontalAlignment: Text.AlignLeft
                        wrapMode:Text.Wrap
                    }
                }
                IconButton {
                    id: btn_icon1
                    width: 30
                    height: 30
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    Icon {
                        anchors.centerIn: parent
                        source: FluentIcons.graph_OpenInNewWindow
                        width: 15
                        height: 15
                    }
                    onClicked: {
                        goodCheckDialog.open()
                    }
                }
            }
            
            onClicked: {
                goodCheckDialog.open()
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