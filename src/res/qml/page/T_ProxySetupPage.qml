import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    title: backend.get_element_loc('proxy_setup')
    id:page
    header:Item{}
    property var state:''
    property bool isParamIncorrect:false
    Dialog{
        id: proxifyreInstallDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("install_proxifyre")
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
                    Layout.preferredWidth:400
                    Layout.leftMargin:10
                    Layout.rightMargin:10

                    ColumnLayout {
                        id:infoColumnLayout
                        visible:true
                        
                        Label {
                            text:qsTr(backend.get_element_loc("install_proxifyre_tip")).arg("1.0.22")
                            wrapMode:Text.Wrap
                            Layout.maximumWidth:contentColumn.width - 10
                        }
                        HyperlinkButton {
                            id:btn
                            text: backend.get_element_loc("goto_github")
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
                                Qt.openUrlExternally("https://github.com/wiresock/proxifyre")
                            }
                        }
                        Label {
                            text:qsTr(backend.get_element_loc("install_ndisapi_tip")).arg("3.6.1")
                            wrapMode:Text.Wrap
                            Layout.maximumWidth:contentColumn.width - 10
                        }
                        HyperlinkButton {
                            id:ndisapiBtn
                            text: backend.get_element_loc("goto_github")
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
                                visible:ndisapiBtn.hovered
                                radius:2
                            }
                            onClicked:{
                                Qt.openUrlExternally("https://github.com/wiresock/ndisapi")
                            }
                        }
                        Label {
                            text:qsTr(backend.get_element_loc("install_vs_tip"))
                            wrapMode:Text.Wrap
                            Layout.maximumWidth:contentColumn.width - 10
                        }
                        HyperlinkButton {
                            id:vsBtn
                            text: backend.get_element_loc("about_license") + ": VS Redistributable"
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
                                visible:vsBtn.hovered
                                radius:2
                            }
                            onClicked:{
                                Qt.openUrlExternally("https://visualstudio.microsoft.com/license-terms/vs2022-cruntime/")
                            }
                        }
                        Rectangle {
                            id:restInfo
                            Layout.preferredHeight: Math.max(80, infoColumnLayoutLic.implicitHeight + 20)
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignHCenter
                            color: Theme.res.controlFillColorDefault
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
                                            text:backend.get_element_loc('attention')
                                            font: Typography.bodyStrong
                                        }
                                        Label{
                                            Layout.preferredWidth:restInfo.width - 100
                                            text:backend.get_element_loc('ELUA_tip')
                                            font: Typography.body
                                            wrapMode:Text.Wrap
                                        }
                                    }

                                }
                                
                            }
                            
                        }
                        HyperlinkButton{
                            id:infoButton
                            text:backend.get_element_loc('about_license')
                            onClicked:{
                                backend.edit_blacklist("", "WPF_ELUA")
                            }
                        }
                        CheckBox {
                            id:acceptLicense
                            text: backend.get_element_loc("accept_license")
                            checked: false
                            onCheckedChanged: {
                                addButton.enabled = checked
                            }
                        }
                    }
                    ColumnLayout {
                        id:loadingColumnLayout
                        visible:false
                        RowLayout {
                            ProgressRing {
                                id: progressBar
                                indeterminate: true
                                Layout.preferredWidth:30
                                Layout.preferredHeight:30
                                strokeWidth:4
                                visible: true
                            }
                            Label {
                                text:backend.get_element_loc("update_in_process")
                                font:Typography.bodyStrong
                            }
                        }
                        Label {
                            text:backend.get_element_loc("after_update_title")
                            Layout.leftMargin:35
                        }
                        RowLayout {
                            CopyableText {
                                id:sttext
                                text:backend.get_element_loc("state_now")
                                Layout.leftMargin:35
                            }
                            ColumnLayout {
                                CopyableText {
                                    id:state_text
                                    text:''
                                    wrapMode:Text.Wrap
                                    Layout.preferredWidth: contentColumn.width - sttext.width
                                }
                            }
                        }
                    }
                    ColumnLayout {
                        id: base_layout_after_error
                        visible: false
                        Layout.fillHeight:true
                        RowLayout{
                            Icon {
                                Layout.alignment: Qt.AlignTop | Qt.AlignLeft
                                Layout.topMargin: 2
                                source: FluentIcons.graph_StatusErrorFull
                                color: Theme.res.systemFillColorCritical
                                Layout.preferredWidth: 30
                                Layout.preferredHeight: 30
                            }
                            ColumnLayout {
                                Label {
                                    text: qsTr(backend.get_element_loc('install_error'))
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                    Layout.rightMargin:20
                                }
                                CopyableText {
                                    id:errorText
                                    text:"ERR_UNKNOWN"
                                }
                            }
                        }
                    }
                    ColumnLayout {
                        id: base_layout_complete
                        visible: false
                        Layout.fillHeight:true
                        RowLayout{
                            Icon {
                                Layout.alignment: Qt.AlignTop | Qt.AlignLeft
                                Layout.topMargin: 2
                                source: FluentIcons.graph_CompletedSolid
                                color: Theme.res.systemFillColorSuccess
                                Layout.preferredWidth: 30
                                Layout.preferredHeight: 30
                            }
                            ColumnLayout {
                                Label {
                                    text: qsTr(backend.get_element_loc('install_complete'))
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                    Layout.rightMargin:20
                                }
                            }
                        }
                    }
                }
            }
            ScrollBar.vertical: ScrollBar {}
        }
        
        footer: DialogButtonBox{
            Button {
                id:addButton
                text: backend.get_element_loc("install")
                visible:true
                highlighted:true
                enabled:acceptLicense.checked
                onClicked: {
                    if (infoColumnLayout.visible) {
                        loadingColumnLayout.visible = true
                        enabled = false
                        text = "OK"
                        cancelButton.visible = false
                        width = (proxifyreInstallDialog.width-40) / 2
                        infoColumnLayout.visible = false
                        proxyHelper.download_proxifyre()
                    } else if (base_layout_complete.visible) {
                        context.router.go("/proxyUDP")
                    } else {
                        proxifyreInstallDialog.close()
                    }
                }
            }
            
            Button {
                id:cancelButton
                text: backend.get_element_loc("cancel")
                visible:true
                onClicked: {
                    proxifyreInstallDialog.close()
                }
            }
        
        }
        
    }
    Dialog{
        id: setupManuallyDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("setup_proxy_manually")
        Flickable {
            id: setupManuallyFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: setupManuallyContentColumn.implicitHeight
            ColumnLayout {
                anchors.fill: parent
                anchors.rightMargin:20
                ColumnLayout {
                    id:setupManuallyContentColumn
                    Layout.leftMargin:10
                    Layout.rightMargin:-10
                    HyperlinkButton {
                        id:hpbtn1
                        text: portSettings.visible ? backend.get_element_loc("hide_ip_settings") : backend.get_element_loc("show_ip_settings")
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
                            visible:hpbtn1.hovered
                            radius:2
                        }
                        onClicked:{
                            portSettings.visible = !portSettings.visible
                        }
                    }
                    ColumnLayout {
                        id: portSettings
                        visible:true
                        Layout.fillWidth: true
                        Label {
                            text: backend.get_element_loc("ip_addr")
                            font: Typography.bodyStrong
                            Layout.topMargin: 5
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            TextField {
                                id: ip_addr
                                Layout.fillWidth: true
                                placeholderText: "127.0.0.1"
                                text:backend.getValue("PROXY", "proxy_addr")
                                property var invalid: false
                                background: InputBackground {
                                    id: ipBackground
                                    implicitWidth: 200
                                    implicitHeight: 32
                                    radius: parent.FluentUI.radius
                                    activeColor: ip_addr.invalid? 
                                        Theme.res.systemFillColorCritical : parent.accentColor.defaultBrushFor() 

                                    color: {
                                        if(!parent.enabled){
                                            return Theme.res.controlFillColorDisabled
                                        }else if(parent.activeFocus){
                                            return Theme.res.controlFillColorInputActive
                                        }else if(parent.hovered){
                                            return Theme.res.controlFillColorSecondary
                                        }else{
                                            return Theme.res.controlFillColorDefault
                                        }
                                    }
                                    target: parent
                                }
                                trailing: IconButton{
                                    id:warnIpIcon
                                    visible:ip_addr.invalid
                                    text:backend.get_element_loc("incorrect_value")
                                    display: Button.IconOnly
                                    implicitWidth: 20
                                    implicitHeight: 20
                                    icon.name: FluentIcons.graph_Warning
                                    icon.color:Theme.res.systemFillColorCaution
                                    icon.width: 14
                                    icon.height: 14
                                    padding: 0
                                    ToolTip.visible: pressed
                                    ToolTip.delay: 0
                                    ToolTip.text: text
                                }
                                onTextChanged:{
                                    var result = proxyHelper.check_ip_addr(text)
                                    if (result){
                                        invalid = false
                                        isParamIncorrect = port.invalid
                                    } else {
                                        invalid = true
                                        isParamIncorrect = true
                                    }
                                }
                                
                            }
                            Button {
                                text: backend.get_element_loc("reset")
                                display: Button.IconOnly
                                icon.name: FluentIcons.graph_Refresh
                                icon.height: 20
                                icon.width:20
                                onClicked: {
                                    ip_addr.text = "127.0.0.1"
                                }
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                            }
                        }
                        Label {
                            text: backend.get_element_loc("port")
                            font: Typography.bodyStrong
                            Layout.topMargin: 5
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            TextField {
                                id: port
                                Layout.fillWidth: true
                                placeholderText: "1080"
                                text:backend.getValue("PROXY", "proxy_port")
                                property var invalid: false
                                background: InputBackground {
                                    implicitWidth: 200
                                    implicitHeight: 32
                                    radius: parent.FluentUI.radius
                                    activeColor: port.invalid? 
                                        Theme.res.systemFillColorCritical : parent.accentColor.defaultBrushFor() 

                                    color: {
                                        if(!parent.enabled){
                                            return Theme.res.controlFillColorDisabled
                                        }else if(parent.activeFocus){
                                            return Theme.res.controlFillColorInputActive
                                        }else if(parent.hovered){
                                            return Theme.res.controlFillColorSecondary
                                        }else{
                                            return Theme.res.controlFillColorDefault
                                        }
                                    }
                                    target: parent
                                }
                                trailing: IconButton{
                                    visible:port.invalid
                                    text:backend.get_element_loc("incorrect_value")
                                    display: Button.IconOnly
                                    implicitWidth: 20
                                    implicitHeight: 20
                                    icon.name: FluentIcons.graph_Warning
                                    icon.color:Theme.res.systemFillColorCaution
                                    icon.width: 14
                                    icon.height: 14
                                    padding: 0
                                    ToolTip.visible: pressed
                                    ToolTip.delay: 0
                                    ToolTip.text: text
                                }
                                onTextChanged:{
                                    var result = proxyHelper.check_port(text)
                                    if (result){
                                        
                                        invalid = false
                                        isParamIncorrect = ip_addr.invalid
                                    } else {
                                        invalid = true
                                        isParamIncorrect = true
                                    }
                                }
                                
                                
                            }
                            Button {
                                text: backend.get_element_loc("reset")
                                display: Button.IconOnly
                                icon.name: FluentIcons.graph_Refresh
                                icon.height: 20
                                icon.width:20
                                onClicked: {
                                    port.text = "1080"
                                }
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                            }
                        }
                    }
                }
            }
            ScrollBar.vertical: ScrollBar {}
        }
        
        
        
        footer: DialogButtonBox{
            Button {
                id:save_button
                text: backend.get_element_loc("accept")
                visible:true
                highlighted:true
                enabled:!isParamIncorrect
                onClicked: {
                    if (!isParamIncorrect) {
                        backend.changeValue("PROXY", "proxy_now_used", "manual")
                        backend.changeValue("PROXY", "proxy_addr", ip_addr.text)
                        backend.changeValue("PROXY", "proxy_port", port.text)
                        proxyHelper.proxyTypeChange()
                        if (process.is_process_alive() && (process.is_proxifyre_used()||process.is_proxy_running())) {
                            process.stop_process()
                            Qt.callLater(process.start_process)
                        }
                        setupManuallyDialog.close()
                    }
                    page_router.go("/")
                }
            }
            
            Button {
                id:_cancelButton
                text: backend.get_element_loc("cancel")
                visible:true
                onClicked: {
                    setupManuallyDialog.close()
                }
            }
        
        }

    }
    ColumnLayout {
        Layout.fillWidth: true
            
        Layout.alignment: Qt.AlignHCenter
        Rectangle {
            id:rest1
            Layout.preferredHeight: Math.max(80, _infoColumnLayout.implicitHeight + 20)
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 6
            Layout.bottomMargin:20
            ColumnLayout{
                id:_infoColumnLayout
                anchors.verticalCenter: parent.verticalCenter  
                RowLayout{
                    
                    spacing:10
                    height:20
                    Layout.leftMargin:20
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
                            text:backend.get_element_loc('proxy_tip')
                            font: Typography.body
                            wrapMode:Text.Wrap
                        }
                    }

                }
                
            }
            
        }
        ColumnLayout {
            id:buttonLayout

            Layout.fillWidth: true
            
            Layout.alignment: Qt.AlignHCenter
            RowLayout {
                Icon {
                    source: FluentIcons.graph_ClickSolid
                    Layout.preferredHeight:15
                    Layout.preferredWidth:15
                }
                Label{
                    text:backend.get_element_loc('choose_any')
                    font: Typography.bodyLarge
                }
            }
            Button{
                id:btn1
                Layout.preferredHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_System
                        Layout.preferredHeight:20
                    }
                    ColumnLayout{
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignLeft
                            text: backend.get_element_loc('setup_basic')
                            font: Typography.body
                            wrapMode:Text.Wrap
                        }
                        Label {
                            Layout.fillWidth:true
                            text: backend.get_element_loc('setup_basic_tip')
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
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
                            source: FluentIcons.graph_ChevronRight
                            width: 15
                            height: 15
                        }
                        onClicked: {
                            proxyHelper.load_proxy_settings()
                            context.router.go("/proxyBasic")
                        }
                    }
                }
                
                onClicked: {
                    proxyHelper.load_proxy_settings()
                    context.router.go("/proxyBasic")
                }
            }
            Button{
                id:btn2
                Layout.preferredHeight: Math.max(68, udpLay.implicitHeight + 10)
                Layout.fillWidth:true
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_VoiceCall
                        Layout.preferredHeight:20
                    }
                    ColumnLayout{
                        id:udpLay
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            text: backend.get_element_loc('setup_udp')
                            horizontalAlignment: Text.AlignLeft
                            wrapMode:Text.Wrap
                            font: Typography.body
                        }
                        Label {
                            text: backend.get_element_loc('setup_udp_tip')
                            Layout.fillWidth: true
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
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
                            source: FluentIcons.graph_ChevronRight
                            width: 15
                            height: 15
                        }
                        onClicked: {
                            if (proxyHelper.check_install()) {
                                context.router.go("/proxyUDP")
                            } else {
                                proxifyreInstallDialog.open()
                            }

                        }
                    }
                }
                
                onClicked: {
                    if (proxyHelper.check_install()) {
                        context.router.go("/proxyUDP")
                    } else {
                        proxifyreInstallDialog.open()
                    }
                }
                
            }
            Button{
                id:btn3
                Layout.preferredHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
                Layout.minimumWidth: 300 
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    Icon {
                        source: FluentIcons.graph_DeveloperTools
                        Layout.preferredHeight:20
                    }
                    ColumnLayout{
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignLeft
                            text: backend.get_element_loc('setup_nothing')
                            font: Typography.body
                            wrapMode:Text.Wrap
                        }
                        Label {
                            Layout.fillWidth:true
                            text: backend.get_element_loc('setup_nothing_tip')
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
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
                            setupManuallyDialog.open()
                        }
                    }
                }
                
                onClicked: {
                    setupManuallyDialog.open()
                }
            }
        }
    }
    Connections {
        target:proxyHelper
        function onProgressChanged(value) {
            value = Math.floor(value);
            if (state == 'PRXF_d') {
                state_text.text = qsTr(backend.get_element_loc("state_proxifyre_download")).arg(value)
            } else if (state == 'NDSA_d') {
                state_text.text = qsTr(backend.get_element_loc("state_ndsapi_download")).arg(value)
            } else if (state == 'NDSA_MSI_d') {
                state_text.text = qsTr(backend.get_element_loc('state_ndsapi_msi_download')).arg(value)
            } else if (state == 'VS_REDIST_d') {
                state_text.text = qsTr(backend.get_element_loc('state_vs_download')).arg(value)
            }
        } 
        function onStateChanged(_state) {

            state = _state
            if (state == 'GETR') {
                state_text.text = backend.get_element_loc('getting_ready')
            } else if (state == 'PRXF_i') {
                state_text.text = backend.get_element_loc('state_proxifyre_installing')
            } else if (state == 'NDSA_i') {
                state_text.text = backend.get_element_loc('state_ndsapi_installing')
            } else if (state == 'NDSA_MSI_i') {
                state_text.text = backend.get_element_loc('state_ndsapi_msi_installing')
            } else if (state == 'VS_REDIST_i') {
                state_text.text = backend.get_element_loc('state_vs_installing')
            } 
        }
        function onDownloadFinished(errorCode) {
            loadingColumnLayout.visible = false
            addButton.enabled = true
            if (errorCode == 'True') {
                base_layout_complete.visible = true
            } else {
                base_layout_after_error.visible = true
                errorText.text = errorCode
            }
        }
    }
}
