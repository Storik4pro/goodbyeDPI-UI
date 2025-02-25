import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    title: backend.get_element_loc('setup_basic')
    id:page
    header:Item{}
    property var currentStep: 0
    property bool isParamIncorrect: false

    ColumnLayout {
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
        Layout.minimumWidth: 300 
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        ColumnLayout {
            id:firstStep
            visible:currentStep === 0
            
            Label {
                text: backend.get_element_loc("sites_white_list")
                font: Typography.bodyStrong
                wrapMode:Text.Wrap
                Layout.fillWidth:true
                Layout.topMargin: 5
            }
            ColumnLayout {
                id:siteChooser
                
                Rectangle {
                    Layout.preferredHeight: customParameters.implicitHeight + 25 + tip.implicitHeight
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
                        Label {
                            id:tip
                            text: backend.get_element_loc("sites_white_list_tip").replace("U+003B", ";")
                            font: Typography.body
                            wrapMode:Text.Wrap
                            Layout.fillWidth:true
                            Layout.topMargin: 0
                        }
                        TextArea  {
                            id: customParameters
                            placeholderText: ""
                            wrapMode: TextEdit.Wrap
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            FluentUI.radius:0
                            property bool isInitializing: false
                            text: proxyHelper.get_proxy_setting_string("ProxyOverride").replace(";<local>", "")
                            onTextChanged: {
                                proxyHelper.set_proxy_setting("ProxyOverride", text+(duplocalCheckBox.checked? ";<local>":""))
                            }
                        }


                    }
                }
            }
            RowLayout {
                id: columnLayout
                spacing: 5
                CheckBox {
                    id: duplocalCheckBox
                    text: backend.get_element_loc("dont_use_proxy_for_localhost")
                    checked: proxyHelper.get_proxy_setting_string("ProxyOverride").indexOf(";<local>") !== -1
                    onCheckedChanged: {
                        if (checked) {
                            proxyHelper.set_proxy_setting("ProxyOverride", customParameters.text + ";<local>")
                        } else {
                            proxyHelper.set_proxy_setting("ProxyOverride", customParameters.text.replace(";<local>", ""))
                        }
                    }
                    Layout.preferredWidth:page.width - 50
                    Layout.leftMargin:-6

                    onClicked: {
                    }
                }
            }
            HyperlinkButton {
                id:btn1
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
                    visible:btn1.hovered
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
                        text:(proxyHelper.get_proxy_setting_string("ProxyServer").split("]:")[1]?
                             proxyHelper.get_proxy_setting_string("ProxyServer").split("]:")[0]:
                             proxyHelper.get_proxy_setting_string("ProxyServer").split(":")[0]).replace("[", "").replace("]", "").replace("socks=", "")
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
                        text:proxyHelper.get_proxy_setting_string("ProxyServer").split("]:")[1]?
                             proxyHelper.get_proxy_setting_string("ProxyServer").split("]:")[1]:
                             proxyHelper.get_proxy_setting_string("ProxyServer").split(":")[1]
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
        ColumnLayout {
            id:endStep
            visible:currentStep === 1
            Layout.fillWidth:true
            ColumnLayout{
                visible:true
                Layout.preferredHeight: page.height - 150
                Layout.preferredWidth:page.width
                Layout.minimumHeight:implicitHeight
                ColumnLayout{
                    Layout.alignment: Qt.AlignHCenter|Qt.AlignVCenter
                    
                    Label {
                        text: "🎉"
                        font.pixelSize: 75
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Label {
                        text:backend.get_element_loc("proxy_complete")
                        font: Typography.subtitle
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Label {
                        text:backend.get_element_loc("proxy_complete_tip")
                        wrapMode:Text.Wrap
                        horizontalAlignment:Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                        Layout.maximumWidth: 350
                    }
                    Button {
                        text:backend.get_element_loc("home")
                        Layout.alignment: Qt.AlignHCenter
                        Layout.topMargin:10
                        Layout.preferredWidth:250
                        highlighted:true
                        onClicked:{
                            page_router.go("/")
                        }
                    }
                }
            }
        }
    }

    footer:ColumnLayout{
        ColumnLayout {
            id:footerColumn
            visible:currentStep !== 1
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, page.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.leftMargin:25
            Layout.rightMargin:25
            Layout.alignment: Qt.AlignHCenter
            Rectangle {
                id:restWarn
                visible: isParamIncorrect
                Layout.preferredHeight: Math.max(60, warnColumnLayout1.implicitHeight + 20)
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.systemFillColorCautionBackground
                radius: 6
                border.color: Theme.res.cardStrokeColorDefault

                ColumnLayout{
                    id:warnColumnLayout1
                    anchors.verticalCenter: parent.verticalCenter  
                    RowLayout{    
                        spacing:10
                        height:20
                        Layout.leftMargin:10
                        
                        Icon{
                            Layout.preferredHeight:20
                            source:FluentIcons.graph_Warning
                            color:Theme.res.systemFillColorCaution
                        }
                        ColumnLayout{
                            Label{
                                text:backend.get_element_loc('warning')
                                font: Typography.bodyStrong

                            }
                            Label{
                                Layout.preferredWidth:restWarn.width - 100
                                text:backend.get_element_loc('apply_udp_proxy_invalid_param')
                                font: Typography.body
                                wrapMode:Text.Wrap
                            }
                        }

                    }
                }
            }
            RowLayout{
                Layout.alignment: Qt.AlignRight
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                Button{
                    highlighted:false
                    visible:currentStep!==2
                    enabled:currentStep !== 0 && currentStep !== 2
                    Layout.alignment:Qt.AlignRight
                    Layout.minimumWidth:page.width > 650 ? 300 : (page.width - 50) / 2
                    Layout.bottomMargin:30
                    text:backend.get_element_loc("back_button")
                    onClicked: {
                        currentStep --;
                    }
                }
                Button{
                    highlighted:true
                    visible:currentStep!==2
                    enabled:(!isParamIncorrect && currentStep == 0)
                    Layout.alignment:Qt.AlignRight
                    Layout.minimumWidth:page.width > 650 ? 300 : (page.width - 50) / 2
                    Layout.bottomMargin:30
                    text:backend.get_element_loc("next_button")
                    onClicked: {
                        var ip = "socks="
                        if (currentStep === 0){
                            if (ip_addr.text.indexOf(":") !== -1){
                                ip += "[" + ip_addr.text + "]:" + port.text
                            } else {
                                ip += ip_addr.text + ":" + port.text
                            }
                        }
                        proxyHelper.set_proxy_setting("ProxyServer", ip)
                        proxyHelper.save_proxy_settings()
                        
                        backend.changeValue("PROXY", "proxy_now_used", "basic")
                        backend.changeValue("PROXY", "proxy_addr", ip_addr.text)
                        backend.changeValue("PROXY", "proxy_port", port.text)
                        proxyHelper.proxyTypeChange()
                        if (process.is_process_alive() && (process.is_proxifyre_used()||process.is_proxy_running())) {
                            process.stop_process()
                            Qt.callLater(process.start_process)
                        }
                        currentStep ++;
                        
                    }
                }
            }
        }
    }
}