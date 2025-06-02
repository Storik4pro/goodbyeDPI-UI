import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI
import QtQuick.Dialogs 

Page{
    id:page
    header: Item{}
    title: "Zapret"
    padding: 0
    topPadding: 24
    InfoBarManager{
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }
    InfoBarManager{
        id: info_manager_top
        target: page
        edge: Qt.TopEdge | Qt.LeftEdge
    }

    function reloadWindow() {
        info_manager_bottomright.clearAllInfo()
        
        pageLoader.sourceComponent = null;
        pageLoader.sourceComponent = pageComponent;
    }
    
Loader {
    id: pageLoader
    anchors.fill: parent
    sourceComponent: pageComponent

    FileDialog {
        id: fileDialogSave
        title: qsTr("Save File As")
        nameFilters: ["JSON Files (*.json)"]
        fileMode: FileDialog.SaveFile
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            backend.save_preset('zapret', filePath)
            process.update_preset()
        }
    }


    FileDialog {
        id: fileDialogOpen
        title: backend.get_element_loc("choose_file")
        nameFilters: [
            backend.get_element_loc("all_files_tip")+" (*.json; *.bat; *.cmd)",
            backend.get_element_loc("json_files_tip")+" (*.json)",
            backend.get_element_loc("bat_files_tip")+" (*.bat; *.cmd)",
        ]
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            var result = backend.load_preset('zapret', filePath)

            if (result === true) {
                pageLoader.sourceComponent = null
                pageLoader.sourceComponent = pageComponent
                process.update_preset()
            } else {
                info_manager_bottomright.show(InfoBarType.Error, "Error: Unknown error", 3000)
            }
        }
    }
    ListModel {
        id: askBlacklistFilesModel
        onCountChanged: {
            if (count === 0) {
                
            }
        }
    }

    Dialog {
        id: askBlacklistDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("blacklist_missing")
        Flickable {
            id: askFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: askColumn.implicitHeight
            ColumnLayout {
                anchors.fill: parent
                ColumnLayout {
                    id:askColumn
                    anchors.fill: parent
                    anchors.rightMargin:10
                    anchors.leftMargin:10
                    spacing: 5
                    width:400
                    Label {
                        id:askBlacklistDialogSubTitle
                        text:backend.get_element_loc("blacklist_missing_tip")
                        wrapMode:Text.Wrap
                        font:Typography.bodyLarge
                        Layout.preferredWidth:askColumn.width-20
                    }
                    Repeater {
                        model: askBlacklistFilesModel
                        
                        delegate: ColumnLayout {
                            Layout.fillWidth: true
                            Layout.preferredWidth: askColumn.width
                            Layout.alignment: Qt.AlignHCenter
                            
                            Loader {
                                id: askItemLoader
                                
                                Layout.preferredWidth: askColumn.width
                                
                                sourceComponent: askBlacklistComponent
                                property var modelData: model
                            }
                        }
                    }
                }
                ColumnLayout {
                    visible:false
                    id: progressRingColumn
                    anchors.centerIn: parent
                    ProgressRing {
                        anchors.horizontalCenter:parent.horizontalCenter
                        indeterminate: true
                        width: 30
                        height: 30
                        
                    }
                    Label {
                        text:backend.get_element_loc("update_in_process")
                    }
                }
                
                
            }
            ScrollBar.vertical: ScrollBar {
                
            }
        }
        footer: DialogButtonBox{
            Button{
                id:autocorrectAllButton
                text: backend.get_element_loc("autocorrect_all")
                highlighted: true
                visible:true
                onClicked: {
                    progressRingColumn.visible = true
                    askColumn.visible = false
                    autocorrectAllButton.enabled = false
                    cancelButton.enabled = false
                    
                    for (var i = askBlacklistFilesModel.count - 1; i >= 0; i--) {
                        var autocorrect = backend.get_load_preset_autocorrect_vars(
                            'zapret', 
                            askBlacklistFilesModel.get(i).blacklist_name
                            )
                        if (autocorrect === '') {
                            continue
                        }
                        var _result = backend.apply_autocorrect('zapret', 
                                                                askBlacklistFilesModel.get(i).blacklist_name, 
                                                                autocorrect)
                        if (_result === 'True') {
                            askBlacklistFilesModel.remove(i)
                        }
                    }
                    progressRingColumn.visible = false
                    askColumn.visible = true
                    autocorrectAllButton.enabled = true
                    cancelButton.enabled = true

                    if (askBlacklistFilesModel.count === 0) {
                        askBlacklistDialog.close()
                        
                        reloadWindow()
                    } else {
                        askBlacklistDialogSubTitle.text = backend.get_element_loc("blacklist_missing_tip_error")
                        autocorrectAllButton.enabled = false
                    }

                }
            }
            Button {
                id:cancelButton
                text: backend.get_element_loc("cancel")
                visible:true
                onClicked: {
                    backend.return_autocorrect_to_default("zapret")
                    askBlacklistDialog.close()
                    reloadWindow()
                    askToReopen()
                }
            }
            
        }
    }
    

    Component {
    id: pageComponent

ScrollablePage {
    topPadding: 0
    leftPadding: 0
    rightPadding: 0
    property var command: ""
    property var infoIndex: 0

    ListModel {
        id: blacklistFilesModel
        onCountChanged: {
            generateCommandLine()
        }
    }
    // DIALOGS

    Dialog {
        id: adDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.CloseOnEscape
        modal: true
        title: backend.get_element_loc("load_config_file")
        Flickable {
            id: adFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin: -10
            anchors.leftMargin: -10
            contentHeight: adColumn.implicitHeight
            ColumnLayout {
                id: adColumn
                anchors.fill: parent
                anchors.rightMargin: 10
                anchors.leftMargin: 10
                spacing: 5
                width: 400
                Image{
                    source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/ad.png"
                    Layout.preferredWidth:adDialog.width - 20
                    Layout.preferredHeight:220
                    asynchronous: true
                    clip: false
                    fillMode: Image.PreserveAspectFit
                }
                Label {
                    text: backend.get_element_loc("load_config_file_ad")
                    wrapMode: Text.Wrap
                    Layout.preferredWidth:adDialog.width - 20
                    font: Typography.body
                }
            }
            ScrollBar.vertical: ScrollBar {
            
            }
        }
        
        footer: DialogButtonBox{
            Button{
                text: backend.get_element_loc("got_it")
                highlighted: true
                onClicked: {
                    adDialog.close()
                    fileDialogOpen.open()
                }
            }
        }
    }

    
    // CONTENT
    ColumnLayout{
        id:base_layout
        anchors.margins: 20
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        Layout.leftMargin:24
        Layout.rightMargin:24
        visible:!backend.getBool('COMPONENTS', 'zapret')
        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter

            Flow {
                id: mainFlow
                Layout.fillWidth: true
                spacing: 20
                flow: Flow.LeftToRight

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
                        text: backend.get_element_loc("component_not_installed")
                        font: Typography.subtitle
                        wrapMode: Text.Wrap
                        Layout.alignment: Qt.AlignLeft
                        Layout.preferredWidth: Math.min(960, Math.max(300, base_layout.width - 20))
                        anchors.rightMargin: 20
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

                    Label {
                        id: timeLabel
                        wrapMode: Text.Wrap
                        text: backend.get_element_loc("component_not_installed_tip")
                        font: Typography.body
                        Layout.preferredWidth: Math.min(960, Math.max(300, base_layout.width - 20))
                        Layout.alignment: Qt.AlignLeft
                        visible: true
                    }
                    CopyableText {
                        id: errorLabel
                        text: ""
                        font: Typography.body
                        color: "#666666"
                        Layout.alignment: Qt.AlignLeft
                        visible: false
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
                Row{
                    height: 30
                    spacing: 10
                    ProgressRing {
                        id: progressBar
                        indeterminate: true
                        anchors {
                            rightMargin: 15
                            topMargin: 20
                            bottomMargin: 20
                        }
                        width:30
                        height:30
                        strokeWidth:4
                        visible: false
                    }

                }
                Button {
                    id: checkBtn
                    text: backend.get_element_loc("update_available_btn_t")
                    highlighted: true
                    enabled:!systemProcessHelper.is_alive()
                    Layout.minimumWidth: 50
                    Layout.alignment: Qt.AlignRight|Qt.AlignVCenter
                    
                    onClicked: {
                        download_component();
                    }
                }
                
                
            }
        }
    }

    ColumnLayout {
        id: mainLayoutt
        Layout.leftMargin:24
        Layout.rightMargin:24
        spacing: 15
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        visible:backend.getBool('COMPONENTS', 'zapret')
        Rectangle {
            id:rest1
            Layout.preferredHeight: Math.max(100, infoColumnLayout.implicitHeight + 20)
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 6
            visible: backend.getValue('GLOBAL', 'engine') === "zapret" ? false : true 
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
                            text:backend.get_element_loc('warn1')
                            font: Typography.body
                            wrapMode:Text.Wrap
                        }
                        Button{
                            text: backend.get_element_loc('fixnow')
                            onClicked:{
                                process.change_engine("zapret")
                                rest1.visible = false
                                askToReopen()
                            }
                        }
                    }

                }
            }
        }
        ListModel {
            id: componentModel
            Component.onCompleted: {
                var jsonFilePath = backend.get_config_path_value('zapret', cmbox.currentIndex)
                componentModel.clear()
                var data = backend.analyze_custom_parameters(jsonFilePath, true)
                for (var i = 0; i < data.length; ++i) {
                    var entry = data[i]
                    componentModel.append({
                        'componentId': i,
                        'blacklist_name': entry.blacklist_name,
                        'type': entry.type,
                        'windows': entry.windows 
                    })
                }
                
            }
        }
        ColumnLayout{
            spacing: 3
            width: parent.width
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width)
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
                            color: Theme.res.textFillColorSecondary
                            wrapMode: Text.Wrap
                        }
                    }

                    ComboBox {
                        id:cmbox
                        enabled:!advancedSwitch.checked
                        Layout.preferredWidth: rwlay.width < 550 ? rwlay.width-200 : 350
                        Layout.fillWidth: false
                        model: backend.get_presets('zapret')
                        currentIndex: backend.get_current_id("zapret") !== 0 ? backend.get_current_id("zapret") : 1
                        property var isInitializing: true
                        onCurrentIndexChanged: {
                            let selectedValue = model[currentIndex];

                            if (!isInitializing) {
                                askToReopen()
                            }
                            isInitializing = false

                            console.log(process.get_preset(), selectedValue)
                            backend.zapret_update_preset(selectedValue);
                            process.update_preset()
                            var jsonFilePath = backend.get_config_path_value('zapret', cmbox.currentIndex)
                            console.log(jsonFilePath)
                            componentModel.clear()
                            var data = backend.analyze_custom_parameters(jsonFilePath, true)
                            for (var i = 0; i < data.length; ++i) {
                                var entry = data[i]
                                componentModel.append({
                                    'componentId': i,
                                    'blacklist_name': entry.blacklist_name,
                                    'type': entry.type,
                                    'windows': entry.windows 
                                })
                            }
                            editModel.clear()
                            var data = backend.analyze_custom_parameters(jsonFilePath, false)
                            for (var i = 0; i < data.length; ++i) {
                                var entry = data[i]

                                for (var j = 0; j < entry.windows.length; ++j) {
                                    var _window = entry.windows[j]
                                    editModel.append({
                                        'blacklist_name': entry.blacklist_name,
                                        'type': entry.type,
                                        'windows': entry.windows,
                                        'args': _window.full_args,
                                        'values_before': _window.values_before,
                                        'values_after': _window.values_after
                                    })
                                    
                                }
                            }
                        }

                        focus: false
                        focusPolicy: Qt.NoFocus
                    }
                    Button {
                        text: "[" + backend.get_element_loc("_beta") + "] " + backend.get_element_loc("edit")
                        visible: backend.getBool('GLOBAL', 'usebetafeatures')
                        icon.name:FluentIcons.graph_Edit
                        icon.height:20
                        icon.width:20
                        Layout.preferredHeight:cmbox.height
                        Layout.preferredWidth:cmbox.height

                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text

                        display:Button.IconOnly
                        onClicked: {
                            editDialog.open()
                        }
                    }
                }
            }
            Dialog {
                id: editDialog
                x: Math.ceil((parent.width - width) / 2)
                y: Math.ceil((parent.height - height) / 2)
                width: Math.max(500, Math.ceil(parent.width / 3)) 
                contentHeight: parent.height < 500 ? Math.ceil(parent.height * 0.4) :parent.height - 300
                parent: Overlay.overlay
                modal: true
                title: backend.get_element_loc("edit") + ": " + cmbox.currentIndex + ".json"
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
                            id:rest111
                            Layout.preferredHeight: Math.max(60, infoColumnLayout1.implicitHeight + 20)
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignHCenter
                            color: Theme.res.controlFillColorDefault
                            radius: 6
                            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)

                            ColumnLayout{
                                id:infoColumnLayout1
                                anchors.verticalCenter: parent.verticalCenter  
                                RowLayout{    
                                    spacing:10
                                    height:20
                                    Layout.leftMargin:10
                                    
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
                                            Layout.preferredWidth:rest111.width - 100
                                            text:backend.get_element_loc('beta')
                                            font: Typography.body
                                            wrapMode:Text.Wrap
                                        }
                                    }

                                }
                            }
                        }
                        Rectangle {
                            id:restWarn
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
                                            text:backend.get_element_loc('edit_warn')
                                            font: Typography.body
                                            wrapMode:Text.Wrap
                                        }
                                    }

                                }
                            }
                        }
                        ListModel {
                            id: editModel
                            Component.onCompleted: {
                                var jsonFilePath = backend.get_config_path_value('zapret', cmbox.currentIndex)
                                editModel.clear()
                                var data = backend.analyze_custom_parameters(jsonFilePath, false)
                                for (var i = 0; i < data.length; ++i) {
                                    var entry = data[i]

                                    for (var j = 0; j < entry.windows.length; ++j) {
                                        var _window = entry.windows[j]
                                        editModel.append({
                                            'blacklist_name': entry.blacklist_name,
                                            'type': entry.type,
                                            'windows': entry.windows,
                                            'args': _window.full_args,
                                            'values_before': _window.values_before,
                                            'values_after': _window.values_after
                                        })
                                        
                                    }
                                }
                                
                                
                            }
                        }
                        Repeater {
                            model: editModel
                            
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                Layout.preferredWidth: column.width
                                Layout.alignment: Qt.AlignHCenter
                                
                                Loader {
                                    id: itemLoader
                                    
                                    Layout.preferredWidth: column.width
                                    sourceComponent: editComponent
                                    property var modelData: model
                                    property int modelIndex: index

                                    onLoaded: {
                                        
                                        //Layout.preferredHeight = sourceComponent.implicitHeight
                                    }
                                }

                            }
                        }
                        
                    }
                    ScrollBar.vertical: ScrollBar {
                        
                    }
                }
                footer: DialogButtonBox{
                    Button{
                        text: backend.get_element_loc("accept")
                        onClicked: {
                            var updatedData = []
                            for (var i = 0; i < editModel.count; ++i) {
                                var item = editModel.get(i)
                                updatedData.push({
                                    'blacklist_name': item.blacklist_name,
                                    'type': item.type,
                                    'args': item.args,
                                    'values_before': item.values_before,
                                    'values_after': item.values_after
                                })
                            }

                            backend.save_custom_parameters(cmbox.currentIndex, updatedData)
                            editDialog.close()
                        }
                    }
                    Button{
                        text: backend.get_element_loc("cancel")
                        highlighted: true
                        onClicked: {
                            editDialog.close()
                        }
                    }
                }
                
            }
            Label {
                text: backend.get_element_loc("blacklist_manage")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            Expander {
                id: exp
                expanded: !advancedSwitch.checked
                enabled:!advancedSwitch.checked
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                _height:68

                header: Label {
                    text: backend.get_element_loc("blacklist_used")
                    horizontalAlignment: Qt.AlignVCenter
                    font: Typography.body
                    width: exp.width - 100 - 30 - 30
                    wrapMode: Text.Wrap
                }
                subHeader: Label {
                    text: backend.get_element_loc("blacklist_used_tip")
                    horizontalAlignment: Qt.AlignVCenter
                    font: Typography.caption
                    color: Theme.res.textFillColorSecondary
                    width: exp.width - 100 - 30 
                    wrapMode: Text.Wrap
                }
                trailing:Button {
                    text: backend.get_element_loc("open_dir")

                    icon.name:FluentIcons.graph_FolderOpen
                    icon.height:18
                    icon.width:18

                    ToolTip.visible: hovered
                    ToolTip.delay: 500
                    ToolTip.text: text

                    display:Button.IconOnly
                    onClicked: {
                        backend.open_component_folder('zapret')
                    }
                }
                content: ColumnLayout {
                    id: cnt
                    spacing: 5
                    Layout.fillWidth: true

                    

                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.bottomMargin: 5
                        opacity: 0.0
                    }

                    Repeater {
                        model: componentModel
                        ColumnLayout {
                            Layout.fillWidth: true

                            Loader {
                                Layout.preferredWidth: mainLayoutt.width
                                sourceComponent: componentRow
                                onLoaded: {
                                    item.componentId = model.componentId
                                    item.blacklist_name = model.blacklist_name
                                    item.type = model.type
                                    item.windows = model.windows
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.leftMargin: -15
                                Layout.topMargin: 5
                                Layout.bottomMargin: 5
                                visible: componentId === componentModel.count - 1 ? false : true
                                height: 3
                                color: Qt.rgba(0.0, 0.0, 0.0, 0.3)
                                opacity: componentId === componentModel.count - 1 ? 0.0 : 0.3
                            }
                        }
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 10
                        Layout.topMargin: 5
                        opacity: 0.0
                    }

                }
                Component.onCompleted: {
                }
            }
            Component {
                id: componentRow
                RowLayout {
                    property string componentId
                    property string type
                    property string blacklist_name
                    property var windows

                    Layout.preferredWidth: mainLayoutt.width - 28
                    spacing: 10

                    ColumnLayout {
                        Layout.leftMargin:20
                        Label {
                            text: type === "iplist" ? backend.get_element_loc("iplist") :
                                type === "blacklist" ? backend.get_element_loc("blacklist") :
                                backend.get_element_loc("autoblacklist")
                            Layout.fillWidth: true
                            font: Typography.bodyStrong
                        }
                        CopyableText {
                            text: backend.get_element_loc("name") + ": " + blacklist_name
                            wrapMode:Text.Wrap
                            Layout.fillWidth: true
                        }

                    }
                    RowLayout{
                        
                        Button {
                            text: blacklist_name === 'russia-blacklist.txt' ? backend.get_element_loc("update"):backend.get_element_loc("edit")

                            icon.name:blacklist_name === 'russia-blacklist.txt' ? FluentIcons.graph_Download:FluentIcons.graph_Edit
                            icon.height:18
                            icon.width:18

                            visible: type !== "autoblacklist"

                            onClicked: {
                                if (blacklist_name === 'russia-blacklist.txt') {
                                    backend.update_list('zapret')
                                } else {
                                    backend.edit_blacklist('zapret', blacklist_name)
                                }
                            }
                        }
                        
                        Button {
                            text: backend.get_element_loc("blacklist_watch")
                            Layout.rightMargin: 20

                            icon.name:FluentIcons.graph_RedEye
                            icon.height:18
                            icon.width:18

                            ToolTip.visible: hovered
                            ToolTip.delay: 500
                            ToolTip.text: text

                            display:Button.IconOnly
                            Dialog {
                                id: blacklistDialog
                                x: Math.ceil((parent.width - width) / 2)
                                y: Math.ceil((parent.height - height) / 2)
                                width: Math.max(500, Math.ceil(parent.width / 3)) 
                                contentHeight: parent.height < 500 ? Math.ceil(parent.height * 0.4) :parent.height - 300
                                parent: Overlay.overlay
                                modal: true
                                title: backend.get_element_loc("blacklist_watch_title")
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
                                        Label {
                                            text:blacklist_name
                                            wrapMode:Text.Wrap
                                            font:Typography.bodyLarge
                                        }
                                        ListModel {
                                            id: _settingsModel
                                            
                                        }
                                        Repeater {
                                            model: _settingsModel
                                            
                                            delegate: ColumnLayout {
                                                Layout.fillWidth: true
                                                Layout.preferredWidth: column.width
                                                Layout.alignment: Qt.AlignHCenter
                                                
                                                Loader {
                                                    id: itemLoader
                                                    
                                                    Layout.preferredWidth: column.width
                                                    Layout.preferredHeight: sourceComponent.implicitHeight
                                                    sourceComponent: blacklistComponent
                                                    property var modelData: model
                                                }
                                            }
                                        }
                                        
                                    }
                                    ScrollBar.vertical: ScrollBar {
                                        
                                    }
                                }
                                footer: DialogButtonBox{
                                    Button{
                                        text: "OK"
                                        highlighted: true
                                        width:Math.ceil(blacklistDialog.width / 2) - 20
                                        onClicked: {
                                            blacklistDialog.close()
                                        }
                                    }
                                }
                                
                            }
                            onClicked: {
                                _settingsModel.clear()
                                for (var i = 0; i < windows.count; ++i) {
                                    var _window = windows.get(i)
                                    _settingsModel.append({
                                        'itemIndex': i,
                                        'args': _window.full_args,
                                        'values_before': _window.values_before,
                                        'values_after': _window.values_after
                                    })
                                    
                                }
                                blacklistDialog.open()
                            }

                            
                        }
                    }
                }
            }


        }
        ColumnLayout {
            id: mainLayout
            spacing: 3
            width: parent.width

            Label {
                text: backend.get_element_loc("zapret_advansed")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            Rectangle {
                Layout.preferredHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width)
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
                        text: backend.get_element_loc("zapret_manual_input")
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
                        id:advancedSwitch
                        property bool isInitializing: backend.getBool('ZAPRET', 'use_advanced_mode') 
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                        checked: backend.getBool('ZAPRET', 'use_advanced_mode')
                        onCheckedChanged: {
                            if (!isInitializing){
                                backend.toggleBool('ZAPRET', 'use_advanced_mode', checked)
                                process.update_preset()
                                askToReopen()
                            }
                            isInitializing = false
                        }
                    }
                }
            }

            Label {
                text: backend.get_element_loc("config_settings")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            RowLayout{
                enabled:advancedSwitch.checked
                Layout.fillWidth:true
                spacing: 10
                ColumnLayout {
                    Layout.preferredWidth:mainLayoutt.width - clmn1.implicitWidth - 10
                    Label {
                        horizontalAlignment: Text.AlignLeft
                        Layout.preferredWidth:mainLayoutt.width - clmn1.implicitWidth
                        text: backend.get_element_loc("config_now_use") + ": "
                        wrapMode:Text.Wrap
                    }
                    CopyableText {
                        horizontalAlignment: Text.AlignLeft
                        Layout.preferredWidth:mainLayoutt.width - clmn1.implicitWidth
                        text:process.get_config_name('zapret')
                        wrapMode:Text.Wrap
                    }

                }
                ColumnLayout{
                    id:clmn1
                    Layout.alignment: Qt.AlignRight
                    Layout.fillWidth:true
                    
                    RowLayout{
                    Layout.alignment: Qt.AlignRight
                    Button {
                        text: backend.get_element_loc("load_config_file")
                        display: Button.IconOnly
                        icon.name: FluentIcons.graph_OpenFile 
                        icon.height: 20
                        icon.width:20
                        onClicked: {
                            if (backend.getBool("GLOBAL", "isadconvertshown")) {
                                fileDialogOpen.open()
                            } else {
                                adDialog.open()
                                backend.toggleBool("GLOBAL", "isadconvertshown", true)
                            }
                        }
                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                    }
                    Button {
                        text: backend.get_element_loc("export_config_file")
                        display: Button.IconOnly
                        icon.name: FluentIcons.graph_SaveAs
                        icon.height: 20
                        icon.width:20
                        onClicked: {
                            fileDialogSave.open()
                        }
                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                    }

                    Button {
                        text: backend.get_element_loc("reset_config")
                        display: Button.IconOnly
                        icon.name: FluentIcons.graph_Refresh
                        icon.height: 20
                        icon.width:20
                        onClicked: {
                            backend.return_to_default('zapret')
                            process.update_preset()
                            pageLoader.sourceComponent = null
                            pageLoader.sourceComponent = pageComponent
                        }
                        ToolTip.visible: hovered
                        ToolTip.delay: 500
                        ToolTip.text: text
                    }
                    }

                }
            }

            Label {
                text: backend.get_element_loc("custom_params")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            Rectangle {
                Layout.preferredHeight: customParameters.implicitHeight + 20
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width)
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

                    

                    TextArea  {
                        id: customParameters
                        placeholderText: backend.get_element_loc("custom_params_placeholder")
                        wrapMode: TextEdit.Wrap
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        FluentUI.radius:6
                        enabled:advancedSwitch.checked
                        property bool isInitializing: false
                        onTextChanged: {
                            if (!isInitializing) {
                                var cursorPosition = customParameters.cursorPosition
                                var previousText = text
                                var newText = text.replace(/[^0-9a-zA-Z:"><\/\\.\-_\s,=+]/g, '')
                                if (newText !== previousText) {
                                    var diff = previousText.length - newText.length
                                    text = newText
                                    customParameters.cursorPosition = cursorPosition - diff
                                    info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                }
                                saveCustomParameters()
                                generateCommandLine()
                            }
                            isInitializing = false
                        }
                        
                        Component.onCompleted: {
                            text = backend.get_from_config("ZAPRET", "custom_parameters")
                            Qt.callLater(generateCommandLine)
                        }
                        function saveCustomParameters() {
                            var params = customParameters.text.trim()
                            var processedParams = params.replace(/=/g, ' ').replace(/"/g, '')
                            if (processedParams !== backend.get_from_config("ZAPRET", "custom_parameters")) {
                                askToReopen()
                            }
                            backend.set_to_config("ZAPRET", "custom_parameters", processedParams)
                        }
                    }


                }
            }
            Button{
                id:btn2
                Layout.preferredHeight: 34
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
                        source: FluentIcons.graph_FastForward
                        Layout.preferredHeight:18
                        Layout.preferredWidth:20
                    }
                    ColumnLayout{
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            text: backend.get_element_loc('qchk_preset')
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
                            page_router.go("/additional",{info:"GoodCheck:startNEW"})
                        }
                    }
                }
                
                onClicked: {
                    page_router.go("/additional",{info:"GoodCheck:startNEW"})
                }
                
            }

            Label {
                text: backend.get_element_loc("output_prompt")
                font: Typography.bodyStrong
                Layout.topMargin: 15
            }
            ColumnLayout {
                id: contentLayout
                Layout.minimumHeight:100
                Layout.preferredHeight:commandLineOutput.implicitHeight + 20
                
                Rectangle {
                    id: rest
                    Layout.fillWidth: true
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
                        text: command
                        wrapMode: Text.Wrap
                        font.pixelSize: 14
                        font.family: "Cascadia Code"
                        color: "#D4D4D4"
                        height: implicitHeight
                    }
                }
            }

        }
    
    }
    // COMPONENTS
    
    Component {
        id: blacklistComponent
        ColumnLayout {
            id:rest
            Layout.fillWidth: true
            

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 5

                Label {
                    id:itemLabel
                    text: "--new"
                    font: Typography.bodyStrong
                    Layout.fillWidth:true
                    wrapMode: Text.Wrap
                    height:20
                    Layout.maximumHeight:20
                    Layout.preferredWidth: parent.width
                }
                ColumnLayout {
                    Layout.minimumHeight:70
                    Layout.preferredHeight:commandLineOutput1.implicitHeight + 20
                    
                    Rectangle {
                        id: rest1
                        Layout.fillWidth: true
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
                            id: commandLineOutput1
                            anchors.fill: parent
                            anchors.margins: 10
                            width: parent.width - 20
                            text: modelData.args
                            wrapMode: Text.Wrap
                            font.pixelSize: 14
                            font.family: "Cascadia Code"
                            color: "#D4D4D4"
                            height: implicitHeight
                        }
                    }
                }
            
            }
        }
    }
    Component {
        id: editComponent

        ColumnLayout {
            id: rest
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 5

                Label {
                    id: itemLabel
                    text: "--new (" + (modelData ? modelData.blacklist_name : "") + ")"
                    font: Typography.bodyStrong
                    Layout.fillWidth: true
                    wrapMode: Text.Wrap
                    height: 20
                    Layout.maximumHeight: 20
                    Layout.preferredWidth: parent.width
                }
                ColumnLayout {
                    Layout.minimumHeight: 70
                    Layout.preferredHeight: customParameters.implicitHeight + 20

                    TextArea {
                        id: customParameters
                        placeholderText: backend.get_element_loc("custom_params_placeholder")
                        wrapMode: TextEdit.Wrap
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        FluentUI.radius: 6
                        property bool isInitializing: false

                        onTextChanged: {
                            if (!isInitializing) {
                                var cursorPosition = customParameters.cursorPosition
                                var previousText = text
                                var newText = text.replace(/[^0-9a-zA-Z:"><\/\\.\-_\s,=+]/g, '')
                                if (newText !== previousText) {
                                    var diff = previousText.length - newText.length
                                    text = newText
                                    customParameters.cursorPosition = cursorPosition - diff
                                    info_manager_bottomright.show(InfoBarType.Warning, backend.get_element_loc("warn_entry"), 3000)
                                }
                                editModel.set(modelIndex, { "args": text })
                            }
                            isInitializing = false
                        }

                        Component.onCompleted: {
                            text = (modelData ? modelData.args : "")
                        }
                    }
                }
            }
        }
    }

    ColumnLayout{
        anchors.margins: 20
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
        Layout.minimumWidth: 300
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        Layout.leftMargin:24
        Layout.rightMargin:24
        Label {
            text: backend.get_element_loc("linked_settings")
            font: Typography.bodyStrong
            Layout.topMargin: 15
        }
        IconButton{
            text: backend.get_element_loc("linked_open_component_url")
            icon.name: FluentIcons.graph_OpenInNewWindow
            icon.width: 18
            icon.height: 18
            spacing: 5
            LayoutMirroring.enabled: true
            onClicked: {
                Qt.openUrlExternally("https://github.com/bol-van/zapret")
            }
        }
        IconButton{
            text: backend.get_element_loc("linked_manage_components")
            icon.name: FluentIcons.graph_ChevronRight
            icon.width: 18
            icon.height: 18
            spacing: 5
            LayoutMirroring.enabled: true
            onClicked: {
                page_router.go("/system",{info:"Component"})
            }
        }
    }

    Component{
        id: comp_action
        Button{
            text: backend.get_element_loc("pseudoconsole_restart")
            onClicked: {
                var result = process.stop_process()
                if (result) {
                    process.start_process()
                    info_manager_bottomright.show(InfoBarType.Success, backend.get_element_loc("save_complete"), 3000)
                } else {
                    info_manager_bottomright.show(InfoBarType.Error, backend.get_element_loc("error_title"), 10000)
                }
                infoIndex = 0
                infoControl.remove(model.index)
            }
        }
    }

    function askToReopen() {
        if ((!process.is_process_alive() && !backend.is_debug()) || infoIndex !== 0 || !backend.getValue('GLOBAL', 'engine') === "zapret") {
            return
        }
        if (page.width < 700) {
            infoIndex = info_manager_bottomright.showWarning(backend.get_element_loc("process_reopen_needed_title"),0,qsTr(""),comp_action)
        } else {
            infoIndex = info_manager_bottomright.showWarning(backend.get_element_loc("process_reopen_needed"),0,qsTr(""),comp_action)
        }
        
    }

    function generateCommandLine() {
        command = "winws.exe"

        if (customParameters.text.trim() !== "") {
            command += " " + customParameters.text.trim()
        }
    }
    function download_component() {
        progressBar.visible = true;
        checkBtn.enabled = false;
        timeLabel.visible = false;
        mainLabel.text = backend.get_element_loc('component_not_installed_p');
        errorLabel.visible = true;
        errorLabel.text = "";
        process.stop_process()
        backend.download_component("zapret", false);
    }

    Connections {
        target: backend
        function onComponent_installing_finished() {
            var success = arguments[0];
            progressBar.visible = false;
            checkBtn.enabled = true;
            console.log(success);
            if (success === 'True') {
                
                reloadWindow()
            } else {
                checkBtn.enabled = true;
                checkBtn.text = backend.get_element_loc("retry");
                errorLabel.visible = true;
                errorLabel.text = success;
                mainLabel.text = backend.get_element_loc('component_not_installed_e');
            }
        }
        function onInformation_requested(target, info) {
            askBlacklistDialog.open()
            if (target === "load_preset:zapret") {
                askBlacklistFilesModel.clear()
                for (var i = 0; i < info.length; i++) {
                    askBlacklistFilesModel.append(info[i])
                }
                
            }
        }
    }

}
}
}
Component {
    id: askBlacklistComponent
    ColumnLayout {
        id:rest
        Layout.fillWidth: true
        property var autocorrect: modelData? backend.get_load_preset_autocorrect_vars('zapret', modelData.blacklist_name) : ""
        
        FileDialog {
            id: fileDialogOpenBlacklist
            title: backend.get_element_loc("choose_file")
            nameFilters: modelData ? modelData.type === 'blacklist' ? [
                backend.get_element_loc("blacklist_files_tip")+" (*.txt)",
            ] : [
                backend.get_element_loc("bin_files_tip")+" (*.bin)",
            ] : "All files (*)"
            onAccepted: {
                var filePath = selectedFile.toString().replace("file:///", "")

                var _result = backend.apply_autocorrect('zapret', 
                                                        modelData.blacklist_name, 
                                                        filePath)
                if (_result === 'True') {
                    if (askBlacklistFilesModel.count <= 1) {
                        askBlacklistDialog.close()
                        
                        reloadWindow()
                    }
                    for (var i = 0; i < askBlacklistFilesModel.count; i++) {
                        if (askBlacklistFilesModel.get(i).blacklist_name === modelData.blacklist_name) {
                            askBlacklistFilesModel.remove(i)
                            break
                        }
                    }
                } else {
                    autocorrectLabel.text = backend.get_element_loc("autocorrect_manual_error") + "\n" + _result
                    autocorrectIcon.source = FluentIcons.graph_IncidentTriangle
                    autocorrectIcon.color = Theme.res.systemFillColorCaution
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 5
            Label {
                id:itemLabel
                text: modelData ? modelData.blacklist_name : "template"
                font: Typography.bodyStrong
                Layout.fillWidth:true
                wrapMode: Text.Wrap
                height:20
                Layout.maximumHeight:20
                Layout.preferredWidth: parent.width
            }
            ColumnLayout {
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter
                    color: Theme.res.controlFillColorDefault
                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                    radius: 6
                    Layout.preferredHeight:clmn.implicitHeight
                    ColumnLayout{
                        id:clmn
                        RowLayout{
                            Layout.leftMargin:10
                            Layout.topMargin:10
                            Layout.fillWidth: true
                            Icon{
                                id:autocorrectIcon
                                Layout.preferredHeight:15
                                Layout.preferredWidth:15
                                source:autocorrect === ''? FluentIcons.graph_Cancel:FluentIcons.graph_CheckMark
                                color:autocorrect === ''? Theme.res.systemFillColorCritical: Theme.res.systemFillColorSuccess
                            }
                            Label {
                                id:autocorrectLabel
                                text: autocorrect === ''? backend.get_element_loc("autocorrect_error") : backend.get_element_loc("autocorrect_success")
                                wrapMode:Text.Wrap
                                font:Typography.body
                                Layout.fillWidth: true
                            }
                            
                        }
                        CopyableText {
                            Layout.leftMargin:10
                            Layout.topMargin:2
                            text: autocorrect
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                            visible: autocorrect !== ''
                        }
                        RowLayout {
                            Layout.leftMargin:10
                            Layout.bottomMargin:10
                            Layout.maximumWidth: 300
                            Button {
                                id:applyButton
                                text: backend.get_element_loc("accept")
                                visible: autocorrect !== ''
                                highlighted: true
                                onClicked: {
                                    var _result = backend.apply_autocorrect('zapret', 
                                                                       modelData.blacklist_name, 
                                                                       autocorrect)
                                    if (_result === 'True') {
                                        if (askBlacklistFilesModel.count <= 1) {
                                            askBlacklistDialog.close()
                                            
                                            reloadWindow()
                                        }
                                        for (var i = 0; i < askBlacklistFilesModel.count; i++) {
                                            if (askBlacklistFilesModel.get(i).blacklist_name === modelData.blacklist_name) {
                                                askBlacklistFilesModel.remove(i)
                                                break
                                            }
                                        }
                                        
                                    } else {
                                        autocorrectLabel.text = backend.get_element_loc("autocorrect_error") + "\n" + _result
                                        autocorrectIcon.source = FluentIcons.graph_IncidentTriangle
                                        autocorrectIcon.color = Theme.res.systemFillColorCaution
                                        applyButton.text = backend.get_element_loc("retry")
                                    }
                                }
                            }
                            Button {
                                text: backend.get_element_loc("open_file")
                                visible: autocorrect !== ''
                                icon.name: FluentIcons.graph_FolderOpen
                                icon.height: 18
                                icon.width: 18
                                onClicked: {
                                    backend.open_folder(autocorrect)
                                }
                            }
                            Button {
                                text: backend.get_element_loc("select_manually")
                                icon.name: FluentIcons.graph_OpenFile
                                icon.height: 18
                                icon.width: 18
                                onClicked: {
                                    fileDialogOpenBlacklist.open()
                                }
                            }
                        }
                    }
                }
            }
        
        }
    }
}
Component.onCompleted:{
        if (window.title !== title){
            multiWindow.close_window(title);
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
