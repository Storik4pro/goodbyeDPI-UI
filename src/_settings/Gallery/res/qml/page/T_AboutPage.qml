import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import FluentUI.Controls
import Gallery

ScrollablePage {
    spacing:3
    id: page
    header: Item{}
    title: backend.get_element_loc('about')
    ColumnLayout {
        Layout.fillWidth: true 
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
        Layout.minimumWidth: 300 
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter 
        Expander {
            expanded: true 
            Layout.fillWidth: true 
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter 


            header: Label {
                text: backend.get_element_loc('about_first')
                horizontalAlignment: Qt.AlignHCenter
                font: Typography.body  
            }

            content: ColumnLayout {
                anchors {
                    topMargin:20
                    bottomMargin:20
                }
                Rectangle {
                    width: parent.width
                    height: 50
                    Layout.bottomMargin: 5
                    color: Qt.rgba(0, 0, 0, 0)
                }
                RowLayout {
                    
                    spacing: 20
                    anchors {
                        verticalCenter: parent.verticalCenter
                        left: parent.left
                        leftMargin: 15
                    }
                    Image {
                        source: backend.load_logo()
                        width: 100
                        height: 100
                        fillMode: Image.PreserveAspectFit
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Column {
                        
                        spacing: 10
                        anchors.verticalCenter: parent.verticalCenter

                        RowLayout {
                            spacing: 10
                            Label {
                                text: "Version"
                                font: Typography.body
                                Layout.preferredWidth: 350
                            }
                            CopyableText {
                                text: backend.get_version()
                                font: Typography.body
                                color: "#c0c0c0"
                            }
                        }

                        RowLayout {
                            spacing: 10
                            Label {
                                text: "Developer"
                                font: Typography.body
                                Layout.preferredWidth: 350
                            }
                            CopyableText {
                                text: 'Storik4pro'
                                font: Typography.body
                                color: "#c0c0c0"
                            }
                        }

                        RowLayout {
                            spacing: 10
                            Label {
                                text: backend.get_element_loc('about_repo')
                                font: Typography.body
                                Layout.preferredWidth: 350
                            }
                            Label {
                                text: backend.get_element_loc('support')+":"
                                font: Typography.body
                                Layout.preferredWidth: 350
                            }
                            
                        }
                        RowLayout {
                            spacing: 10
                            ColumnLayout {
                                Layout.preferredWidth: 350

                                HyperlinkButton{
                                    anchors {
                                        leftMargin: 15
                                        topMargin:0
                                    }
                                    text: "https://github.com/Storik4pro/goodbyeDPI-UI/"
                                    onClicked: {
                                        Qt.openUrlExternally(text)
                                    }
                                }
                            }
                            HyperlinkButton{
                                anchors {
                                    leftMargin: 15
                                    topMargin:0
                                }
                                text: "https://github.com/Storik4pro/goodbyeDPI-UI/issues"
                                onClicked: {
                                    Qt.openUrlExternally(text)
                                }
                            }
                        }
                        CopyableText {
                            text: "© 2024 Storik4. License: Apache License, Version 2.0."
                            font.pixelSize: 14
                            color: "#c0c0c0"
                        }
                        Button{
                            text:backend.get_element_loc('about_license')
                            onClicked:{
                                Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/blob/main/LICENSE")
                            }
                        }
                    }
                }
                
            }
            _height: 68

        }

        Expander {
            expanded: true 
            Layout.fillWidth: true 
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
            Layout.minimumWidth: 300 
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter 


            header: Label {
                text: backend.get_element_loc('about_second')
                horizontalAlignment: Qt.AlignHCenter
                font: Typography.body  
            }

            content: ColumnLayout {
                Rectangle {
                    width: parent.width
                    height: 20
                    Layout.bottomMargin: 5
                    color: Qt.rgba(0, 0, 0, 0)
                }
                ColumnLayout{
                    RowLayout {
                        spacing: 20
                        anchors {
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: 15
                        }

                        Column {
                            spacing: 10
                            anchors.verticalCenter: parent.verticalCenter
                            Label {
                                    text: "GoodbyeDPI"
                                    font: Typography.subtitle
                                    Layout.preferredWidth: 350
                                }
                            RowLayout {
                                spacing: 10
                                Label {
                                    text: backend.get_element_loc('about_about')
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: backend.get_element_loc('about_GDPI')
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }
                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Version"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: backend.get_GDPI_version()
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Developer"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: 'ValdikSS'
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Links:"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                
                            }
                            RowLayout {
                                spacing: 10
                                ColumnLayout {
                                    Layout.preferredWidth: 350

                                    HyperlinkButton{
                                        anchors {
                                            leftMargin: 15
                                            topMargin:0
                                        }
                                        text: "https://github.com/ValdikSS/GoodbyeDPI/"
                                        onClicked: {
                                            Qt.openUrlExternally(text)
                                        }
                                    }
                                }
                                ColumnLayout {
                                    Layout.preferredWidth: 350

                                    HyperlinkButton{
                                        anchors {
                                            leftMargin: 15
                                            topMargin:0
                                        }
                                        text: "https://github.com/ValdikSS/"
                                        onClicked: {
                                            Qt.openUrlExternally(text)
                                        }
                                    }
                                }
                            }
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
                
                ColumnLayout {

                    RowLayout {
                        spacing: 20
                        anchors {
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: 15
                        }
                        
                        Column {
                            spacing: 10
                            anchors.verticalCenter: parent.verticalCenter
                            Label {
                                text: "BlockCheck strategies"
                                font: Typography.subtitle
                                Layout.preferredWidth: 350
                                Layout.topMargin:0
                            }
                            RowLayout {
                                spacing: 10
                                Label {
                                    text: backend.get_element_loc('about_about')
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: backend.get_element_loc('about_blockcheck')
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Developer"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: 'Ori'
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Links:"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                
                            }
                            RowLayout {
                                spacing: 10
                                ColumnLayout {
                                    Layout.preferredWidth: 350

                                    HyperlinkButton{
                                        anchors {
                                            leftMargin: 15
                                            topMargin:0
                                        }
                                        text: "https://ntc.party/"
                                        onClicked: {
                                            Qt.openUrlExternally("https://ntc.party/t/goodcheck-%D0%B1%D0%BB%D0%BE%D0%BA%D1%87%D0%B5%D0%BA-%D1%81%D0%BA%D1%80%D0%B8%D0%BF%D1%82-%D0%B4%D0%BB%D1%8F-goodbyedpi-zapret-byedpi/10880")
                                        }
                                    }
                                }
                            }
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
                
                ColumnLayout {

                    RowLayout {
                        spacing: 20
                        anchors {
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: 15
                        }
                        
                        Column {
                            spacing: 10
                            anchors.verticalCenter: parent.verticalCenter
                            Label {
                                text: "QML FluentUI"
                                font: Typography.subtitle
                                Layout.preferredWidth: 350
                                Layout.topMargin:0
                            }
                            RowLayout {
                                spacing: 10
                                Label {
                                    text: backend.get_element_loc('about_about')
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: backend.get_element_loc('about_FUI')
                                    font: Typography.body
                                    color: "#c0c0c0"
                                    wrapMode: Text.WordWrap
                                    width: paintedWidth
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Developer"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: 'zhuzichu520'
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Links:"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                
                            }
                            RowLayout {
                                spacing: 10
                                ColumnLayout {
                                    Layout.preferredWidth: 350

                                    HyperlinkButton{
                                        anchors {
                                            leftMargin: 15
                                            topMargin:0
                                        }
                                        text: "https://github.com/zhuzichu520/"
                                        onClicked: {
                                            Qt.openUrlExternally(text)
                                        }
                                    }
                                }
                            }
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
                
                ColumnLayout {

                    RowLayout {
                        spacing: 20
                        anchors {
                            verticalCenter: parent.verticalCenter
                            left: parent.left
                            leftMargin: 15
                        }
                        
                        Column {
                            spacing: 10
                            anchors.verticalCenter: parent.verticalCenter
                            Label {
                                text: "Toasted"
                                font: Typography.subtitle
                                Layout.preferredWidth: 350
                                Layout.topMargin:0
                            }
                            RowLayout {
                                spacing: 10
                                Label {
                                    text: backend.get_element_loc('about_about')
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: backend.get_element_loc('about_toast')
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Developer"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                CopyableText {
                                    text: 'ysfchn'
                                    font: Typography.body
                                    color: "#c0c0c0"
                                }
                            }

                            RowLayout {
                                spacing: 10
                                Label {
                                    text: "Links:"
                                    font: Typography.body
                                    Layout.preferredWidth: 350
                                }
                                
                            }
                            RowLayout {
                                spacing: 10
                                ColumnLayout {
                                    Layout.preferredWidth: 350

                                    HyperlinkButton{
                                        anchors {
                                            leftMargin: 15
                                            topMargin:0
                                        }
                                        text: "https://github.com/ysfchn/"
                                        onClicked: {
                                            Qt.openUrlExternally(text)
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                }

                Rectangle {
                    width: parent.width
                    height: 20
                    Layout.bottomMargin: 5
                    color: Qt.rgba(0, 0, 0, 0)
                }
                
            }
            _height: 68

        }
    }

}
