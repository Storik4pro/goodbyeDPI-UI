import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import FluentUI.Controls
import GoodbyeDPI_UI

ScrollablePage {
    spacing:3
    id: page
    header: Item{}
    title: backend.get_element_loc('about')
    ColumnLayout {
        id:cllay
        Layout.preferredWidth: Math.min(1000, parent.width) 
        Layout.minimumWidth: 300 
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter 
        ColumnLayout {
            Layout.topMargin:5
            Layout.bottomMargin:5
            RowLayout {
                
                spacing: 20
                Layout.leftMargin: 15
                Image {
                    source: backend.load_logo()
                    width: 100
                    height: 100
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }

                Column {
                    
                    spacing: 10
                    Layout.alignment: Qt.AlignVCenter
                    Label {
                        text: "GOODBYEDPI UI"
                        font: Typography.bodyLarge
                        Layout.preferredWidth: Math.min(350, page.width-250)
                    }

                    RowLayout {
                        spacing:0
                        Label {
                            text: backend.get_element_loc('version')
                            font: Typography.body
                            Layout.preferredWidth: Math.min(350, page.width-250)
                        }
                        CopyableText {
                            text: backend.get_version()
                            font: Typography.body
                            color: "#c0c0c0"
                        }
                    }

                    RowLayout {
                        spacing:0
                        Label {
                            text: backend.get_element_loc('developer')
                            font: Typography.body
                            Layout.preferredWidth: Math.min(350, page.width-250)
                        }
                        CopyableText {
                            text: 'Storik4pro'
                            font: Typography.body
                            color: "#c0c0c0"
                        }
                    }
                }
            }
            
            
        }
        RowLayout {
            spacing: 10

            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_WebSearch
                icon.width: 20
                icon.height: 20
                text: backend.get_element_loc('about_repo')
                onClicked: {
                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/")
                }
            }
            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_ChatBubbles
                icon.width: 20
                icon.height: 20
                text: backend.get_element_loc('support')
                onClicked: {
                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/issues")
                }
            }
        }
        RowLayout{
            spacing:0
            CopyableText {
                text: "© 2024 Storik4. License: Apache License, Version 2.0."
                Layout.preferredWidth: cllay.width - infoButton.width
                font.pixelSize: 14
                color: "#c0c0c0"
                wrapMode:Text.Wrap
            }
            HyperlinkButton{
                id:infoButton
                text:backend.get_element_loc('about_license')
                onClicked:{
                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/blob/main/LICENSE")
                }
            }
        }

        IconLabel {
            text: backend.get_element_loc('components')
            icon.name:FluentIcons.graph_OEM
            spacing:10
            font: Typography.subtitle
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: -15
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            height: 3
            color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
            opacity: 0.3
        }
        Column {
            spacing: 10
            Label {
                text: "GoodbyeDPI"
                font: Typography.bodyLarge
                Layout.preferredWidth: 350
            }
            RowLayout{
                spacing:10
                Icon{
                    source:FluentIcons.graph_Info
                    Layout.preferredWidth:15
                    Layout.preferredHeight:14
                }
                Label {
                    text: backend.get_element_loc('about_GDPI')
                    font: Typography.body
                    wrapMode:Text.Wrap
                    Layout.preferredWidth: cllay.width - 15
                }
            }
            IconLabel {
                icon.name:FluentIcons.graph_Contact
                spacing:10
                icon.width:15
                icon.height:14
                text: 'ValdikSS'
                font: Typography.body
            }
            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_WebSearch
                icon.width: 15
                icon.height: 15
                text: backend.get_element_loc('about_repo')
                onClicked: {
                    Qt.openUrlExternally("https://github.com/ValdikSS/GoodbyeDPI/")
                }
                FluentUI.textColor:Theme.accentColor.defaultBrushFor()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: -15
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            height: 3
            color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
            opacity: 0.3
        }
        Column {
            spacing: 10
            Label {
                text: "Zapret"
                font: Typography.bodyLarge
                Layout.preferredWidth: 350
            }
            RowLayout{
                spacing:10
                Icon{
                    source:FluentIcons.graph_Info
                    Layout.preferredWidth:15
                    Layout.preferredHeight:14
                }
                Label {
                    text: backend.get_element_loc('about_ZAPRET')
                    font: Typography.body
                    wrapMode:Text.Wrap
                    Layout.preferredWidth: cllay.width - 15
                }
            }
            IconLabel {
                icon.name:FluentIcons.graph_Contact
                spacing:10
                icon.width:15
                icon.height:14
                text: 'bol-van'
                font: Typography.body
            }
            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_WebSearch
                icon.width: 15
                icon.height: 15
                text: backend.get_element_loc('about_repo')
                onClicked: {
                    Qt.openUrlExternally("https://github.com/bol-van/zapret/")
                }
                FluentUI.textColor:Theme.accentColor.defaultBrushFor()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: -15
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            height: 3
            color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
            opacity: 0.3
        }
        Column {
            spacing: 10
            Label {
                text: "ByeDPI"
                font: Typography.bodyLarge
                Layout.preferredWidth: 350
            }
            
            RowLayout{
                spacing:10
                Icon{
                    source:FluentIcons.graph_Info
                    Layout.preferredWidth:15
                    Layout.preferredHeight:14
                }
                Label {
                    text: backend.get_element_loc('about_BDPI')
                    font: Typography.body
                    wrapMode:Text.Wrap
                    Layout.preferredWidth: cllay.width - 15
                }
            }
            IconLabel {
                icon.name:FluentIcons.graph_Contact
                spacing:10
                icon.width:15
                icon.height:14
                text: 'hufrea'
                font: Typography.body
            }
            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_WebSearch
                icon.width: 15
                icon.height: 15
                text: backend.get_element_loc('about_repo')
                onClicked: {
                    Qt.openUrlExternally("https://github.com/hufrea/byedpi/")
                }
                FluentUI.textColor:Theme.accentColor.defaultBrushFor()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: -15
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            height: 3
            color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
            opacity: 0.3
        }
        Column {
            spacing: 10
            Label {
                text: "SpoofDPI"
                font: Typography.bodyLarge
                Layout.preferredWidth: 350
            }
            RowLayout{
                spacing:10
                Icon{
                    source:FluentIcons.graph_Info
                    Layout.preferredWidth:15
                    Layout.preferredHeight:14
                }
                Label {
                    text: backend.get_element_loc('about_SDPI')
                    font: Typography.body
                    wrapMode:Text.Wrap
                    Layout.preferredWidth: cllay.width - 15
                }
            }
            IconLabel {
                icon.name:FluentIcons.graph_Contact
                spacing:10
                icon.width:15
                icon.height:14
                text: 'xvzc'
                font: Typography.body
            }
            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_WebSearch
                icon.width: 15
                icon.height: 15
                text: backend.get_element_loc('about_repo')
                onClicked: {
                    Qt.openUrlExternally("https://github.com/xvzc/spoofdpi/")
                }
                FluentUI.textColor:Theme.accentColor.defaultBrushFor()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: -15
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            height: 3
            color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
            opacity: 0.3
        }
        Column {
            spacing: 10
            Label {
                text: "GoodCheck"
                font: Typography.bodyLarge
                Layout.preferredWidth: 350
            }
            RowLayout{
                spacing:10
                Icon{
                    source:FluentIcons.graph_Info
                    Layout.preferredWidth:15
                    Layout.preferredHeight:14
                }
                Label {
                    text: backend.get_element_loc('about_blockcheck')
                    font: Typography.body
                    wrapMode:Text.Wrap
                    Layout.preferredWidth: cllay.width - 15
                }
            }
            IconLabel {
                icon.name:FluentIcons.graph_Contact
                spacing:10
                icon.width:15
                icon.height:14
                text: 'Ori'
                font: Typography.body
            }
            IconButton{
                Layout.leftMargin: 0
                icon.name: FluentIcons.graph_WebSearch
                icon.width: 15
                icon.height: 15
                text: backend.get_element_loc('goto_ntc')
                onClicked: {
                    Qt.openUrlExternally("https://ntc.party/t/goodcheck-%D0%B1%D0%BB%D0%BE%D0%BA%D1%87%D0%B5%D0%BA-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82-%D0%B4%D0%BB%D1%8F-goodbyedpi-zapret-byedpi/10880")
                }
                FluentUI.textColor:Theme.accentColor.defaultBrushFor()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: -15
            Layout.topMargin: 5
            Layout.bottomMargin: 5
            height: 3
            color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
            opacity: 0.3
        }
        IconLabel {
            text: backend.get_element_loc('about_special')
            icon.name:FluentIcons.graph_HeartFill
            spacing:10
            font: Typography.subtitle
        }
        ListModel {
            id: settingsModel
            ListElement { text: "ysfchn"; link: "https://github.com/ysfchn/toasted"}
            ListElement { text: "zhuzichu520"; link: "https://github.com/zhuzichu520"}
            ListElement { text: "Lux Fero"; link: ""}
            ListElement { text: "lumenpearson"; link: ""}

        }
        Repeater {
            model: settingsModel
            
            delegate: ColumnLayout {
                height:40
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin:5
                Loader {
                    id: itemLoader
                    
                    Layout.fillWidth: true
                    Layout.preferredHeight: link === "" ? 25:60 
                    sourceComponent: defaultItemComponent
                    property var modelData: model
                }
            }
        }
        Component {
            id: defaultItemComponent
            ColumnLayout{
                IconLabel {
                    Layout.alignment:Qt.AlignVCenter
                    icon.name:FluentIcons.graph_Contact
                    spacing:10
                    icon.width:15
                    icon.height:14
                    text: modelData.text
                    font: Typography.body
                }
                IconButton{
                    visible: modelData.link !== ""
                    Layout.leftMargin: 0
                    icon.name: FluentIcons.graph_WebSearch
                    icon.width: 15
                    icon.height: 15
                    text: backend.get_element_loc('about_repo')
                    onClicked: {
                        Qt.openUrlExternally(modelData.link)
                    }
                    FluentUI.textColor:Theme.accentColor.defaultBrushFor()
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.leftMargin: -15
                    Layout.topMargin: 0
                    Layout.bottomMargin: 0
                    height: 3
                    color: Qt.rgba(0.0, 0.0, 0.0, 0.2)
                    opacity: 0.3
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
            if (id === title && window.title !== title) {
                page_router.go("/")
            }
        }
    }

}
