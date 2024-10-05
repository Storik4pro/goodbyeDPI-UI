import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery


ScrollablePage {
    title: backend.get_element_loc("_update")
    id:page
    header:Item{}

    property string lastCheckedTime: ""
    property bool updatesAvailable: backend.getBool('GLOBAL', 'updatesavailable')
    property bool isUpdating: false
    property bool isDownloading : false
    property string availableVersion: backend.getValue('GLOBAL', 'version_to_update')
    property bool isError : false
    property string errorText: ''

    InfoBarManager{
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }

    ColumnLayout {
        id:base_layout
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter

        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            Image {
                source: "qrc:/qt/qml/Gallery/res/image/update.png" 
                width: 90
                height: 90
                fillMode: Image.PreserveAspectFit
                sourceSize.width: width
                sourceSize.height: height
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(700, base_layout.width * 0.65)
                Layout.minimumWidth: 100
                Layout.maximumWidth: 700

                Label {
                    text: isError ? backend.get_element_loc("update_fail") :
                          isDownloading ? backend.get_element_loc("update_downloading") :
                          isUpdating ? backend.get_element_loc("update_check") : 
                          updatesAvailable ? backend.get_element_loc("update_available_t") : backend.get_element_loc("update_available_f")
                    font:Typography.subtitle
                    wrapMode:WrapAnywhere
                    Layout.alignment: Qt.AlignLeft
                    anchors{
                        rightMargin:20
                    }
                }

                ProgressBar{
                    id: progressBar
                    indeterminate: true
                    Layout.fillWidth:true
                    anchors{
                        rightMargin:15
                        topMargin:20
                        bottomMargin:20
                    }
                    visible:false
                }
                ProgressBar{
                    id: progressBarDownload
                    indeterminate: false
                    Layout.fillWidth:true
                    from: 0
                    to: 100
                    anchors{
                        rightMargin:15
                        topMargin:20
                        bottomMargin:20
                    }
                    visible:false
                }

                CopyableText {
                    id:timeLabel
                    text: isError ? errorText:
                          updatesAvailable ? qsTr(backend.get_element_loc("update_v")+": %1").arg(availableVersion) : qsTr(backend.get_element_loc("update_t")+": %1").arg(lastCheckedTime)
                    font:Typography.body
                    color: "#666666"
                    Layout.alignment: Qt.AlignLeft
                    visible:true
                }
                HyperlinkButton {
                    id: whatsNewButton
                    text: backend.get_element_loc("whats_new")
                    visible: updatesAvailable
                    onClicked: {
                        showWhatsNew()
                    }
                }
            }

            Item {
                Layout.fillWidth: true
            }

            Button {
                id:checkBtn
                text: qsTr("")
                highlighted: true
                
                anchors{
                    right:parent.right
                }
                onClicked: {
                    if (updatesAvailable) {
                        enabled:false
                        download_update()
                    } else {
                        checkForUpdates()
                    }
                }
            }
        }

        Rectangle {
            color: "#CCCCCC"
            height: 1
            Layout.fillWidth: true
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

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
                        text: backend.get_element_loc("notify")
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
                        property bool isInitializing: backend.getBool("GLOBAL", "notifyAboutUpdates")
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                        checked: backend.getBool("GLOBAL", "notifyAboutUpdates")
                        onCheckedChanged: {
                            if (!isInitializing){
                                backend.toggleBool("GLOBAL", "notifyAboutUpdates", checked)
                            }
                            isInitializing = false
                        }
                    }
                }
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
                        text: backend.get_element_loc("update_beta")
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
                        property bool isInitializing: backend.getBool('GLOBAL', 'usebetafeatures') 
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                        checked: backend.getBool('GLOBAL', 'usebetafeatures')
                        onCheckedChanged: {
                            if (!isInitializing){
                                backend.toggleBool('GLOBAL', 'usebetafeatures', checked)
                            }
                            isInitializing = false
                        }
                    }
                }
            }

        }
    }

    Component.onCompleted: {
        lastCheckedTime = backend.getValue("GLOBAL", "lastCheckedTime")
        updatesAvailable = backend.getBool("GLOBAL", "updatesavailable")
        checkBtn.text = updatesAvailable ? backend.get_element_loc("update_available_btn_t") : backend.get_element_loc("update_available_btn_f")
        
    }

    function checkForUpdates() {
        progressBar.visible = true
        timeLabel.visible = false
        checkBtn.enabled = false
        isUpdating = true
        backend.get_download_url()
    }

    function download_update() {
        isError = false
        timeLabel.visible = false
        checkBtn.enabled = false
        isDownloading = true
        progressBar.visible = true
        progressBarDownload.value = 0
        checkBtn.text = backend.get_element_loc("update_available_btn_t")
        backend.download_update()
    }

    function showWhatsNew() {
        Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/releases/latest")
    }

    Connections {
        target: backend
        onDownload_url_ready: {
            isError = false
            var version = arguments[0]
            progressBar.visible = false
            checkBtn.enabled = true
            timeLabel.visible = true
            isUpdating = false
            if (version !== 'false') {
                updatesAvailable = true
                availableVersion = version
                whatsNewButton.visible = true
                backend.changeValue('GLOBAL', 'version_to_update', availableVersion)
                backend.toggleBool("GLOBAL", "updatesavailable", updatesAvailable)
            } else {
                updatesAvailable = false
            }
            var currentTime = new Date()
            lastCheckedTime = currentTime.toLocaleString(Qt.locale(), "HH:mm dd.MM.yyyy")
            backend.changeValue("GLOBAL", "lastCheckedTime", lastCheckedTime)
        }
        onDownload_progress: {
            var progress = arguments[0]
            progressBar.visible = false
            progressBarDownload.visible = true
            progressBarDownload.value = progress
            console.log(progress, progressBarDownload.value)
        }

        onDownload_finished: {
            var success = arguments[0]
            isDownloading = false
            
            progressBarDownload.visible = false
            if (success === 'True') {
                errorText = ''
                backend._update()
            } else {
                isError = true
                checkBtn.enabled = true
                checkBtn.text = backend.get_element_loc("retry")
                timeLabel.visible = true
                progressBar.visible = false
                whatsNewButton.visible = false
                errorText = success
            }
        }
    }

}