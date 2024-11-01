import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI


ScrollablePage {
    title: backend.get_element_loc("_update")
    id:page
    header:Item{}

    property string lastCheckedTime: backend.getValue("GLOBAL", "lastcheckedtime")
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
        id: base_layout
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter

        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter

            Flow {
                id: mainFlow
                Layout.fillWidth: true
                spacing: 20
                flow: Flow.LeftToRight

                Image {
                    id:uimg
                    source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/update.png"
                    width: 90
                    height: 90
                    fillMode: Image.PreserveAspectFit
                    sourceSize.width: width
                    sourceSize.height: height
                    Layout.alignment: Qt.AlignHCenter
                }
                RowLayout{
                    Item{
                        Layout.alignment: Qt.AlignLeft
                        Layout.preferredHeight:90 
                    }

                ColumnLayout {
                    id: contentColumn
                    Layout.minimumWidth: 100
                    Layout.maximumWidth: 700
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignLeft
                    

                    Label {
                        id:mainLabel
                        text: isError ? backend.get_element_loc("update_fail") :
                              isDownloading ? backend.get_element_loc("update_downloading") :
                              isUpdating ? backend.get_element_loc("update_check") :
                              updatesAvailable ? backend.get_element_loc("update_available_t") : backend.get_element_loc("update_available_f")
                        font: Typography.subtitle
                        wrapMode: Text.Wrap
                        Layout.alignment: Qt.AlignLeft
                        Layout.preferredWidth: Math.min(740, Math.max(timeLabel.width, base_layout.width - uimg.width - 20 - checkBtn.width-40))
                        anchors.rightMargin: 20
                    }

                    ProgressBar {
                        id: progressBar
                        indeterminate: true
                        Layout.fillWidth: true
                        anchors {
                            rightMargin: 15
                            topMargin: 20
                            bottomMargin: 20
                        }
                        visible: false
                    }
                    ProgressBar {
                        id: progressBarDownload
                        indeterminate: false
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        anchors {
                            rightMargin: 15
                            topMargin: 20
                            bottomMargin: 20
                        }
                        visible: false
                    }

                    CopyableText {
                        id: timeLabel
                        text: isError ? errorText :
                              updatesAvailable ? qsTr(backend.get_element_loc("update_v") + ": %1").arg(availableVersion) : 
                              qsTr(backend.get_element_loc("update_t") + ": %1").arg(lastCheckedTime)
                        font: Typography.body
                        color: "#666666"
                        Layout.alignment: Qt.AlignLeft
                        visible: true
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
                }

                RowLayout{
                    Layout.alignment: Qt.AlignVCenter
                    Layout.fillWidth: true
                    Item{
                        Layout.alignment: Qt.AlignLeft
                        Layout.preferredHeight:mainLabel.width == timeLabel.width ? checkBtn.height:90 
                    }
                    Button {
                        id: checkBtn
                        text: updatesAvailable ? backend.get_element_loc("update_available_btn_t") : backend.get_element_loc("update_available_btn_f")
                        highlighted: true
                        Layout.minimumWidth: 50
                        Layout.alignment: Qt.AlignRight|Qt.AlignVCenter
                        
                        onClicked: {
                            if (updatesAvailable) {
                                enabled = false
                                download_update()
                            } else {
                                checkForUpdates()
                            }
                        }
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
                radius: 6

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10

                    Label {
                        text: backend.get_element_loc("notify")
                        font: Typography.body
                        Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                        wrapMode: Text.Wrap
                    }

                    

                    Switch {
                        property bool isInitializing: backend.getBool("GLOBAL", "notifyaboutupdates")
                        text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                        checked: backend.getBool("GLOBAL", "notifyaboutupdates")
                        onCheckedChanged: {
                            if (!isInitializing) {
                                backend.toggleBool("GLOBAL", "notifyaboutupdates", checked)
                            }
                            isInitializing = false
                        }
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
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
                radius: 6

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10

                    Label {
                        text: backend.get_element_loc("update_beta")
                        font: Typography.body
                        Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                        wrapMode: Text.Wrap
                    }

                    

                    Switch {
                        property bool isInitializing: backend.getBool('GLOBAL', 'usebetafeatures')
                        text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                        checked: backend.getBool('GLOBAL', 'usebetafeatures')
                        onCheckedChanged: {
                            if (!isInitializing) {
                                backend.toggleBool('GLOBAL', 'usebetafeatures', checked)
                            }
                            isInitializing = false
                        }
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        lastCheckedTime = backend.getValue("GLOBAL", "lastcheckedtime")
        updatesAvailable = backend.getBool("GLOBAL", "updatesavailable")
        checkBtn.text = updatesAvailable ? backend.get_element_loc("update_available_btn_t") : backend.get_element_loc("update_available_btn_f")
        if (window.title !== title){
            multiWindow.close_window(title);
        }
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
        function onDownload_url_ready() {
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
                checkBtn.text = backend.get_element_loc("update_available_btn_t")
            } else {
                updatesAvailable = false
            }
            var currentTime = new Date()
            lastCheckedTime = currentTime.toLocaleString(Qt.locale(), "HH:mm dd.MM.yyyy")
            backend.changeValue("GLOBAL", "lastCheckedTime", lastCheckedTime)
        }
        function onDownload_progress() {
            var progress = arguments[0]
            progressBar.visible = false
            progressBarDownload.visible = true
            progressBarDownload.value = progress
            isError = false
            timeLabel.visible = false
            checkBtn.enabled = false
            isDownloading = true
            checkBtn.text = backend.get_element_loc("update_available_btn_t")
            console.log(progress, progressBarDownload.value)
        }

        function onDownload_finished() {
            var success = arguments[0]
            isDownloading = false
            
            progressBarDownload.visible = false
            if (success === 'True') {
                errorText = ''
                process.stop_service()
                Qt.callLater(backend._update)
                Qt.callLater(WindowRouter.close, 0)
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
    Connections {
        target:multiWindow
        function onMulti_window_init(id) {
            if (id === title && window.title !== title) {
                page_router.go("/")
            }
        }
    }

}