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
    property bool getting_ready: patcher.is_getting_ready()
    property string listOfChangesLabelText: backend.get_element_loc("list_of_changes_load_failure")

    InfoBarManager{
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }

    Menu {
        id:menu
        width: 300
        title: qsTr("More")
        
        MenuItem{
            icon.name: FluentIcons.graph_ChatBubbles
            icon.width: 14
            icon.height: 14
            text: backend.get_element_loc("help")
            onClicked: {
                Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/issues")
            }
        }
        MenuItem{
            icon.name: FluentIcons.graph_Bug
            icon.width: 14
            icon.height: 14
            text: backend.get_element_loc("report_bug")
            onClicked: {
                Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/issues")
            }
        }
        MenuItem{
            icon.name: FluentIcons.graph_Globe
            icon.width: 14
            icon.height: 14
            text: backend.get_element_loc("open_site_prg")
            onClicked: {
                Qt.openUrlExternally("https://storik4pro.github.io/cdpiui/")
            }
        }
        MenuItem{
            icon.name: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/telegram.png"
            icon.width: 14
            icon.height: 14
            text: backend.get_element_loc("open_telegram_prg")
            onClicked: {
                Qt.openUrlExternally("https://t.me/storik4dev")
            }
        }
        MenuSeparator { }
        MenuItem{
            icon.name: FluentIcons.graph_Ringer
            icon.width: 14
            icon.height: 14
            text: backend.get_element_loc("notifications_settings")
            onClicked: {
                page_router.go("/system")
            }
        }
        MenuSeparator { }
        MenuItem{
            icon.name: FluentIcons.graph_Info
            icon.width: 14
            icon.height: 14
            text: backend.get_element_loc("about")
            onClicked: {
                page_router.go("/about")
            }
        }
        
    }

    ColumnLayout {
        id: base_layout
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter

        Rectangle {
            color: "#CCCCCC"
            height: 1
            Layout.fillWidth: true
            visible:false
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                id:rest1
                Layout.preferredHeight: Math.max(60, infoColumnLayout.implicitHeight + 20)
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.systemFillColorCautionBackground
                radius: 6
                border.color: Theme.res.cardStrokeColorDefault

                visible: isError
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
                            source:FluentIcons.graph_Warning
                            color:Theme.res.systemFillColorCaution
                        }
                        ColumnLayout{
                            Label{
                                text:backend.get_element_loc('warning')
                                font: Typography.bodyStrong
                            }
                            CopyableText{
                                Layout.preferredWidth:rest1.width - 100
                                text:backend.get_element_loc('update_fail') + " — " + errorText
                                font: Typography.body
                                wrapMode:Text.Wrap
                            }
                        }
                    }
                }
            }

            Row {
                height:30
                ColumnLayout {
                    height: parent.height
                    
                    Icon {
                        source: FluentIcons.graph_Recent
                        width:10
                        height:10
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        Layout.rightMargin:5
                    }
                }
                CopyableText {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr(backend.get_element_loc("update_t") + ": %1").arg(lastCheckedTime)
                }
            }

            ColumnLayout {
                Layout.fillWidth:true
                Rectangle {
                    id:cdpiVerRect
                    Layout.preferredHeight: Math.max(68, cdpiVerLay.implicitHeight + 40)
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    color: Theme.res.controlFillColorDefault
                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                    radius: 6
                    ColumnLayout {
                        id:cdpiVerLay
                        anchors.fill: parent
                        anchors.leftMargin:20
                        anchors.rightMargin:20
                        anchors.topMargin:20
                        anchors.bottomMargin:20
                        
                        ColumnLayout {
                            visible:isDownloading || isUpdating || getting_ready
                            RowLayout {
                                Label {
                                    id:mainLabel
                                    text:isError ? backend.get_element_loc("update_fail") :
                                         isDownloading ? backend.get_element_loc("update_downloading") :
                                         isUpdating ? backend.get_element_loc("update_check") :
                                         updatesAvailable ? backend.get_element_loc("update_available_t") : 
                                         getting_ready? backend.get_element_loc("getting_ready") : backend.get_element_loc("update_available_f")
                                }
                                Item {
                                    Layout.fillWidth:true
                                }
                                Label {
                                    id:speedLabel
                                    text:"2MB/s, " + backend.get_element_loc("after_update_title")
                                }
                            }
                            ProgressBar {
                                id: progressBar
                                visible:false
                                Layout.fillWidth:true
                                indeterminate:true
                            }
                            ProgressBar {
                                id: progressBarDownload
                                Layout.fillWidth:true
                                indeterminate:false
                                from: 0
                                to: 100
                            }
                        }
                        Grid  {
                            id:bodyGrid
                            Layout.fillWidth: true
                            Layout.maximumWidth: parent.width
                            clip:true
                            
                            property bool animating: false

                            move: Transition {
                                enabled: bodyGrid.animating
                                NumberAnimation {
                                    properties: "x,y"
                                    easing.period: 1.0
                                    easing.type: Easing.OutQuad
                                    
                                }
                            }

                            ColumnLayout {
                                height: bodyLayout.implicitHeight
                                Icon {
                                    id:logoIcon
                                    source:"qrc:/qt/qml/GoodbyeDPI_UI/res/image/logo.png"
                                    color: "#00000000"
                                    width: 20
                                    height: 20
                                    visible: bodyGrid.implicitWidth > bodyLayout.implicitWidth
                                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                    Layout.rightMargin: 10
                                }
                            }
                            Column {
                                id:bodyLayout
                                spacing: 2
                                RowLayout {
                                    Label {
                                        id:cdpiNameLabel
                                        font:Typography.bodyLarge
                                        text:"GOODBYEDPI UI"
                                        Layout.topMargin:0
                                    }
                                    Rectangle {
                                        id: badge
                                        clip: true  
                                        Layout.preferredHeight:cdpiNameLabel.implicitHeight - 1
                                        Layout.preferredWidth: badgeRowLayout.implicitWidth + 10
                                        color: isError ? "#A80000" :
                                               isDownloading||isUpdating||getting_ready ? Theme.accentColor.defaultBrushFor() :
                                               updatesAvailable ? "#FFEB3B" : 
                                               "#107C10"

                                        ColumnLayout {
                                            id: badgeRowLayout
                                            anchors.fill: parent
                                            anchors.leftMargin:5
                                            anchors.rightMargin:5
                                            anchors.topMargin:2
                                            anchors.bottomMargin:2
                                            RowLayout {
                                                spacing: 5
                                                Icon {
                                                    Layout.preferredWidth:15
                                                    Layout.topMargin: !updatesAvailable? 2 : 0
                                                    source: isError ? FluentIcons.graph_Warning :
                                                            isDownloading||isUpdating||getting_ready ? FluentIcons.graph_Sync :
                                                            updatesAvailable ? FluentIcons.graph_UpArrowShiftKey : 
                                                            FluentIcons.graph_Completed

                                                    color:isError || (!updatesAvailable && !(isDownloading||isUpdating||getting_ready)) ? "#FFF" : "#000"
                                                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                                }
                                                Label {
                                                    text: isError? backend.get_element_loc("update_fail").toUpperCase() :
                                                          isDownloading||isUpdating||getting_ready ? backend.get_element_loc("update_in_process_badge").toUpperCase() :
                                                          updatesAvailable ? backend.get_element_loc("new_vesion_available").toUpperCase() :
                                                          backend.get_element_loc("update_available_f").toUpperCase()

                                                    color:isError || (!updatesAvailable && !(isDownloading||isUpdating||getting_ready)) ? "#FFF" : "#000"
                                                    Layout.fillHeight:true
                                                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                                }
                                            }
                                        }
                                        Rectangle {
                                            id: shine
                                            anchors.verticalCenter: parent.verticalCenter
                                            visible: !isError
                                            width: 100 
                                            height: parent.height
                                            z: badge.z + 1

                                            gradient: Gradient {
                                                GradientStop { position: 0.0; color: "#00ffffff" }
                                                GradientStop { position: 0.5; color: "#80ffffff" }
                                                GradientStop { position: 1.0; color: "#00ffffff" }
                                            }

                                            rotation: 50
                                            transformOrigin: Item.Center
                                            x: -width
                                        }
                                        SequentialAnimation {
                                            id: shineAnim
                                            running: backend.getBool('APPEARANCE_MODE', 'animations') && 
                                                     (isDownloading||isUpdating||updatesAvailable||getting_ready) &&
                                                     !isError
                                            loops: Animation.Infinite

                                            PauseAnimation { duration: 1000 }

                                            ScriptAction {
                                                script: {
                                                    shine.x = -badge.width
                                                }
                                            }

                                            NumberAnimation {
                                                target: shine
                                                property: "x"
                                                from: -shine.width
                                                to: badge.width + shine.width
                                                duration: 1000
                                                easing.type: Easing.InOutQuad
                                            }
                                        }
                                        Component.onCompleted: {
                                            
                                        }
                                    }

                                }
                                Label {
                                    text: qsTr(backend.get_element_loc("version_now") + ": %1").arg(backend.get_version())
                                }
                                Label {
                                    text: qsTr(backend.get_element_loc("update_v") + ": %1").arg(availableVersion)
                                    visible: updatesAvailable
                                }
                                HyperlinkButton {
                                    id:aboutCurrentReleaseBtn
                                    text: backend.get_element_loc("release_notes")
                                    visible: !updatesAvailable
                                    FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                                    height:15
                                    font: Typography.caption
                                    width:implicitWidth - 15
                                    flat: true
                                    background: Rectangle {
                                        implicitWidth: 100
                                        implicitHeight: 40
                                        color: Theme.accentColor.defaultBrushFor()
                                        opacity: 0.1
                                        visible:aboutCurrentReleaseBtn.hovered
                                        radius:2
                                    }
                                    onClicked:{
                                        showWhatsNewCurrentVersion()
                                    }
                                }
                            }

                            Item { 
                                id:flowItem
                                width: 10
                                height: 10
                                
                            }
                            ColumnLayout {
                                id: buttonColumn
                                spacing: 4
                                //anchors.right: parent.right
                                RowLayout {
                                    Layout.topMargin:bodyGrid.columns === 1? 10:0
                                    Button {
                                        id: checkBtn
                                        text: updatesAvailable ? backend.get_element_loc("update_available_btn_t") : backend.get_element_loc("update_available_btn_f")
                                        highlighted: true
                                        visible:!isDownloading && !isUpdating && !getting_ready
                                        enabled:!goodCheck.is_process_alive() && !systemProcessHelper.is_alive()
                                        onClicked: {
                                            if (updatesAvailable) {
                                                enabled = false
                                                download_update()
                                            } else {
                                                checkForUpdates()
                                            }
                                        }
                                        

                                    }
                                    ColumnLayout {
                                        id:viewMoreLaySmall
                                        visible: false
                                        Button {
                                            id:viewMoreButtonSmall
                                            visible: false
                                            text: backend.get_element_loc("view_more")
                                            icon.name: FluentIcons.graph_More
                                            width: 20
                                            icon.width: 18
                                            icon.height: 18
                                            display: Button.IconOnly
                                            ToolTip.visible: hovered
                                            ToolTip.delay: 500
                                            ToolTip.text: text
                                            onClicked: {
                                                menu.popup()
                                            }
                                        }
                                    }
                                }
                                RowLayout {
                                    Layout.alignment: Qt.AlignRight
                                    Button {
                                        id:viewMoreButtonBig
                                        visible: bodyGrid.columns !== 1
                                        text: backend.get_element_loc("view_more")
                                        icon.name: FluentIcons.graph_More
                                        width: 20
                                        icon.width: 18
                                        icon.height: 18
                                        display: Button.IconOnly
                                        ToolTip.visible: hovered
                                        ToolTip.delay: 500
                                        ToolTip.text: text
                                        onClicked: {
                                            menu.popup()
                                        }
                                    }
                                }

                                onWidthChanged:Qt.callLater(recalculateGrid)
                            
                            }

                            onWidthChanged: {
                                recalculateGrid()
                            }

                            Component.onCompleted: {
                                Qt.callLater(recalculateGrid)
                            }
                            
                        }
                        Expander {
                            id:exp
                            expanded:true 
                            visible: updatesAvailable
                            Layout.fillWidth: true 
                            Layout.preferredWidth: Math.min(1000, parent.width) 
                            Layout.minimumWidth: 300 
                            Layout.maximumWidth: 1000
                            Layout.alignment: Qt.AlignHCenter 
                            _height:40

                            header: Label {
                                text: backend.get_element_loc("list_of_changes")
                                horizontalAlignment: Qt.AlignVCenter
                                font: Typography.body
                                
                            }
                            content: ColumnLayout{
                                spacing:2
                                width: parent.width 
                                ColumnLayout {
                                    spacing: 5
                                    Layout.leftMargin:15
                                    Layout.rightMargin:15
                                    Layout.preferredWidth:exp.implicitWidth
                                    Layout.alignment:Qt.AlignVCenter
                                    Rectangle {
                                        width: parent.width
                                        height: 10
                                        Layout.bottomMargin: 5
                                    }
                                    Label {
                                        id:listOfChangesLabel
                                        wrapMode:Text.Wrap
                                        Layout.fillWidth:true
                                        textFormat: Text.RichText
                                        text: listOfChangesLabelText
                                    }
                                    RowLayout {
                                        Item {
                                            Layout.fillWidth:true
                                        }
                                        HyperlinkButton {
                                            id:btn
                                            text: backend.get_element_loc("learn_more")
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
                                                showWhatsNew()
                                            }
                                        }
                                    }
                                    Rectangle {
                                        width: parent.width
                                        height: 10
                                        Layout.bottomMargin: 5
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Label {
                font:Typography.bodyStrong
                text:backend.get_element_loc("update_components")
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

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            Layout.fillWidth: true
                            text: backend.get_element_loc("goto_components_page")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                        }
                        Label {
                            Layout.fillWidth: true
                            text: backend.get_element_loc("components_tip")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
                            wrapMode: Text.Wrap
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
                            page_router.go("/system",{info:"Component"})
                        }
                    }
                }

                onClicked: {
                    page_router.go("/system",{info:"Component"})
                }
            }

            Label {
                font:Typography.bodyStrong
                text:backend.get_element_loc("linked_settings")
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
            Button {
                Layout.minimumHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                visible: backend.getBool('GLOBAL', 'developer_mode') || backend.is_debug()

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
                            text: backend.get_element_loc("developer_settings")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                        }
                        Label {
                            Layout.fillWidth: true
                            text: backend.get_element_loc("developer_settings_tip")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
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
                            context.router.go("/developerSettings")
                        }
                    }
                }

                onClicked: {
                    context.router.go("/developerSettings")
                }
            }
        }
    }

    Component.onCompleted: {
        lastCheckedTime = backend.getValue("GLOBAL", "lastcheckedtime")
        updatesAvailable = backend.getBool("GLOBAL", "updatesavailable")
        listOfChangesLabelText = backend.get_release_notes("prg")
        checkBtn.text = updatesAvailable ? backend.get_element_loc("update_available_btn_t") : backend.get_element_loc("update_available_btn_f")
        if (window.title !== title){
            multiWindow.close_window(title);
        }
        if (getting_ready){
            progressBar.visible = true
            checkBtn.enabled = false
        }
        
    }

    function recalculateGrid() {
        var btnW = buttonColumn.childrenRect.width
        if (cdpiVerLay.width < bodyLayout.implicitWidth + btnW  + logoIcon.implicitWidth + 10) {
            viewMoreLaySmall.visible = true
            viewMoreButtonSmall.visible = true
            bodyGrid.animating = backend.getBool('APPEARANCE_MODE', 'animations')
            bodyGrid.columns = 1
            flowItem.width = 0
            logoIcon.visible = false
        } else {
            viewMoreLaySmall.visible = false
            viewMoreButtonSmall.visible = false
            bodyGrid.columns = 4
            logoIcon.visible = true
            flowItem.width = cdpiVerLay.width - bodyLayout.implicitWidth - btnW  - 10 - logoIcon.implicitWidth
        }
        Qt.callLater(function() { bodyGrid.animating = false })
    }

    function checkForUpdates() {
        recalculateGrid()
        progressBarDownload.visible = false
        progressBar.visible = true
        speedLabel.text = " "
        checkBtn.enabled = false
        isUpdating = true
        backend.get_download_url()
    }

    function download_update() {
        recalculateGrid()
        isError = false
        checkBtn.enabled = false
        isDownloading = true
        progressBar.visible = true
        progressBarDownload.visible = false
        progressBarDownload.value = 0
        getting_ready = false
        speedLabel.text = backend.get_element_loc("calculating")
        checkBtn.text = backend.get_element_loc("update_available_btn_t")
        patcher.download_update()
    }

    function showWhatsNew() {
        Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/releases/latest")
    }

    function showWhatsNewCurrentVersion() {
        var version = backend.get_version()
        Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/releases/tag/"+version)
    }

    Connections {
        target:goodCheck
        function onStarted(){
            checkBtn.enabled = false;
        }
        function onProcess_finished_signal(){
            checkBtn.enabled = true;
        }
    }

    Connections {
        target: backend
        function onDownload_url_ready() {
            recalculateGrid()
            isError = false
            var version = arguments[0]
            progressBar.visible = false
            checkBtn.enabled = true
            isUpdating = false
            getting_ready = false
            if (version !== 'false') {
                updatesAvailable = true
                availableVersion = version
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
    }
    Connections {
        target: patcher
        function onSpeedInfoChanged(speed, time) {
            var timeLabel = "";
            var timeInt = parseInt(time)
            if (timeInt <= 60) {
                timeLabel = backend.get_element_loc("cleanup_m")
            } else {
                timeLabel = qsTr(backend.get_element_loc("cleanup_cq")).arg(Math.ceil(timeInt/60))
            }
            speedLabel.text = speed + " " + timeLabel
        }
        function onDownloadProgress() {
            recalculateGrid()
            var progress = arguments[0]
            progressBar.visible = false
            progressBarDownload.visible = true
            progressBarDownload.value = progress
            isError = false
            checkBtn.enabled = false
            isDownloading = true
            getting_ready = false
            checkBtn.text = backend.get_element_loc("update_available_btn_t")
            console.log(progress, progressBarDownload.value)
        }
        function onPreparationProgress() {
            recalculateGrid()
            progressBar.visible = true
            progressBarDownload.visible = false
            isDownloading = true
            checkBtn.enabled = false
            getting_ready = true
        }

        function onDownloadFinished() {
            var success = arguments[0]
            isDownloading = false
            getting_ready = false
            progressBarDownload.visible = false
            if (success === 'True') {
                mainLabel.text = backend.get_element_loc("installing")
                process.stop_service()
                patcher.get_ready_for_install()
                Qt.callLater(backend._update)
                Qt.callLater(WindowRouter.close, 0)
            } else {
                isError = true
                checkBtn.enabled = true
                checkBtn.text = backend.get_element_loc("retry")
                progressBar.visible = false
                errorText = success
            }
            Qt.callLater(recalculateGrid)
        }
    }
    Connections{
        target:systemProcessHelper
        function onProcessCheckedStarted(){
            checkBtn.enabled = false
        }
        function onProcessCheckedStopped(){
            checkBtn.enabled = true
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