import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery

ScrollablePage {
    id: page
    header: Item{}
    title: backend.get_element_loc("settings")+" goodbyeDPI"
    
    property string currentDnsV4: backend.getDnsV4() 
    property string currentPortV4: backend.getPortV4()
    property string currentDnsV6: backend.getDnsV6()
    property string currentPortV6: backend.getPortV6()

    ColumnLayout {
        width: parent.width
        Layout.fillWidth: true
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
            visible: backend.getValue('GLOBAL', 'engine') === "goodbyeDPI" ? false : true 
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
                                backend.changeValue('GLOBAL', 'engine', "goodbyeDPI")
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
                        "1. " + backend.get_element_loc("preset_1"),
                        "2. " + backend.get_element_loc("preset_2"),
                        "3. " + backend.get_element_loc("preset_3"),
                        "4. " + backend.get_element_loc("preset_4"),
                        "5. " + backend.get_element_loc("preset_5"),
                        "6. " + backend.get_element_loc("preset_6"),
                        "7. " + backend.get_element_loc("preset_7"),
                        "8. " + backend.get_element_loc("preset_8"),
                        "9. " + backend.get_element_loc("preset_9") + " (" + backend.get_element_loc("default") + ")",
                        "<separator>" + backend.get_element_loc("new"),
                        "10. " + backend.get_element_loc("preset_10") + " (" + backend.get_element_loc("recommended") + ")",
                        "11. " + backend.get_element_loc("preset_11") + " (" + backend.get_element_loc("alt") + ")",
                    ]
                    currentIndex: backend.getPreset()
                    onCurrentIndexChanged: {
                        let selectedValue = model[currentIndex];
                        backend.update_preset(selectedValue);
                    }

                    focus: false
                    focusPolicy: Qt.NoFocus
                }
            }
        }



        Expander {
            expanded: true 
            Layout.fillWidth: true 
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter 


            header: Label {
                text: backend.get_element_loc("dns")
                horizontalAlignment: Qt.AlignHCenter
                font: Typography.body  
            }

            subHeader: Label {
                text: backend.get_element_loc("dns_tip")
                horizontalAlignment: Qt.AlignHCenter
                font: Typography.caption
                color: "#c0c0c0"
            }

            trailing: Switch {
                id: dnsSwitch
                text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                checked: backend.getBool("GLOBAL", "change_dns")
                onClicked: {
                    backend.toggleBool("GLOBAL", "change_dns", dnsSwitch.checked)
                }
            }
            
            content: ColumnLayout {
                spacing: 2
                ColumnLayout {
                    spacing: 5
                    anchors {
                        verticalCenter: parent.verticalCenter
                        left: parent.left
                        leftMargin: 20
                    }
                    Rectangle {
                        width: parent.width
                        height: 5
                        Layout.topMargin: 5
                    }

                    RowLayout {
                        spacing: 10
                        Label {
                            text: "DNS-"+backend.get_element_loc("server")+" IPv4:"
                            font: Typography.body
                            Layout.preferredWidth: 200
                        }
                        CopyableText {
                            text: currentDnsV4
                            font: Typography.body
                            color: "#c0c0c0"
                        }
                    }
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "DNS-"+backend.get_element_loc("port")+" IPv4:"
                            font: Typography.body
                            Layout.preferredWidth: 200
                        }
                        CopyableText {
                            text: currentPortV4
                            font: Typography.body
                            color: "#c0c0c0"
                        }
                    }

                    RowLayout {
                        spacing: 10
                        Label {
                            text: "DNS-"+backend.get_element_loc("server")+" IPv6:"
                            font: Typography.body
                            Layout.preferredWidth: 200
                        }
                        CopyableText {
                            text: currentDnsV6
                            font: Typography.body
                            color: "#c0c0c0"
                        }
                    }
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "DNS-"+backend.get_element_loc("port")+" IPv6:"
                            font: Typography.body
                            Layout.preferredWidth: 200
                        }
                        CopyableText {
                            text: currentPortV6
                            font: Typography.body
                            color: "#c0c0c0"
                        }
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 5
                        Layout.bottomMargin: 5
                    }
                }

                Button {
                    text: backend.get_element_loc("edit")
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 20
                    }

                    onClicked: confirmationDialog.open()

                    Dialog {
                        id: confirmationDialog
                        x: Math.ceil((parent.width - width) / 2)
                        y: Math.ceil((parent.height - height) / 2)
                        parent: Overlay.overlay
                        modal: true
                        title: backend.get_element_loc("dns_title")

                        Column {
                            spacing: 20
                            anchors.fill: parent
                            Label {
                                text: qsTr("IPv4")
                                font: Typography.subtitle
                            }
                            ColumnLayout {
                                Label {
                                    text: qsTr("DNS — "+backend.get_element_loc("server"))
                                    font: Typography.bodyStrong
                                }
                                TextField {
                                    id: dnsV4Field
                                    text: currentDnsV4
                                    implicitWidth: 400 
                                }
                                Label {
                                    text: qsTr("DNS — "+backend.get_element_loc("port"))
                                    font: Typography.bodyStrong
                                }
                                TextField {
                                    id: portV4Field
                                    text: currentPortV4
                                    implicitWidth: 400 
                                }
                            }

                            Label {
                                text: qsTr("IPv6")
                                font: Typography.subtitle
                            }
                            ColumnLayout {
                                Label {
                                    text: qsTr("DNS — "+backend.get_element_loc("server"))
                                    font: Typography.bodyStrong
                                }
                                TextField {
                                    id: dnsV6Field
                                    text: currentDnsV6
                                    implicitWidth: 400 
                                }
                                Label {
                                    text: qsTr("DNS — "+backend.get_element_loc("port"))
                                    font: Typography.bodyStrong
                                }
                                TextField {
                                    id: portV6Field
                                    text: currentPortV6
                                    implicitWidth: 400 
                                }
                            }
                        }

                        footer: DialogButtonBox{
                            Button{
                                anchors{
                                    topMargin:50
                                }
                                text: backend.get_element_loc("accept")
                                highlighted: true
                                onClicked: {
                                    currentDnsV4 = dnsV4Field.text
                                    currentPortV4 = portV4Field.text
                                    currentDnsV6 = dnsV6Field.text
                                    currentPortV6 = portV6Field.text
                                    
                                    backend.update_dns(currentDnsV4, currentPortV4, currentDnsV6, currentPortV6)
                                    confirmationDialog.close()
                                }
                            }
                            Button{
                                text: backend.get_element_loc("cancel")
                                onClicked: {
                                    confirmationDialog.close()
                                }
                            }
                        }

                    }
                }
            }
            _height: 68
        }

        Expander {
            id:exp
            expanded:true 
            Layout.fillWidth: true 
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter 

            header: Label {
                text: backend.get_element_loc("base_blacklist")
                horizontalAlignment: Qt.AlignVCenter
                font: Typography.body  
            }
            subHeader: Label {
                text: backend.get_element_loc("base_blacklist_tip")
                horizontalAlignment: Qt.AlignVCenter
                font: Typography.caption
                color: "#c0c0c0"
                width:exp.width - 30 - 20 - 50
                
                wrapMode:Text.Wrap
            }
            content: ColumnLayout{
                spacing:2
                width: parent.width 
                ColumnLayout {
                    spacing: 5
                    anchors {
                        verticalCenter: parent.verticalCenter
                        left: parent.left
                        leftMargin: 15
                    }

                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.bottomMargin: 5
                    }

                    RowLayout {
                        spacing: 10
                        CheckBox {
                            id:chkb1
                            topPadding: 10
                            text: backend.get_element_loc("base_blacklist_r")
                            checked: backend.getBool("GOODBYEDPI", 'use_blacklist')
                            Layout.alignment: Qt.AlignVCenter
                            onClicked: {
                                backend.toggleBool("GOODBYEDPI", 'use_blacklist', chkb1.checked)
                            }
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        Button {
                            text: backend.get_element_loc("update")
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: 35
                            onClicked: {
                                backend.update_list()
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
                    }
                    RowLayout {
                        spacing: 10
                        CheckBox {
                            id:chkb2
                            bottomPadding: 10
                            text: backend.get_element_loc("base_blacklist_c")
                            checked: backend.getBool("GOODBYEDPI", 'use_blacklist_custom')
                            Layout.alignment: Qt.AlignVCenter
                            onClicked: {
                                backend.toggleBool("GOODBYEDPI", 'use_blacklist_custom', chkb2.checked)
                            }
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        Button {
                            text: backend.get_element_loc("edit")
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: 35
                            onClicked: {
                                backend.edit_custom_blacklist()
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.topMargin: 5
                    }
                }

            }
            _height: 68
            
        }

        Button {
            Layout.minimumHeight: 68
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter

            RowLayout {
                anchors.fill: parent
                anchors{
                    leftMargin: 20
                    rightMargin: 20
                }
                spacing: 10

                Icon {
                    source: FluentIcons.graph_DeveloperTools
                    width: 20
                    height: 20
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Label {
                        Layout.fillWidth: true
                        text: backend.get_element_loc("advanced")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.body
                        wrapMode: Text.Wrap
                    }
                    Label {
                        Layout.fillWidth: true
                        text: backend.get_element_loc("advanced_tip")
                        horizontalAlignment: Text.AlignLeft
                        font: Typography.caption
                        color: "#c0c0c0"
                        wrapMode: Text.Wrap
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
                        context.router.go("/goodbyedpiAdvanced")
                    }
                }
            }

            onClicked: {
                context.router.go("/goodbyedpiAdvanced")
            }
        }
    }
    
    
}


