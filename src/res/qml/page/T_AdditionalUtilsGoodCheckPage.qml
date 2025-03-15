import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI


ScrollablePage {
    title: backend.get_element_loc("chk_preset")
    id:page
    header:Item{}

    function _asyncToGenerator(fn) {
        return function() {
            var self = this,
            args = arguments
            return new Promise(function(resolve, reject) {
                var gen = fn.apply(self, args)
                function _next(value) {
                    _asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value)
                }
                function _throw(err) {
                    _asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err)
                }
                _next(undefined)
            })
        }
    }

    function _asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) {
        try {
            var info = gen[key](arg)
            var value = info.value
        } catch (error) {
            reject(error)
            return
        }
        if (info.done) {
            resolve(value)
        } else {
            Promise.resolve(value).then(_next, _throw)
        }
    }

    property int currentStep: context && context.argument.info === 'results' ? 
                              2: goodCheck.is_process_alive() ? 1 : 0
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
    property var byedpi_model: [
        "[TCP] - [IPv4]"
    ]

    property var models:[
        zapret_model,
        goodbyeDPI_model,
        byedpi_model
    ]

    property bool output_ready: false
    property bool process_state: false
    property bool isExitAvailible: false
    property string state_text: "[0/0]"
    property string execut: "goodcheckgogo.exe" 
    property string _execut: "chk preset" 
    property string output_str: ""

    property var applyDialogX:100
    property var applyDialogY:100
    property var applyDialogCalledButton:undefined
    property string strategyForApply:""

    property var buttonArray: []

    Dialog {
        id: applyDialog
        x: applyDialogX
        y: applyDialogY+height<page.height? applyDialogY : applyDialogY - height
        width:300
        title: backend.get_element_loc("apply_custom_parameters_question_title")
        ColumnLayout{
            Label {
                text: backend.get_element_loc("apply_custom_parameters_question")
                Layout.preferredWidth:applyDialog.width-20
                wrapMode:Text.Wrap
            }
            RowLayout {
                Layout.rightMargin:10
                Button{
                    text:backend.get_element_loc("accept")
                    highlighted:true
                    Layout.preferredWidth:(applyDialog.width-30)/2
                    onClicked:{
                        var result = backend.create_config(goodCheck.get_check_engine_name(), strategyForApply)
                        
                        if (result) {
                            process.update_preset()
                            var _engine = goodCheck.get_check_engine_name() === 'GoodbyeDPI' ? 'goodbyeDPI':goodCheck.get_check_engine_name()
                            process.change_engine(_engine)
                            isExitAvailible = true
                            for (var i = 0; i < buttonArray.length; i++) {
                                if (buttonArray[i].btnstrategy === strategyForApply) {
                                    buttonArray[i].highlighted = true
                                    continue;
                                }
                                buttonArray[i].highlighted = false
                            }
                            applyDialogCalledButton.highlighted = true
                        
                        }
                        
                        applyDialog.close()
                    }
                }
                Button{
                    text:backend.get_element_loc("cancel")
                    Layout.preferredWidth:(applyDialog.width-30)/2
                    onClicked:applyDialog.close()
                }
            }
        }
    }
    dialog:applyDialog

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

    property string checkStrategy: ""

    Dialog {
        id: testDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        parent: Overlay.overlay
        modal: true
        title: backend.get_element_loc("check")
        width: 500
        contentHeight: 250
        closePolicy: Popup.NoAutoClose
        Flickable {
            id: addAppFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: contentColumn.implicitHeight
            ColumnLayout {
                anchors.fill: parent
                anchors.rightMargin:20
                ColumnLayout {
                    id:contentColumn
                    spacing: 5
                    Layout.preferredWidth:480
                    Layout.leftMargin:10
                    Layout.rightMargin:10

                    Label {
                        Layout.preferredWidth: 470
                        text: backend.get_element_loc("check_tip").arg(goodCheck.get_check_engine_name())
                        wrapMode: Text.Wrap
                    }
                    ColumnLayout {
                        id: contentLayout
                        Layout.minimumHeight:52
                        Layout.fillWidth:true
                        Layout.preferredWidth:475
                        Layout.preferredHeight:commandLineOutput.implicitHeight + 20

                        Rectangle {
                            Layout.preferredWidth: Math.min(1000, parent.width)
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
                                text: checkStrategy
                                wrapMode: Text.Wrap
                                font.pixelSize: 14
                                font.family: "Cascadia Code"
                                color: "#D4D4D4"
                                height: implicitHeight
                            }
                        }
                    }

                    Button{
                        id:startTextButton
                        Layout.preferredHeight: Math.max(68, startTestLay.implicitHeight + 10)
                        Layout.fillWidth:true
                        Layout.minimumWidth: 300 
                        Layout.maximumWidth: 1000
                        Layout.rightMargin:0
                        Layout.alignment: Qt.AlignHCenter
                        highlighted:false
                        property bool isProcessStarted: false
                        RowLayout{
                            anchors.fill: parent
                            anchors {
                                leftMargin: 20
                                rightMargin: 20
                            }
                            spacing: 10
                            ColumnLayout{
                                id:startTestLay
                                Layout.fillWidth: true
                                spacing: 2
                                Label{
                                    id:startTestText
                                    Layout.fillWidth: true
                                    text: backend.get_element_loc('start_check')
                                    horizontalAlignment: Text.AlignLeft
                                    wrapMode:Text.Wrap
                                    font: Typography.body
                                }
                            }
                            IconButton {
                                width: 30
                                height: 30
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                                Icon {
                                    id:playIcon
                                    anchors.centerIn: parent
                                    source: FluentIcons.graph_Play
                                    color:startTestText.color
                                    width: 15
                                    height: 15
                                }
                                onClicked: {
                                    if (startTextButton.isProcessStarted) {
                                        process.stop_process()
                                        startTestText.text = backend.get_element_loc("start_check")
                                        playIcon.source = FluentIcons.graph_Play
                                        startTestText.color = Qt.rgba(255, 255, 255, 255)
                                        
                                    } else {
                                        process.start_process_manually(goodCheck.get_check_engine_name(), checkStrategy)
                                        startTestText.text = backend.get_element_loc("stop_check")
                                        playIcon.source = FluentIcons.graph_Stop
                                        startTestText.color = Qt.rgba(0, 0, 0, 255)
                                    }
                                    
                                    startTextButton.isProcessStarted = !startTextButton.isProcessStarted
                                    startTextButton.highlighted = startTextButton.isProcessStarted
                                }
                            }
                        }
                        
                        onClicked: {
                            if (isProcessStarted) {
                                process.stop_process()
                                startTestText.text = backend.get_element_loc("start_check")
                                playIcon.source = FluentIcons.graph_Play
                                startTestText.color = Qt.rgba(255, 255, 255, 255)
                            } else {
                                process.start_process_manually(goodCheck.get_check_engine_name(), checkStrategy)
                                
                                startTestText.text = backend.get_element_loc("stop_check")
                                playIcon.source = FluentIcons.graph_Stop
                                startTestText.color = Qt.rgba(0, 0, 0, 255)
                            }
                            isProcessStarted = !isProcessStarted
                            highlighted = isProcessStarted
                        }
                        
                    }
                    IconButton{
                        text: backend.get_element_loc("see_output")
                        icon.name: FluentIcons.graph_Flashlight
                        icon.width: 18
                        icon.height: 18
                        spacing: 5
                        LayoutMirroring.enabled: false
                        onClicked: {
                            WindowRouter.go("/pseudoconsole")
                        }
                    }
                }
            }
            ScrollBar.vertical: ScrollBar {}
        }
        footer: DialogButtonBox{
            Button {
                id:cancelButton
                text: backend.get_element_loc("cancel")
                visible:true
                width:(testDialog.width - 20)/2
                onClicked: {
                    if (startTextButton.isProcessStarted) {
                        process.stop_process()
                    }
                    testDialog.close()
                }
            }
        
        }
    }
    ColumnLayout {
        Layout.preferredWidth: Math.min(1000, parent.width)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignCenter
        ColumnLayout {
            id:setupLayout
            visible:currentStep === 0

            Button{
                Layout.preferredHeight: Math.max(68, openCheckFileLay.implicitHeight + 10)
                Layout.fillWidth:true
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                visible:goodCheck.is_data_ready()
                RowLayout{
                    anchors.fill: parent
                    anchors {
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_History
                        Layout.preferredHeight:20
                        
                    }
                    ColumnLayout{
                        id:openCheckFileLay
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            text: backend.get_element_loc('chk_preset_view_previous')
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                            font: Typography.body
                        }
                    }
                    IconButton {
                        width: 30
                        height: 30
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                        Icon {
                            anchors.centerIn: parent
                            source: FluentIcons.graph_ChevronRight
                            width: 15
                            height: 15
                        }
                        onClicked: {
                            currentStep = 2
                        }
                    }
                }
                
                onClicked: {
                    currentStep = 2
                }
                
            }
        
            Rectangle {
                Layout.minimumHeight: 68
                Layout.preferredHeight:clmn.height+20
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.controlFillColorDefault
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius:6
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
                            text: backend.get_element_loc("engine")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                            Layout.preferredWidth: rwlay.width - engine.width - 40
                        }

                        
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
                        id:engine
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        width:page.width < 700 ? page.width - 350 : 350
                        model: [
                            "Zapret",
                            "GoodbyeDPI",
                        ]
                        currentIndex:model.indexOf(backend.get_from_config("GOODCHECK", "engine"))
                        onActivated: {
                            let selectedValue = model[currentIndex];
                            backend.set_to_config("GOODCHECK", "engine", selectedValue)
                        }
                    }
                }
            }
            Rectangle {
                Layout.minimumHeight: 68
                Layout.preferredHeight:clmn_sitelist.height+20
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.controlFillColorDefault
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius:6
                RowLayout {
                    id:rwlay_sitelist_element
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                        topMargin: 10
                        bottomMargin: 10
                    }
                    spacing: 10
                    ColumnLayout {
                        id:clmn_sitelist
                        
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: backend.get_element_loc("check_list") +( engine.currentIndex === 2 ? ' (TCP)' : '')
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                            Layout.preferredWidth: rwlay_sitelist_element.width - sitelist_element.width - 40
                        }
                    }
                }

                Item {
                    
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 20
                    }
                    RowLayout {
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        ComboBox {
                            id:sitelist_element
                            
                            Layout.preferredWidth:(page.width < 700 ? page.width - 350 : 350) - height - 10
                            model: [backend.get_element_loc("goodcheck_all"), backend.get_element_loc("goodcheck_googlevideo"), 
                            backend.get_element_loc("goodcheck_miscellaneous"), backend.get_element_loc("goodcheck_nothing"), backend.get_element_loc("goodcheck_twitter")]
                            currentIndex: engine.currentIndex===2 ? goodCheck.get_chk_preset_int_value('tcp_hosts') : backend.get_int_from_config("GOODCHECK", "check_list")
                            onActivated: {
                                let selectedValue = model[currentIndex];
                                if (engine.currentIndex===2) {
                                    goodCheck.set_chk_preset_int_value('tcp_hosts', currentIndex)
                                } else {
                                    backend.set_to_config("GOODCHECK", "check_list", currentIndex)
                                }
                            }
                        }
                        Button {
                            text: backend.get_element_loc("edit")
                            icon.name:FluentIcons.graph_Edit
                            icon.height:20
                            icon.width:20
                            Layout.preferredHeight:sitelist_element.height
                            Layout.preferredWidth:sitelist_element.height
                            Layout.leftMargin:5

                            ToolTip.visible: hovered
                            ToolTip.delay: 500
                            ToolTip.text: text

                            display:Button.IconOnly
                            onClicked: {
                                goodCheck.open_goodcheck_file(sitelist_element.currentIndex);
                            }
                        }
                    }

                }
            }
            Rectangle {
                Layout.minimumHeight: 68
                Layout.preferredHeight:_strategy.height+20
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.controlFillColorDefault
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius:6
                RowLayout {
                    id:rwlay_strategy_element
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                        topMargin: 10
                        bottomMargin: 10
                    }
                    spacing: 10
                    ColumnLayout {
                        id:_strategy
                        
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: backend.get_element_loc("strategies")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                            Layout.preferredWidth: rwlay_strategy_element.width - strategy_element.width - 40
                        }
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
                        id:strategy_element
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        width:page.width < 700 ? page.width - 350 : 350
                        model: models[engine.currentIndex]
                        currentIndex: engine.currentIndex===2 ? goodCheck.get_chk_preset_int_value('strategy') : backend.get_int_from_config("GOODCHECK", "strategies")
                        onActivated: {
                            let selectedValue = model[currentIndex];
                            if (engine.currentIndex===2) {
                                goodCheck.set_chk_preset_int_value('strategy', currentIndex)
                            } else {
                                backend.set_to_config("GOODCHECK", "strategies", currentIndex)
                            }
                        }
                    }
                }
            }

            ColumnLayout {
                id:chkPresetLayout
                visible:engine.currentIndex === 2
                
                HyperlinkButton {
                    id:btnChk
                    text: additionalChkLayout.visible ? backend.get_element_loc("hide_additional_settings") : backend.get_element_loc("show_additional_settings")
                    FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                    Layout.preferredHeight:15
                    Layout.topMargin: 15
                    font: Typography.caption
                    Layout.preferredWidth:implicitWidth - 15
                    flat: true
                    background: Rectangle {
                        implicitWidth: 100
                        implicitHeight: 40
                        color: Theme.accentColor.defaultBrushFor()
                        opacity: 0.1
                        visible:btnChk.activeFocus ? true:btnChk.hovered
                        radius:2
                    }
                    onClicked:{
                        additionalChkLayout.visible = !additionalChkLayout.visible
                    }
                }
                ListModel {
                    id: _settingsModel

                    ListElement { text: "AutomaticGoogleCacheTest"; optionId: "AutomaticGoogleCacheTest"; optionGroup: "General"; checked: true; type: "switch" }
                    ListElement { text: "ConnectionTimeout"; optionId: "tcp_timeout"; optionGroup: "General"; value: "300"; placeholder: ""; type: "input" }
                    ListElement { text: "TCPPort"; optionId: "tcp_port"; optionGroup: "General"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "udp_hosts"; optionId: "udp_hosts"; optionGroup: "General"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "ConnectionTimeout"; optionId: "udp_timeout"; optionGroup: "General"; value: "300"; placeholder: ""; type: "input" }
                    ListElement { text: "udpPort"; optionId: "udp_port"; optionGroup: "General"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeSNI"; optionId: "FakeSNI"; optionGroup: "Fakes"; value: "fonts.google.com"; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexStreamTCP"; optionId: "FakeHexStreamTCP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexStreamUDP"; optionId: "FakeHexStreamUDP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexBytesTCP"; optionId: "FakeHexBytesTCP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "FakeHexBytesUDP"; optionId: "FakeHexBytesUDP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "PayloadTCP"; optionId: "PayloadTCP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    ListElement { text: "PayloadUDP"; optionId: "PayloadUDP"; optionGroup: "Fakes"; value: ""; placeholder: ""; type: "input" }
                    
                }
                ColumnLayout {
                    id:additionalChkLayout
                    visible:false
                    Repeater {
                        model: _settingsModel
                        ColumnLayout {
                            Layout.fillWidth: true

                            Loader {
                                Layout.fillWidth: true
                                
                                Layout.preferredHeight: modelData.type === "switch" ? 35:60
                                sourceComponent: defaultItemComponent
                                property int itemIndex: index
                                property var modelData: model
                                property bool chk_type: true
                            }
                        }
                    }
                }
            }
            ColumnLayout {
                id:goodcheckLayout
                visible:engine.currentIndex !== 2
                Rectangle {
                    Layout.minimumHeight: 68
                    Layout.preferredHeight:clmn_curl.height+20
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    color: Theme.res.controlFillColorDefault
                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                    radius:6
                    RowLayout {
                        id:rwlay_curl_element
                        anchors.fill: parent
                        anchors{
                            leftMargin: 20
                            rightMargin: 20
                            topMargin: 10
                            bottomMargin: 10
                        }
                        spacing: 10
                        ColumnLayout {
                            id:clmn_curl
                            
                            Layout.fillWidth: true
                            spacing: 2

                            Label {
                                text: backend.get_element_loc("curl")
                                horizontalAlignment: Text.AlignLeft
                                font: Typography.body
                                wrapMode: Text.Wrap
                                Layout.preferredWidth: rwlay_curl_element.width - curl_element.width - 40
                            }

                            Label {
                                text: backend.get_element_loc("curl_tip")
                                horizontalAlignment: Text.AlignLeft
                                font: Typography.caption
                                color: "#c0c0c0"
                                wrapMode: Text.Wrap
                                Layout.preferredWidth: rwlay_curl_element.width - curl_element.width - 40
                            }
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
                            id:curl_element
                            anchors {
                                verticalCenter: parent.verticalCenter
                                right: parent.right
                                rightMargin: 0
                            }
                            width:page.width < 700 ? page.width - 350 : 350
                            model: [
                                "Native",
                                "Curl",
                            ]
                            currentIndex: backend.get_from_config("GOODCHECK", "curl") === "Native" ? 0:1
                            onActivated: {
                                let selectedValue = model[currentIndex];
                                backend.set_to_config("GOODCHECK", "curl", selectedValue)
                            }
                        }
                    }
                }
                HyperlinkButton {
                    id:btn1
                    text: additionalLayout.visible ? backend.get_element_loc("hide_additional_settings") : backend.get_element_loc("show_additional_settings")
                    FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                    Layout.preferredHeight:15
                    Layout.topMargin: 15
                    font: Typography.caption
                    Layout.preferredWidth:implicitWidth - 15
                    flat: true
                    background: Rectangle {
                        implicitWidth: 100
                        implicitHeight: 40
                        color: Theme.accentColor.defaultBrushFor()
                        opacity: 0.1
                        visible:btn1.hovered
                        radius:2
                    }
                    onClicked:{
                        additionalLayout.visible = !additionalLayout.visible
                    }
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
                ColumnLayout {
                    id:additionalLayout
                    visible:false
                    Repeater {
                        model: settingsModel
                        ColumnLayout {
                            Layout.fillWidth: true

                            Loader {
                                Layout.fillWidth: true
                                
                                Layout.preferredHeight: modelData.type === "switch" ? 35:60
                                sourceComponent: defaultItemComponent
                                property int itemIndex: index
                                property var modelData: model
                                property bool chk_type: false
                            }
                        }
                    }
                }
            }
        }
        ColumnLayout{
            id:workingLayout
            visible:currentStep === 1
            ColumnLayout {
                id:basicProgressLayout
                
                ColumnLayout {
                    Label {
                        text:backend.get_element_loc("chk_preset_work")
                        font: Typography.subtitle
                        wrapMode:Text.Wrap
                        Layout.fillWidth:true
                    }
                    Label {
                        text:backend.get_element_loc("currently_running") + " " + state_text
                    }
                    
                }
                RowLayout{
                    Label {
                        text:backend.get_element_loc("chk_preset_state") + ": "
                    }
                    IconLabel {
                        id: status_label
                        text: qsTr(backend.get_element_loc('pseudoconsole_find'))
                        font: Typography.body
                        icon.name: FluentIcons.graph_InfoSolid
                        icon.width: 15
                        icon.height: 12
                        icon.color: Theme.accentColor.defaultBrushFor()
                        
                        spacing: 5
                    }
                }
                ProgressBar{
                    id:progressBar
                    indeterminate: true
                    Layout.fillWidth:true
                }
            }
            CheckBox {
                id: notify
                checked: backend.getBool('NOTIFICATIONS', 'goodcheck_complete')
                text: backend.get_element_loc('notifications_after_complete')
                font:Typography.bodyStrong
                Layout.leftMargin:-5
                onClicked: {
                    backend.toggleBool('NOTIFICATIONS', 'goodcheck_complete', checked)
                }
            }
            
            HyperlinkButton {
                id:btn2
                text: backend.get_element_loc("show_logs")
                FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                Layout.preferredHeight:15
                Layout.topMargin: 15
                font: Typography.caption
                Layout.preferredWidth:implicitWidth - 15
                flat: true
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: Theme.accentColor.defaultBrushFor()
                    opacity: 0.1
                    visible:btn2.hovered
                    radius:2
                }
                onClicked:{
                    WindowRouter.go("/goodcheck")
                }
            }
        }
        ColumnLayout {
            id: resultLayout
            visible: currentStep === 2
            ColumnLayout {
                id:completeProgressLayout
                
                ColumnLayout {
                    Label {
                        text:backend.get_element_loc("chk_preset_complete")
                        font: Typography.subtitle
                        wrapMode:Text.Wrap
                        Layout.fillWidth:true
                    }
                    RowLayout {
                        Icon {
                            source: FluentIcons.graph_ClickSolid
                            Layout.preferredHeight:15
                            Layout.preferredWidth:15
                        }
                        Label{
                            text:backend.get_element_loc('choose_any_chk_preset')
                            font: Typography.bodyLarge
                        }
                    }       
                }
            }
            Button{
                Layout.preferredHeight: Math.max(68, viewForSitesLay.implicitHeight + 10)
                Layout.fillWidth:true
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors {
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_Globe
                        Layout.preferredHeight:20
                    }
                    ColumnLayout{
                        id:viewForSitesLay
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            text: backend.get_element_loc('chk_preset_view_for_sites')
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                            font: Typography.body
                        }
                        Label {
                            text: backend.get_element_loc('chk_preset_view_for_sites_tip')
                            Layout.fillWidth: true
                            font: Typography.caption
                            color: "#c0c0c0"
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                        }
                    }
                    IconButton {
                        width: 30
                        height: 30
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                        Icon {
                            anchors.centerIn: parent
                            source: FluentIcons.graph_ChevronRight
                            width: 15
                            height: 15
                        }
                        onClicked: {
                            currentStep = 21
                        }
                    }
                }
                
                onClicked: {
                    currentStep = 21
                }
                
            }
            Button{
                Layout.preferredHeight: Math.max(68, viewForStrategyLay.implicitHeight + 10)
                Layout.fillWidth:true
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors {
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_MapLayers
                        Layout.preferredHeight:20
                    }
                    ColumnLayout{
                        id:viewForStrategyLay
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            text: backend.get_element_loc('chk_preset_view_for_strategy')
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                            font: Typography.body
                        }
                        Label {
                            text: backend.get_element_loc('chk_preset_view_for_strategy_tip')
                            Layout.fillWidth: true
                            font: Typography.caption
                            color: "#c0c0c0"
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                        }
                    }
                    IconButton {
                        width: 30
                        height: 30
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                        Icon {
                            anchors.centerIn: parent
                            source: FluentIcons.graph_ChevronRight
                            width: 15
                            height: 15
                        }
                        onClicked: {
                            currentStep = 22
                        }
                    }
                }
                
                onClicked: {
                    currentStep = 22
                }
                
            }
            Button{
                Layout.preferredHeight: Math.max(68, openLogLay.implicitHeight + 10)
                Layout.fillWidth:true
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors {
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_Flashlight
                        Layout.preferredHeight:20
                    }
                    ColumnLayout{
                        id:openLogLay
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            text: backend.get_element_loc('show_logs')
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                            font: Typography.body
                        }
                    }
                    IconButton {
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
                            WindowRouter.go('/goodcheck')
                        }
                    }
                }
                
                onClicked: {
                    WindowRouter.go('/goodcheck')
                }
                
            }
            Rectangle {
                id:restInfo
                Layout.preferredHeight: Math.max(40, infoColumnLayoutLic.implicitHeight + 20)
                Layout.preferredWidth:Math.min(1000, parent.width)
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.topMargin:10
                color: Theme.res.subtleFillColorTertiary
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 6
                
                Layout.rightMargin:-20
                ColumnLayout{
                    id:infoColumnLayoutLic
                    anchors.verticalCenter: parent.verticalCenter  
                    RowLayout{
                        spacing:10
                        height:20
                        Layout.leftMargin:20
                        Icon{
                            Layout.preferredHeight:20
                            source:FluentIcons.graph_InfoSolid
                            color:Theme.accentColor.defaultBrushFor()
                        }
                        ColumnLayout{
                            Label{
                                Layout.preferredWidth:restInfo.width - 100
                                text:backend.get_element_loc('choose_any_tip')
                                font: Typography.bodyStrong
                                wrapMode:Text.Wrap
                            }
                        }

                    }
                    
                }
                
            }
        }
        ColumnLayout{
            id: resultSitelistLayout
            visible: currentStep === 21

            ListModel {
                id: sitelistModel
            }

            ListModel {
                id: failureSitelistModel
            }

            Repeater {
                model: sitelistModel
                delegate: ColumnLayout {
                    Layout.preferredHeight: 45 
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        sourceComponent: defaultSite
                        onLoaded: {
                            item.url = model.url 
                            item.shortUrl = model.url.length >= 14 && model.url.lastIndexOf('.') >= 20 ? 
                                            model.url.replace("https://", "").slice(0, 14) + '<...>' + model.url.slice(model.url.lastIndexOf('.')) :
                                            model.url.replace("https://", "")

                            item.ip = model.ip
                            item.bestStrategy = model.bestStrategy
                            item.id = index
                        }
                    }

                    
                }
            }
            ColumnLayout {
                visible:failureSitelistModel.count !== 0

                Label {
                    text:backend.get_element_loc("failure_sitelist")
                    font: Typography.bodyStrong
                }
                Label {
                    text:backend.get_element_loc("failure_sitelist_tip")
                    font: Typography.body
                    wrapMode:Text.Wrap
                    Layout.fillWidth:true
                    Layout.minimumWidth: 300 
                    Layout.maximumWidth: 1000
                }
            }
            Repeater {
                model: failureSitelistModel
                delegate: ColumnLayout {
                    Layout.preferredHeight: 45 
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        sourceComponent: defaultSite
                        onLoaded: {
                            item.url = model.url 
                            item.shortUrl = model.url.length >= 14 && model.url.lastIndexOf('.') >= 20 ? 
                                            model.url.replace("https://", "").slice(0, 14) + '<...>' + model.url.slice(model.url.lastIndexOf('.')) :
                                            model.url.replace("https://", "")

                            item.ip = model.ip
                            item.bestStrategy = model.bestStrategy
                            item.id = index
                        }
                    }

                    
                }
            }
        }
        ColumnLayout {
            id:resultStrategyLayout
            visible:currentStep === 22
            ListModel {
                id: strategyModel
            }
            Repeater {
                model: strategyModel
                delegate: ColumnLayout {
                    Layout.preferredHeight: 45 
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    Loader {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        sourceComponent: defaultStrategy
                        onLoaded: {
                            item.all = model.all 
                            item.success = model.success
                            item.type = model.type
                            item.strategy = model.strategy
                            item.id = index
                        }
                    }

                    
                }
            }
        }
    }
    footer:ColumnLayout{
        ColumnLayout {
            id:footerColumn
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, page.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.leftMargin:25
            Layout.rightMargin:25
            Layout.topMargin:20
            Layout.alignment: Qt.AlignHCenter
            ColumnLayout {
                Layout.alignment: Qt.AlignRight
                Layout.fillWidth: true
                Layout.preferredHeight: (
                    currentStep === 21 || currentStep === 22 || currentStep == 2 ? 65:50
                    )+(animation.visible? animation.height+10:0)
                RowLayout {
                    id: animation
                    visible: false
                    Layout.alignment: Qt.AlignRight
                    Label {
                        text:backend.get_element_loc("data_getting_ready")
                    }
                    AnimatedImage { 
                        Layout.alignment: Qt.AlignRight
                        width:15
                        height:15
                        source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/find.gif" 
                        speed: 2
                    }
                }
                RowLayout{
                    Layout.alignment: Qt.AlignRight
                    Layout.fillWidth: true
                    Layout.preferredHeight: currentStep === 21 || currentStep === 22 || currentStep == 2 ? 65:50
                    Button{
                        Layout.preferredHeight: Math.max(40, goBackLay.implicitHeight + 10)
                        Layout.fillWidth:true
                        Layout.minimumWidth: 140 
                        Layout.maximumWidth: 1000
                        Layout.alignment: Qt.AlignHCenter
                        Layout.bottomMargin: 20
                        visible:currentStep === 21 || currentStep === 22
                        RowLayout{
                            LayoutMirroring.enabled: true
                            anchors.fill: parent
                            anchors {
                                leftMargin: 20
                                rightMargin: 20
                            }
                            spacing: 10
                            Icon {
                                visible:!isExitAvailible
                                source: FluentIcons.graph_ClickSolid
                                Layout.preferredHeight:15
                                Layout.preferredWidth:15
                            }
                            ColumnLayout{
                                id:goBackLay
                                Layout.fillWidth: true
                                spacing: 2
                                Label{
                                    Layout.fillWidth: true
                                    text: backend.get_element_loc('choose_any_back')
                                    horizontalAlignment: Text.AlignLeft
                                    wrapMode:Text.Wrap
                                    font: Typography.body
                                }
                            }
                            IconButton {
                                width: 30
                                height: 30
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                                Icon {
                                    anchors.centerIn: parent
                                    source: FluentIcons.graph_ChevronLeft
                                    width: 15
                                    height: 15
                                }
                                onClicked: {
                                    currentStep = 2;
                                }
                            }
                        }
                        
                        onClicked: {
                            currentStep = 2;
                        }
                        
                    }
                    Button{
                        Layout.preferredHeight: Math.max(40, goHomeLay.implicitHeight + 10)
                        Layout.fillWidth:true
                        Layout.minimumWidth: 140 
                        Layout.maximumWidth: 1000
                        Layout.alignment: Qt.AlignHCenter
                        Layout.bottomMargin: 20
                        visible:isExitAvailible
                        highlighted:true
                        RowLayout{
                            LayoutMirroring.enabled: true
                            anchors.fill: parent
                            anchors {
                                leftMargin: 20
                                rightMargin: 20
                            }
                            spacing: 10
                            ColumnLayout{
                                id:goHomeLay
                                Layout.fillWidth: true
                                spacing: 2
                                Label{
                                    Layout.fillWidth: true
                                    text: backend.get_element_loc('home')
                                    horizontalAlignment: Text.AlignLeft
                                    wrapMode:Text.Wrap
                                    font: Typography.body
                                    color: Qt.rgba(0, 0, 0, 255)
                                }
                            }
                            IconButton {
                                width: 30
                                height: 30
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                                Icon {
                                    anchors.centerIn: parent
                                    source: FluentIcons.graph_Home
                                    color: Qt.rgba(0, 0, 0, 255)
                                    width: 15
                                    height: 15
                                }
                                onClicked: {
                                    page_router.go('/')
                                }
                            }
                        }
                        
                        onClicked: {
                            page_router.go('/')
                        }
                        
                    }
                    Button{
                        id:stop_button
                        highlighted:false
                        visible:currentStep === 1 
                        enabled:true
                        display: page.width-50 < 500? IconButton.IconOnly:IconButton.TextBesideIcon 
                        icon.name: FluentIcons.graph_Delete
                        icon.width: 18
                        icon.height: 18
                        Layout.alignment:Qt.AlignRight
                        Layout.preferredWidth: page.width-50 < 500? 40:implicitWidth
                        Layout.minimumWidth:page.width-50 < 500? 40: page.width > 650 ? 200 : (page.width - 55) / 3
                        Layout.bottomMargin:30
                        text:backend.get_element_loc("pseudoconsole_stop")
                        onClicked: {
                            confirmationDialog.open()
                        }
                    }
                    Button{
                        id:back_button
                        highlighted:false
                        visible:currentStep!==2 && currentStep !== 21 && currentStep !== 22
                        enabled:currentStep !== 0 && currentStep !== 1
                        Layout.alignment:Qt.AlignRight
                        Layout.minimumWidth:page.width > 650 ? 200 : (page.width - 55) / 3
                        Layout.bottomMargin:30
                        text:backend.get_element_loc("back_button")
                        onClicked: {
                            currentStep --;
                        }
                    }
                    Button{
                        id:next_button
                        highlighted:true
                        visible:currentStep!==2 && currentStep !== 21 && currentStep !== 22
                        enabled:currentStep!==1
                        Layout.alignment:Qt.AlignRight
                        Layout.minimumWidth:page.width > 650 ? 200 : (page.width - 55) / 3
                        Layout.bottomMargin:30
                        text:backend.get_element_loc("next_button")
                        onClicked: {
                            if (currentStep === 0) {
                                var success = process.stop_process()
                                //process.stop_service()
                                goodCheck.start(engine.model[engine.currentIndex])
                                progressBar.visible = true
                                stop_button.enabled = true
                            }
                            if (currentStep === 1) {

                            }
                            currentStep ++;
                        }
                    }
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
                                        if (chk_type) {
                                            goodCheck.set_chk_preset_value(modelData.optionId, text)
                                        } else {
                                            goodCheck.set_value(modelData.optionGroup, modelData.optionId, text)
                                        }
                                    }    
                                }
                                
                                isInitializing = false
                            }
                            
                            Component.onCompleted: {
                                if (modelData.type === "input") {
                                    if (chk_type) {
                                        text = goodCheck.get_chk_preset_value(modelData.optionId)
                                    } else {
                                        text = goodCheck.get_value(modelData.optionGroup, modelData.optionId)
                                    }
                                }
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
                                    if (chk_type) {
                                        goodCheck.set_chk_preset_int_value(modelData.optionId, checked)
                                    } else {
                                        goodCheck.set_value(modelData.optionGroup, modelData.optionId, checked)
                                    
                                    }
                                }
                                isInitializing = false
                            }
                            Component.onCompleted: {
                                if (chk_type) {
                                    checked = goodCheck.get_chk_preset_int_value(modelData.optionId)
                                } else {
                                    checked = goodCheck.get_bool(modelData.optionGroup, modelData.optionId)
                                }
                                isInitializing = false
                            }
                        }
                    }
                }
            
            }
        }
    }
    Component {
        id: defaultSite
        Rectangle {
            property string url: ""
            property string shortUrl: ""
            property var ip: ""
            property var bestStrategy: ""
            property var id: 0

            
            Layout.preferredHeight: content.implicitHeight + 5
            color: id % 2 === 0 ? Theme.res.subtleFillColorSecondary : Theme.res.subtleFillColorTertiary
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 4
            
            RowLayout {
                id:content
                anchors.fill: parent
                anchors.leftMargin: 10
                spacing: 10

                ColumnLayout{
                    Layout.alignment:Qt.AlignVCenter|Qt.AlignLeft
                    Layout.preferredWidth:150
                    spacing:5.5 
                    HyperlinkButton {
                        id:btn3
                        text:shortUrl
                        FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                        Layout.preferredHeight:15
                        Layout.topMargin: 3
                        font: Typography.caption
                        Layout.preferredWidth:implicitWidth - 15
                        Layout.maximumWidth:parent.width
                        flat: true
                        background: Rectangle {
                            implicitWidth: 10
                            implicitHeight: 40
                            color: Theme.accentColor.defaultBrushFor()
                            opacity: 0.1
                            visible:btn3.hovered
                            radius:2
                        }
                        onClicked:{
                            Qt.openUrlExternally(url)
                        }
                    }
                    RowLayout {
                        Label {
                            text:"IP: "
                        }
                        CopyableText {
                            text:ip
                        }
                    }
                }
                
                ColumnLayout {
                    Layout.alignment:Qt.AlignVCenter|Qt.AlignRight
                    Layout.preferredWidth:parent.width-actions.width-170
                    width: parent.width-actions.width-170
                    visible: bestStrategy !== "NO"
                    Layout.topMargin:3
                    Label {
                        text:backend.get_element_loc("best_strategy_found")
                        Layout.bottomMargin:-8
                    }
                    RowLayout {
                        width:parent.width
                        TextField {
                            id: bestStrategyText
                            width: parent.width
                            property string truncatedText: bestStrategy
                            text: bestStrategy
                            Layout.preferredWidth:parent.width
                            Layout.topMargin: -5 
                            readOnly:true
                            background: Item{}
                            
                        }
                        HyperlinkButton {
                            id:btn4
                            text:"More..."
                            visible:false
                            FluentUI.primaryColor: Theme.res.textFillColorTertiary
                            Layout.preferredHeight:11
                            Layout.topMargin: 0
                            font: Typography.caption
                            Layout.preferredWidth:implicitWidth - 15
                            Layout.maximumWidth:parent.width
                            flat: true
                            background: Rectangle {
                                implicitWidth: 10
                                implicitHeight: 40
                                color: Theme.res.controlStrongStrokeColorDefault
                                opacity: 0.1
                                visible:btn4.hovered
                                radius:2
                            }
                            onClicked:{
                                Qt.openUrlExternally(url)
                            }
                        }
                    }
                }
                RowLayout {
                    id:actions
                    visible: bestStrategy !== "NO"
                    Layout.rightMargin:10
                    Button{
                        id:copy
                        text: backend.get_element_loc('copy')
                        display:IconButton.IconOnly
                        icon.name: FluentIcons.graph_Copy
                        icon.width: 18
                        icon.height: 18
                        spacing: 5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                        Timer {
                            id:timer
                            interval: 1000
                            repeat: false
                            onTriggered: {
                                copy.highlighted = false
                            }
                            running: false
                        }
                        onClicked:{
                            bestStrategyText.selectAll()
                            bestStrategyText.copy()
                            bestStrategyText.deselect()
                            highlighted = true
                            timer.start()
                            
                        }
                    }
                    Button{
                        text: backend.get_element_loc('check')
                        display:IconButton.IconOnly
                        icon.name: FluentIcons.graph_Play
                        icon.width: 18
                        icon.height: 18
                        spacing: 5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                        onClicked:{
                            checkStrategy = bestStrategy
                            testDialog.open()
                        }
                    }
                    Button{
                        id:applyStrategyButton
                        text: qsTr(backend.get_element_loc('apply_for_engine')).arg(goodCheck.get_check_engine_name())
                        display:IconButton.IconOnly
                        icon.name: FluentIcons.graph_CheckMark
                        icon.width: 18
                        icon.height: 18
                        spacing: 5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text

                        property string btnstrategy:bestStrategy
                        onClicked:{
                            strategyForApply = bestStrategy
                            var position = applyStrategyButton.mapToItem(null, 0, 0);
                            if (570 < position.x && position.x <= 940) {
                                applyDialogX = position.x-applyDialog.width-30
                            } else if (position.x <= 570){
                                applyDialogX = position.x-applyDialog.width+20
                            } else {
                                applyDialogX = page.width>1200? position.x-335-applyDialog.width/2 :position.x-300-applyDialog.width
                            }
                            applyDialogY = position.y-100
                            applyDialogCalledButton = applyStrategyButton
                            applyDialog.open()
                        }

                        Component.onCompleted:{
                            buttonArray.push(applyStrategyButton)
                        }
                    }
                }
            }
                
        }
        
    }
    Component {
        id: defaultStrategy
        Rectangle {
            id:defaultStrategyRect
            property string all: ""
            property string success: ""
            property var type: ""
            property var id: 0
            property string strategy:""

            
            Layout.preferredHeight: content.implicitHeight + 5
            color: type === "separator" ? 
                        Theme.res.controlFillColorTransparent :
                        id % 2 === 0 ? Theme.res.subtleFillColorSecondary : Theme.res.subtleFillColorTertiary
            border.color:type === "separator" ? 
                        Qt.rgba(0.67, 0.67, 0.67, 0.0): 
                        Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 4
            
            RowLayout {
                id:content
                anchors.fill: parent
                anchors.leftMargin: type === "separator" ? 0:10
                spacing: 10

                ColumnLayout{
                    Layout.alignment:Qt.AlignVCenter|Qt.AlignLeft
                    Layout.preferredWidth:150
                    spacing:5.5 
                    visible: type === "separator"
                    Label {
                        text: success !== 0 ?
                        (
                            qsTr(backend.get_element_loc('chk_preset_strategy_result'))
                            .arg(Math.floor(success / all * 100)).arg(success).arg(all)
                        ) :
                        (
                            qsTr(backend.get_element_loc('chk_preset_strategy_result_zero'))
                            .arg(success).arg(all)
                        )
                        font:Typography.bodyStrong
                    }
                }
                
                ColumnLayout {
                    Layout.alignment:Qt.AlignVCenter|Qt.AlignRight
                    Layout.preferredWidth:parent.width-actions.width-20
                    width: parent.width-actions.width-20
                    visible: type === "strategy" && strategy
                    Layout.topMargin:3
                    RowLayout {
                        width:parent.width
                        TextField {
                            id: bestStrategyText
                            width: parent.width
                            text: strategy ? strategy: ""
                            Layout.preferredWidth:parent.width
                            Layout.topMargin: -5 
                            readOnly:true
                            background: Item{}
                            
                        }
                    }
                }
                RowLayout {
                    id:actions
                    visible: type === "strategy"
                    Layout.rightMargin:10
                    Button{
                        id:copy
                        text: backend.get_element_loc('copy')
                        display:IconButton.IconOnly
                        icon.name: FluentIcons.graph_Copy
                        icon.width: 18
                        icon.height: 18
                        spacing: 5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                        Timer {
                            id:timer
                            interval: 1000
                            repeat: false
                            onTriggered: {
                                copy.highlighted = false
                            }
                            running: false
                        }
                        onClicked:{
                            bestStrategyText.selectAll()
                            bestStrategyText.copy()
                            bestStrategyText.deselect()
                            highlighted = true
                            timer.start()
                            
                        }
                    }
                    Button{
                        text: backend.get_element_loc('check')
                        display:IconButton.IconOnly
                        icon.name: FluentIcons.graph_Play
                        icon.width: 18
                        icon.height: 18
                        spacing: 5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                        onClicked:{
                            checkStrategy = strategy
                            testDialog.open()
                        }
                    }
                    Button{
                        id:applyStrategyButton
                        text: qsTr(backend.get_element_loc('apply_for_engine')).arg(goodCheck.get_check_engine_name())
                        display:IconButton.IconOnly
                        icon.name: FluentIcons.graph_CheckMark
                        icon.width: 18
                        icon.height: 18
                        spacing: 5

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text

                        property string btnstrategy:strategy

                        onClicked:{
                            strategyForApply = strategy
                            var position = applyStrategyButton.mapToItem(null, 0, 0);
                            if (570 < position.x && position.x <= 940) {
                                applyDialogX = position.x-applyDialog.width-30
                            } else if (position.x <= 570){
                                applyDialogX = position.x-applyDialog.width+20
                            } else {
                                applyDialogX = page.width>1200? position.x-335-applyDialog.width/2 :position.x-300-applyDialog.width
                            }
                            applyDialogY = position.y-100
                            applyDialogCalledButton = applyStrategyButton
                            applyDialog.open()
                        }

                        Component.onCompleted:{
                            buttonArray.push(applyStrategyButton)
                        }

                        
                    }
                }
            }
                
        }
        
    }

    
    Component.onCompleted:{
        if (goodCheck.is_data_ready()) {
            loadAllData()
        }
    }

    function loadAllData() {
        _asyncToGenerator(function*() {
            animation.visible = true
            var data = goodCheck.get_strategy_list()
            strategyModel.clear()
            yield pass();
                        
            for (var i = 0; i < data.length; ++i) {
                yield pass();
                var strategyGroup = data[i]
                var all = strategyGroup.all
                var success = strategyGroup.success
                strategyModel.append({
                    'all':all,
                    'success':success,
                    'type':'separator',
                    'strategy':''
                })
                var strategies = strategyGroup.strategies
                for (var j = 0; j < strategies.length; ++j) {
                    yield pass();
                        strategyModel.append({
                        'all':all,
                        'success':success,
                        'type':'strategy',
                        'strategy':strategies[j]
                    })
                }
            }

            var data = goodCheck.get_sitelist()
            failureSitelistModel.clear()

            for (var i = 0; i < data.length; ++i) {
                var failureSites = data[i]['failure']
                if (failureSites !== undefined) {
                    for (var j = 0; j < failureSites.length; ++j) {
                        yield pass();
                        var failureSite = failureSites[j]
                        failureSitelistModel.append({
                            'url': failureSite.url,
                            'ip': failureSite.ip,
                            'bestStrategy': 'NO'
                        })
                    }
                }
            }

            var data = goodCheck.get_sitelist()
            sitelistModel.clear()
                        
            for (var i = 0; i < data.length; ++i) {
                var successSites = data[i]['success']
                for (var j = 0; j < successSites.length; ++j) {
                    yield pass();
                    var successSite = successSites[j]
                    sitelistModel.append({
                        'url': successSite.url,
                        'ip': successSite.ip,
                        'bestStrategy': successSite.best
                    })
                }
            }
            animation.visible = false
        })();
    }

    function pass() {
        return new Promise(function (resolve, reject) {
            Qt.callLater(resolve);
        } );
    }

    function changeWidth() {
        width = Math.min(page.width-50, 1000)
        return width - 150 - 100
    }
    function stopActions() {
        progressBar.visible = false
        stop_button.enabled = false
        back_button.enabled = true
        next_button.enabled = true
        loadAllData();
    }
    function addOutput(output) {
        if (!output_ready) {
            output_ready = true
            output_str = "[DEBUG] Connecting to process...\n\n"
        }
        if (output !== '') {
            output_str += output
        }
        var execut_string = engine.currentIndex !== 2 ? execut : _execut 
        if (output.includes("Exiting with an error...")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_error')).arg(execut_string))
            setIcon("error")
            progressBar.visible = false
            back_button.enabled = true
            stop_button.enabled = false
        } else if (output.includes("All Done")) {
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success_end')).arg(execut_string))
            setIcon("success")
            goodCheck.handle_finished()
            currentStep = 2;
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

    function processStopAction() {
        if (startTextButton.isProcessStarted) {
            startTestText.text = backend.get_element_loc("start_check")
            playIcon.source = FluentIcons.graph_Play
            startTestText.color = Qt.rgba(255, 255, 255, 255)
            startTextButton.isProcessStarted = false
            startTextButton.highlighted = false
        }
        if (goodCheck.is_chk_preset_alive()) {
            goodCheck.force_error()
        }
    }

    Connections {
        target: process
        function onProcess_stopped() {
            processStopAction()
        }
        function onError_happens() {
            processStopAction()
        }
    }

    Connections {
        target: goodCheck
        function onOutput_signal (output_signal) {
            var execut_string = engine.currentIndex !== 2 ? execut : _execut 
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success')).arg(execut_string))
            setIcon("success")
            addOutput(output_signal)
        }
        function onProcess_finished_signal () {
            var execut_string = engine.currentIndex !== 2 ? execut : _execut 
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_success_end')).arg(execut_string))
            setIcon("success")
            stopActions()
        }
        function onProcess_stopped_signal() {
            var execut_string = engine.currentIndex !== 2 ? execut : _execut 
            updateStatus(qsTr(backend.get_element_loc('pseudoconsole_user_stop')).arg(execut_string))
            setIcon("info")
            stopActions()
        }
        function onCurrent_strategy_check_changed(current, all) {
            state_text = "["+current+"/"+all+"]"
        }
    }

}