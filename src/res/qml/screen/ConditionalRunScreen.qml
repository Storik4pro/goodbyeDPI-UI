import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import QtQuick.Dialogs 
import GoodbyeDPI_UI
import QtQuick.Templates as T

ScrollablePage {
    id: page
    title: backend.get_element_loc('conditional_run_page_title')
    header:ColumnLayout{
        TabBar {
            id: bar
            width: parent.width
            clip: true
            Repeater {
                model: [
                    backend.get_element_loc("settings"),
                    backend.get_element_loc("conditions"),
                    backend.get_element_loc("about")
                ]
                TabButton {
                    id: btn_tab
                    text: model.modelData
                    onClicked: {
                        settingsLayout.visible = false
                        conditionListLayout.visible = false
                        notificationsLayout.visible = false
                        aboutLayout.visible = false
                        if (model.index == 0) {
                            settingsLayout.visible = true
                        } else if (model.index == 1) {
                            conditionListLayout.visible = true
                        } else if (model.index == 2) {
                            aboutLayout.visible = true
                        }
                    }
                }
            }
            Layout.topMargin: 46
            Layout.leftMargin: 20
        }
    }
    property var canEdit:!systemProcessHelper.is_alive()
    property var canRun: systemProcessHelper.is_start_process_checker_availible()

    property var currentSettingsEdit: ""
    property var locPriority: [backend.get_element_loc('highest'), backend.get_element_loc('default'), backend.get_element_loc('lowest')]
    property var locAction: [backend.get_element_loc('kill'), backend.get_element_loc('run')]
    property var locActionEngine: ["GoodbyeDPI", "Zapret", "ByeDPI", "SpoofDPI"]
    property var locType: [backend.get_element_loc('single_action'), backend.get_element_loc('track')]
    function hideAll() {
        drawerContentRect.visible = true
        conditionSettings.visible = true
        actionSettings.visible = false
        stateSettings.visible = false
        appSettings.visible = false
        conditionVariants.visible = false
    }

    FileDialog {
        id: fileDialogOpenEXE
        title: backend.get_element_loc("choose_file")
        nameFilters: [
            backend.get_element_loc("exe_files_tip")+" (*.exe)",
        ]
        onAccepted: {
            var filePath = selectedFile.toString().replace("file:///", "")
            exeNameInput.text = filePath
        }
    }
    FolderDialog {
        id: fileDialogOpenFolder
        currentFolder: "file:///C:\\Progra~1\\WindowsApps"
        title: backend.get_element_loc("choose_folder")
        onAccepted: {
            var filePath = selectedFolder.toString().replace("file:///", "").replace(/\//g, "\\")
            uwpPathInput.text = filePath
        }
    }
    Dialog {
        id: addAppDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("add_app_manually")
        Flickable {
            id: addAppFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: addColumn.implicitHeight
            ColumnLayout {
                anchors.fill: parent
                anchors.rightMargin:20
                ColumnLayout {
                    id:addColumn
                    anchors.fill: parent
                    anchors.rightMargin:10
                    anchors.leftMargin:10
                    spacing: 5
                    width:400
                    ColumnLayout {
                        id:addClassicApp
                        Label {
                            text: backend.get_element_loc("add_classic_app")
                            font: Typography.bodyStrong
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:addColumn.width
                        }
                        Label {
                            text: backend.get_element_loc("add_classic_app_tip")
                            font: Typography.body
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:addColumn.width
                        }
                        RowLayout {
                            Layout.preferredWidth:addColumn.width
                            TextField {
                                id: exeNameInput
                                placeholderText: backend.get_element_loc("add_classic_app_placeholder")
                                Layout.preferredWidth:addColumn.width-addEXEButton.implicitWidth+15
                                onTextChanged: {
                                    if (text != '') {
                                        orSeparator.visible = false
                                        addUniversalApp.visible = false
                                        addAppPreview.visible = true
                                        previewLabel.text = text.replace('.exe', '')
                                        addButton.enabled = true
                                        
                                    } 
                                    else {
                                        orSeparator.visible = true
                                        addUniversalApp.visible = true
                                        addAppPreview.visible = false
                                        addButton.enabled = false
                                    }
                                }
                            }
                            Button {
                                id:addEXEButton
                                text: backend.get_element_loc("select_file")
                                display: Button.IconOnly
                                icon.name:FluentIcons.graph_OpenFile
                                icon.height: 20
                                icon.width:20
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                                onClicked: {
                                    fileDialogOpenEXE.open()
                                }
                            }
                        }
                    }

                    
                    Label {
                        id:orSeparator
                        text: backend.get_element_loc("or_separator")
                        font: Typography.bodyStrong
                        Layout.alignment: Qt.AlignHCenter
                    }

                    ColumnLayout {
                        id:addUniversalApp
                        Label {
                            text: backend.get_element_loc("add_uwp_app")
                            font: Typography.bodyStrong
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:addColumn.width
                        }
                        Label {
                            text: backend.get_element_loc("add_uwp_app_tip")
                            font: Typography.body
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:addColumn.width
                        }
                        RowLayout {
                            Layout.preferredWidth:addColumn.width
                            TextField {
                                id: uwpPathInput
                                placeholderText: backend.get_element_loc("add_uwp_app_placeholder")
                                Layout.preferredWidth:addColumn.width-addFolderButton.implicitWidth+15
                                onTextChanged: {
                                    if (text != '') {
                                        orSeparator.visible = false
                                        addClassicApp.visible = false
                                        addAppPreview.visible = true
                                        previewLabel.text = text
                                        addButton.enabled = true
                                    } 
                                    else {
                                        orSeparator.visible = true
                                        addClassicApp.visible = true
                                        addAppPreview.visible = false
                                        addButton.enabled = false
                                    }
                                }
                            }
                            Button {
                                id: addFolderButton
                                text: backend.get_element_loc("select_folder")
                                display: Button.IconOnly
                                icon.name:FluentIcons.graph_FolderOpen
                                icon.height: 20
                                icon.width:20
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                                onClicked: {
                                    fileDialogOpenFolder.open()
                                }
                            }
                        }
                    }
                    ColumnLayout {
                        id:addAppPreview
                        visible:false
                        Label {
                            text: backend.get_element_loc("preview")
                            font: Typography.bodyStrong
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:addColumn.width
                        }
                        Rectangle {
                            Layout.preferredHeight: Math.max(60, appLayout.implicitHeight + 20)
                            Layout.fillWidth: true
                            color: Theme.res.subtleFillColorTertiary
                            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                            radius: 0
                            ColumnLayout {
                                spacing: 0
                                anchors.fill: parent
                                anchors{
                                    leftMargin: 10
                                    rightMargin: 10
                                }
                                RowLayout {
                                    id: appLayout
                                    spacing: 5
                                    Image {
                                        Layout.preferredHeight: 40
                                        Layout.preferredWidth: 40
                                        visible: true
                                        source: {
                                            var appIcon = "qrc:/qt/qml/GoodbyeDPI_UI/res/image/app.png";
                                            var exe_path = previewLabel.text + '.exe'
                                            for (var i = 0; i < appsModel.count; ++i) {
                                                var app = appsModel.get(i);
                                                if (app.exe_name.toLowerCase() === previewLabel.text.replace(/\//g, "\\").toLowerCase()) {
                                                    appIcon = app.icon;
                                                    break;
                                                }
                                            }
                                            if (backend.is_exe_file(exe_path)||backend.is_uwp_folder(exe_path)) {
                                                appIcon = 'image://icons/'+exe_path
                                            }
                                            return appIcon;
                                            }
                                    }
                                    Label {
                                        id: previewLabel
                                        text: ""
                                        font: Typography.bodyStrong
                                        Layout.fillWidth: true
                                        wrapMode: Text.WrapAnywhere
                                        height: 20
                                        Layout.preferredWidth: parent.width
                                    
                                    }
                                }
                            }
                        }
                        
                    }
                }
            }
        ScrollBar.vertical: ScrollBar {
                
            }
        }
        footer: DialogButtonBox{
            Button {
                id:addButton
                text: backend.get_element_loc("add")
                visible:true
                highlighted:true
                enabled:false
                onClicked: {
                    var appName = exeNameInput.text != ''? previewLabel.text + ".exe" : previewLabel.text
                    exeNameInput.text = ''
                    uwpPathInput.text = ''
                    for (var i = 0; i < appsModel.count; ++i) {
                        var app = appsModel.get(i);
                        if (app.exe_name.toLowerCase() === appName.toLowerCase() ||
                            app.path.toLowerCase() === appName.toLowerCase()) {
                            addAppDialog.close();
                            return;
                        }
                    }
                    
                    appsModel.append({
                        'name': appName,
                        'path': appName,
                        'exe_name': appName,
                        'icon': appName ? "image://icons/" + appName : FluentIcons.graph_AppIconDefault,
                    })

                    addAppDialog.close()
                }
            }
            Button {
                text: backend.get_element_loc("cancel")
                visible:true
                onClicked: {
                    addAppDialog.close()
                }
            }
            
        }
    }
    property var somethingChanged: false
    property var fileNowEdit: ""

    property string condVarVariant1: backend.get_element_loc('conditional_util_variant1').arg(qsTr(btnAppName.text)).arg(qsTr(btnState.text)).toUpperCase()
    property string condVarVariant2: backend.get_element_loc('conditional_util_variant2').arg(qsTr(btnAppName.text)).arg(qsTr(btnState.text)).toUpperCase()
    property var condVarVariantIndex:0                
    Drawer {
        id: drawer
        width: Overlay.overlay.width
        height: Overlay.overlay.height - header.height - 2
        edge: Qt.BottomEdge
        closePolicy: Popup.NoAutoClose
        modal: true
        onClosed: {
            drawerContentRect.visible = false
            conditionSettings.visible = false
            actionSettings.visible = false
            stateSettings.visible = false
            appSettings.visible = false
            conditionVariants.visible = false
            appsModel.clear()
            addAppDialog.close()
            condVarVariantIndex = 0
            cond_var_list_view.currentIndex = 0
            list_view.currentIndex = 0
            targetComponentComboBox.currentIndex = 0
            targetActionComboBox.currentIndex = 0
            priorityComboBox.currentIndex = 1
            somethingChanged = false
            fileNowEdit = ""
        }
        onOpened:{
            if (fileNowEdit !== "") {
                var tasklist = systemProcessHelper.get_task(fileNowEdit)
                for (var i = 0; i < tasklist.length; i++) {
                    var task = tasklist[i]
                    list_view.currentIndex = task.state
                    targetComponentComboBox.currentIndex = task.action_engine
                    targetActionComboBox.currentIndex = task.action
                    priorityComboBox.currentIndex = task.priority
                    cond_var_list_view.currentIndex = task.type
                    condVarVariantIndex = task.type
                    appsModel.clear()
                    for (var j = 0; j < task.apps.length; ++j) {
                        var app = task.apps[j];
                        appsModel.append({
                            'name': app[0],
                            'path': app[1],
                            'exe_name': app[0],
                            'icon': app[0] ? "image://icons/" + app[0] : FluentIcons.graph_AppIconDefault,
                        })
                    }
                }

            }
            somethingChanged = false
        }
        ColumnLayout{
            Layout.fillWidth: true
            RowLayout {
                Layout.margins: 20
                Layout.fillWidth: true
                Label {
                    id: drawerLabel
                    text: backend.get_element_loc('add_condition')
                    font: Typography.title
                }
                Item {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 
                        drawer.width - 
                        (drawerLabel ? drawerLabel.implicitWidth: 0) - 
                        (cancelButton ? cancelButton.width: 0) - 
                        (saveButton ? saveButton.width:0) - 40-10-20
                }
                Button {
                    id: saveButton
                    text:backend.get_element_loc('save')
                    highlighted:true
                    enabled: appsModel.count !== 0 && targetComponentComboBox.currentIndex !== 0 && canEdit
                    Layout.rightMargin:10
                    Layout.alignment: Qt.AlignRight|Qt.AlignVCenter
                    icon.name: FluentIcons.graph_Save
                    icon.height: 20
                    icon.width:20
                    Layout.preferredWidth:150
                    onClicked: {
                        var applist = []
                        for (var i = 0; i < appsModel.count; ++i) {
                            var app = appsModel.get(i);
                            applist.push([app.exe_name, app.path]);
                        }
                        var condition = {
                            'type': cond_var_list_view.currentIndex,
                            'apps': applist,
                            'state': list_view.currentIndex,
                            'action_engine': targetComponentComboBox.currentIndex,
                            'action': targetActionComboBox.currentIndex,
                            'priority': priorityComboBox.currentIndex,
                        }
                        systemProcessHelper.save_task(fileNowEdit, [condition])
                        drawer.close()
                    }
                }
                Button {
                    id: cancelButton
                    text: backend.get_element_loc('cancel')
                    icon.name: FluentIcons.graph_Cancel
                    Layout.rightMargin: 20
                    icon.height: 20
                    icon.width:20
                    Layout.preferredWidth:150
                    Dialog {
                        id: messageDialog
                        x: Math.ceil((parent.width - width) / 2) - 50
                        y: Math.ceil((parent.height - height) / 2)
                        width: 270
                        title: backend.get_element_loc('pseudoconsole_question_title')
                        ColumnLayout {
                            spacing: 10
                            anchors.fill: parent
                            anchors.rightMargin:0
                            anchors.leftMargin:0
                            Label {
                                width:messageDialog.width - 20
                                Layout.preferredWidth: messageDialog.width - 20
                                text: backend.get_element_loc('close_ask')
                                wrapMode:Text.Wrap
                            }
                            RowLayout {
                                Layout.preferredWidth: parent.width
                                spacing: 10
                                Button {
                                    Layout.preferredWidth: (parent.width)/2-5
                                    text: backend.get_element_loc("yes")
                                    onClicked: {
                                        messageDialog.close()
                                        drawer.close()
                                    }
                                }
                                Button {
                                    Layout.preferredWidth: (parent.width)/2-5
                                    highlighted:true
                                    text: backend.get_element_loc("no")
                                    onClicked: messageDialog.close()
                                }
                            }
                        }
                    }
                    onClicked: {
                        if (somethingChanged) {
                            messageDialog.open()
                        } else {
                            drawer.close()
                        }
                    }
                }
            }
            ColumnLayout {
                Layout.leftMargin: 20
                Layout.rightMargin: 20
                Flickable {
                    id: contentFlickable
                    boundsBehavior: Flickable.StopAtBounds
                    Layout.preferredWidth: drawer.width - 40
                    Layout.preferredHeight: drawer.height - 100 - drawerContent.implicitHeight
                    contentHeight: contentLayout.implicitHeight
                    contentWidth: contentLayout.implicitWidth
                    clip: true
                    ColumnLayout {
                        id: contentLayout
                        RowLayout {
                            HyperlinkButton {
                                id:btnType
                                text: "<u>"+
                                    backend.get_element_loc('if_app')
                                    +"</u>"
                                FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                                Layout.preferredHeight:15
                                font: Typography.bodyLarge
                                Layout.preferredWidth:implicitWidth - 15
                                Layout.alignment: Qt.AlignVCenter
                                flat: true
                                background: Rectangle {
                                    implicitWidth: 100
                                    implicitHeight: 40
                                    color: Theme.accentColor.defaultBrushFor()
                                    opacity: 0.1
                                    visible:btnType.activeFocus ? true:btnType.hovered
                                    radius:2
                                }
                                onClicked:{
                                    hideAll()
                                    conditionVariants.visible = true
                                    currentSettingsEdit = backend.get_element_loc('conditional_util_type')
                                }
                            }
                            IconButton {
                                id:typeEditButton
                                text: backend.get_element_loc('edit')
                                display: Button.IconOnly
                                FluentUI.radius: 0
                                Layout.leftMargin: -5
                                icon.name: FluentIcons.graph_Edit
                                icon.height: 15
                                icon.width:15
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                                Layout.alignment: Qt.AlignVCenter
                                icon.color: Theme.accentColor.defaultBrushFor()
                                onClicked:{
                                    hideAll()
                                    conditionVariants.visible = true
                                    currentSettingsEdit = backend.get_element_loc('conditional_util_type')
                                }
                            }
                            Image {
                                source:appsModel.count !== 0 ? appsModel.get(0).icon :"qrc:/qt/qml/GoodbyeDPI_UI/res/image/app.png"
                                width: 30
                            }
                            HyperlinkButton {
                                id:btnAppName
                                text: "<u>" + 
                                    (
                                        appsModel.count !== 0 ? 
                                        appsModel.get(0).name : backend.get_element_loc("conditional_util_nothing")
                                    ) + (
                                        appsModel.count > 1 ? 
                                        " "+backend.get_element_loc("conditional_util_and").arg(appsModel.count-1) : ""
                                    )
                                    + "</u>"
                                FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                                Layout.preferredHeight:15
                                font: Typography.bodyLarge
                                Layout.preferredWidth:implicitWidth - 15
                                Layout.alignment: Qt.AlignVCenter
                                flat: true
                                background: Rectangle {
                                    implicitWidth: 100
                                    implicitHeight: 40
                                    color: Theme.accentColor.defaultBrushFor()
                                    opacity: 0.1
                                    visible:btnAppName.activeFocus ? true:btnAppName.hovered
                                    radius:2
                                }
                                onClicked:{
                                    hideAll()
                                    appSettings.visible = true
                                    currentSettingsEdit = backend.get_element_loc('app')
                                }
                            }
                            IconButton {
                                id:appNameEditButton
                                text: backend.get_element_loc('edit')
                                display: Button.IconOnly
                                FluentUI.radius: 0
                                Layout.leftMargin: -5
                                icon.name: FluentIcons.graph_Edit
                                icon.height: 15
                                icon.width:15
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                                Layout.alignment: Qt.AlignVCenter
                                icon.color: Theme.accentColor.defaultBrushFor()
                                onClicked:{
                                    hideAll()
                                    appSettings.visible = true
                                    currentSettingsEdit = backend.get_element_loc('app')
                                }
                            }
                            HyperlinkButton {
                                id:btnState
                                text: "<u>"+backend.get_element_loc("conditional_util_runned")+"</u>"
                                FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                                Layout.preferredHeight:15
                                font: Typography.bodyLarge
                                Layout.preferredWidth:implicitWidth - 15
                                Layout.alignment: Qt.AlignVCenter
                                flat: true
                                background: Rectangle {
                                    implicitWidth: 100
                                    implicitHeight: 40
                                    color: Theme.accentColor.defaultBrushFor()
                                    opacity: 0.1
                                    visible:btnState.activeFocus ? true:btnState.hovered
                                    radius:2
                                }
                                onClicked:{
                                    hideAll()
                                    stateSettings.visible = true
                                    currentSettingsEdit = backend.get_element_loc('conditional_util_state')
                                }
                            }
                            IconButton {
                                id:stateButton
                                text: backend.get_element_loc('edit')
                                display: Button.IconOnly
                                FluentUI.radius: 0
                                Layout.leftMargin: -5
                                icon.name: FluentIcons.graph_Edit
                                icon.height: 15
                                icon.width:15
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                                Layout.alignment: Qt.AlignVCenter
                                icon.color: Theme.accentColor.defaultBrushFor()
                                onClicked:{
                                    hideAll()
                                    stateSettings.visible = true
                                    currentSettingsEdit = backend.get_element_loc('conditional_util_state')
                                }
                            }
                            Label {
                                id:actionText
                                text: backend.get_element_loc('if_app_action')
                                font: Typography.bodyLarge
                                Layout.alignment: Qt.AlignVCenter
                            }
                            HyperlinkButton {
                                id:btnAction
                                text: "<u>"+backend.get_element_loc("action").toLowerCase()+"</u>"
                                FluentUI.primaryColor: Theme.accentColor.defaultBrushFor()
                                Layout.preferredHeight:15
                                font: Typography.bodyLarge
                                Layout.preferredWidth:implicitWidth - 15
                                Layout.alignment: Qt.AlignVCenter
                                flat: true
                                background: Rectangle {
                                    implicitWidth: 100
                                    implicitHeight: 40
                                    color: Theme.accentColor.defaultBrushFor()
                                    opacity: 0.1
                                    visible:btnAction.activeFocus ? true:btnAction.hovered
                                    radius:2
                                }
                                onClicked:{
                                    hideAll()
                                    actionSettings.visible = true
                                    currentSettingsEdit = backend.get_element_loc('action')
                                    actionSettings.forceActiveFocus()
                                }
                            }
                            IconButton {
                                id:actionButton
                                text: backend.get_element_loc('edit')
                                display: Button.IconOnly
                                FluentUI.radius: 0
                                Layout.leftMargin: -5
                                icon.name: FluentIcons.graph_Edit
                                icon.height: 15
                                icon.width:15
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: text
                                Layout.alignment: Qt.AlignVCenter
                                icon.color: Theme.accentColor.defaultBrushFor()
                                onClicked:{
                                    hideAll()
                                    actionSettings.visible = true
                                    currentSettingsEdit = backend.get_element_loc('action')
                                    actionSettings.forceActiveFocus()
                                }
                            }
                        }
                        RowLayout {
                            Layout.topMargin:50
                            Label {
                                text: backend.get_element_loc('priority')
                                font: Typography.body
                                Layout.alignment: Qt.AlignVCenter
                            }
                            ComboBox{
                                id:priorityComboBox
                                model: [
                                    "1 ("+backend.get_element_loc('highest')+")", 
                                    "0 ("+backend.get_element_loc('default')+")",
                                    "-1 ("+backend.get_element_loc('lowest')+")"
                                    ]
                                currentIndex: 1
                                Layout.preferredWidth: 300
                                Layout.alignment: Qt.AlignRight
                                Layout.margins:0
                                FluentUI.radius:0
                                onCurrentIndexChanged: {
                                    somethingChanged = true
                                }
                            }
                        }
                    }
                    ScrollBar.vertical: ScrollBar {}
                    ScrollBar.horizontal: ScrollBar {}
                    
                }
                ColumnLayout {
                    id:drawerContent
                    
                    Rectangle {
                        id:drawerContentRect
                        visible: false
                        Layout.fillWidth: true
                        Layout.preferredWidth: drawer.width
                        Layout.alignment: Qt.AlignHCenter
                        color: Theme.res.solidBackgroundFillColorBase
                        border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                        radius: 0
                        Layout.minimumHeight: 46
                        Layout.leftMargin: -20
                        RowLayout {
                            anchors.fill: parent
                            anchors{
                                leftMargin: 20
                                rightMargin: 20
                                topMargin: 0
                                bottomMargin: 0
                            }
                            Label {
                                id:currentSettingsLabel
                                text: backend.get_element_loc('edit') + ": " + currentSettingsEdit
                                font: Typography.subtitle
                            }
                            Item {
                                Layout.fillWidth: true
                                }
                            Button {
                                id:settingsButton
                                text: conditionSettings.visible? 
                                    backend.get_element_loc('hide_additional_settings') : 
                                    backend.get_element_loc('show_additional_settings')
                                icon.name: conditionSettings.visible?
                                    FluentIcons.graph_ChevronDown : FluentIcons.graph_ChevronUp
                                icon.height: 20
                                icon.width:20
                                FluentUI.radius: 0
                                Layout.alignment: Qt.AlignRight
                                onClicked: {
                                    if (conditionSettings.visible) {
                                        conditionSettings.visible = false
                                    } else {
                                        conditionSettings.visible = true
                                    }
                                }
                            }
                        }
                    }
                    ColumnLayout {
                        id:conditionSettings
                        ColumnLayout {
                            id:conditionVariants
                            visible: false
                            Layout.rightMargin: 20
                            Layout.bottomMargin: 10
                            ListView {
                                id: cond_var_list_view
                                clip: true
                                height: 80
                                currentIndex: 0
                                width: drawer.width - 40
                                Layout.preferredWidth: drawer.width - 40
                                
                                model: [
                                    condVarVariant1,
                                    condVarVariant2,
                                ]
                                highlightMoveDuration: 0
                                spacing: 6
                                boundsBehavior: ListView.StopAtBounds
                                delegate: ListTile {
                                    id: control_menu_item_c
                                    required property var model
                                    required property int index
                                    width: ListView.view.width
                                    property bool isSeparator: false
                                    property string itemText: model.modelData
                                    text: itemText
                                    font: Typography.bodyStrong

                                    highlighted: cond_var_list_view.highlightedIndex === index && !isSeparator
                                    hoverEnabled: cond_var_list_view.hoverEnabled && !isSeparator  
                                    textColor: Theme.res.textFillColorPrimary
                                    enabled: !isSeparator
                                    background: FocusItem{
                                        radius: 4
                                        implicitHeight: isSeparator ? 24 : 36
                                        implicitWidth: 100
                                        target: control_menu_item_c
                                        Rectangle{
                                            width: 3
                                            height: 18
                                            radius: 1.5
                                            anchors{
                                                verticalCenter: parent.verticalCenter
                                                left: parent.left
                                                leftMargin: 6
                                            }
                                            visible: cond_var_list_view.currentIndex === index
                                            color: Theme.accentColor.defaultBrushFor()
                                        }
                                        Rectangle{
                                            radius: 4
                                            anchors{
                                                fill: parent
                                                leftMargin: 6
                                                rightMargin: 6
                                            }
                                            color: control_menu_item_c.highlighted ? Theme.res.subtleFillColorSecondary : Theme.uncheckedInputColor(control_menu_item_c,true,true)
                                        }
                                    }
                                    onClicked: {
                                        condVarVariantIndex = index
                                        cond_var_list_view.currentIndex = index;
                                    }
                                    Component.onCompleted:{
                                        if (isSeparator) {
                                            font.bold = true
                                            font.color = "#FFFFFF"
                                        }
                                    }
                                }
                                ScrollBar.vertical: ScrollBar {}
                                onCurrentIndexChanged: {
                                    if (cond_var_list_view.currentIndex !== condVarVariantIndex) {
                                        cond_var_list_view.currentIndex = condVarVariantIndex
                                    }
                                        
                                    somethingChanged = true
                                    if (cond_var_list_view.currentIndex === 0) {
                                        btnType.text = "<u>"+backend.get_element_loc('if_app')+"</u>"
                                        actionText.text = backend.get_element_loc('if_app_action')
                                    } else if (cond_var_list_view.currentIndex === 1) {
                                        btnType.text = "<u>"+backend.get_element_loc('while_app')+"</u>"
                                        actionText.text = backend.get_element_loc('while_app_action')
                                    }
                                }
                                Component.onCompleted:{
                                }
                            }
                        }
                        ColumnLayout {
                            id:appSettings
                            visible: false
                            RowLayout {
                                id:headerLayout
                                Layout.fillWidth: true
                                Button {
                                    id:addAppButton
                                    text: backend.get_element_loc("add_app")
                                    Layout.maximumWidth:implicitWidth
                                    icon.name: FluentIcons.graph_Add
                                    icon.height: 20
                                    icon.width:20
                                    onClicked:{
                                        addAppDialog.open()
                                    }
                                }
                            }
                            Flickable {
                                id: appsFlickable
                                clip: true
                                Layout.fillWidth:true
                                boundsBehavior: Flickable.StopAtBounds
                                Layout.minimumHeight:150
                                Layout.preferredHeight: Math.min(contentHeight, drawer.height-400)
                                contentHeight: column.implicitHeight
                                Layout.rightMargin: 20
                                Layout.bottomMargin: 10
                                ColumnLayout {
                                    id:column
                                    spacing: 5
                                    width: appsFlickable.width-10
                                    ListModel {
                                        id: appsModel
                                        Component.onCompleted: {
                                        }
                                        onCountChanged: {
                                            somethingChanged = true
                                        }
                                    }
                                    Repeater {
                                        model: appsModel
                                        
                                        delegate: ColumnLayout {
                                            Layout.fillWidth: true
                                            Layout.preferredWidth: column.width
                                            Layout.alignment: Qt.AlignHCenter
                                            
                                            Loader {
                                                id: itemLoader
                                                
                                                Layout.preferredWidth: column.width
                                                sourceComponent: appComponent
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
                                    orientation: Qt.Vertical
                                    visible:true
                                    
                                }


                            }
                        }
                        ColumnLayout {
                            id:stateSettings
                            visible: false
                            Layout.rightMargin: 20
                            Layout.bottomMargin: 10

                            ListView {
                                id: list_view
                                clip: true
                                height: 80
                                width: drawer.width - 40
                                Layout.preferredWidth: drawer.width - 40
                                model: [
                                    backend.get_element_loc('conditional_util_runned').toUpperCase(),
                                    backend.get_element_loc('conditional_util_stopped').toUpperCase(),
                                ]
                                currentIndex: 0
                                highlightMoveDuration: 0
                                spacing: 6
                                boundsBehavior: ListView.StopAtBounds
                                delegate: ListTile {
                                    id: control_menu_item
                                    required property var model
                                    required property int index
                                    width: ListView.view.width
                                    property bool isSeparator: false
                                    property string itemText: model.modelData
                                    text: itemText
                                    font: Typography.bodyStrong

                                    highlighted: list_view.highlightedIndex === index && !isSeparator
                                    hoverEnabled: list_view.hoverEnabled && !isSeparator  
                                    textColor: Theme.res.textFillColorPrimary
                                    enabled: !isSeparator
                                    background: FocusItem{
                                        radius: 4
                                        implicitHeight: isSeparator ? 24 : 36
                                        implicitWidth: 100
                                        target: control_menu_item
                                        Rectangle{
                                            width: 3
                                            height: 18
                                            radius: 1.5
                                            anchors{
                                                verticalCenter: parent.verticalCenter
                                                left: parent.left
                                                leftMargin: 6
                                            }
                                            visible: list_view.currentIndex === index
                                            color: Theme.accentColor.defaultBrushFor()
                                        }
                                        Rectangle{
                                            radius: 4
                                            anchors{
                                                fill: parent
                                                leftMargin: 6
                                                rightMargin: 6
                                            }
                                            color: control_menu_item.highlighted ? Theme.res.subtleFillColorSecondary : Theme.uncheckedInputColor(control_menu_item,true,true)
                                        }
                                    }
                                    onClicked: {
                                        if (!isSeparator) {
                                            list_view.currentIndex = index;
                                        } else {
                                            list_view.currentIndex = index+1;
                                        }
                                    }
                                    Component.onCompleted:{
                                        if (isSeparator) {
                                            font.bold = true
                                            font.color = "#FFFFFF"
                                        }
                                    }
                                }
                                ScrollBar.vertical: ScrollBar {}
                                onCurrentIndexChanged: {
                                    somethingChanged = true
                                    var curI = cond_var_list_view.currentIndex
                                    if (list_view.currentIndex === 0) {
                                        btnState.text = "<u>"+backend.get_element_loc('conditional_util_runned')+"</u>"
                                    } else if (list_view.currentIndex === 1) {
                                        btnState.text = "<u>"+backend.get_element_loc('conditional_util_stopped')+"</u>"
                                    }
                                    //cond_var_list_view.currentIndex = curI
                                }
                                Component.onCompleted:{
                                }
                            }
                        }
                        ColumnLayout {
                            id:actionSettings
                            Layout.rightMargin: 20
                            Layout.bottomMargin: 10
                            visible: false
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                                Layout.alignment: Qt.AlignHCenter
                                color: Theme.res.controlFillColorDefault
                                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                                radius: 0
                                Layout.minimumHeight: 46
                                Layout.preferredHeight:rowLayout1.height+20
                                RowLayout {
                                    anchors.fill: parent
                                    anchors{
                                        leftMargin: 10
                                        rightMargin: 10
                                        topMargin: 10
                                        bottomMargin: 10
                                    }
                                    RowLayout {
                                        id: rowLayout1
                                        Label {
                                            text: backend.get_element_loc('target_component')
                                            font: Typography.body
                                            Layout.preferredWidth: 300
                                        }
                                        Item {
                                            Layout.fillWidth: true
                                        }
                                        ComboBox{
                                            id:targetComponentComboBox
                                            model: [
                                                backend.get_element_loc("notset"), 
                                                "GoodbyeDPI", 
                                                "Zapret", 
                                                "ByeDPI", 
                                                "SpoofDPI"
                                                ]
                                            Layout.preferredWidth: 300
                                            Layout.alignment: Qt.AlignRight
                                            Layout.margins:0
                                            FluentUI.radius:0
                                            onCurrentIndexChanged: {
                                                somethingChanged = true
                                            }
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                                Layout.alignment: Qt.AlignHCenter
                                color: Theme.res.controlFillColorDefault
                                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                                radius: 0
                                Layout.minimumHeight: 46
                                Layout.preferredHeight:rowLayout2.height+20
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors{
                                        leftMargin: 10
                                        rightMargin: 10
                                        topMargin: 10
                                        bottomMargin: 10
                                    }
                                    RowLayout {
                                        id: rowLayout2
                                        Label {
                                            text: backend.get_element_loc('target_action')
                                            font: Typography.body
                                            Layout.preferredWidth: 300
                                        }
                                        Item {
                                            Layout.fillWidth: true
                                        }
                                        ComboBox{
                                            id:targetActionComboBox
                                            enabled: targetComponentComboBox.currentIndex !== 0
                                            model: [backend.get_element_loc('kill'), backend.get_element_loc('run')]
                                            Layout.preferredWidth: 300
                                            Layout.alignment: Qt.AlignRight
                                            Layout.margins:0
                                            FluentUI.radius:0
                                            onCurrentIndexChanged: {
                                                somethingChanged = true
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredWidth: drawer.width
                        Layout.preferredHeight: 10
                        Layout.alignment: Qt.AlignHCenter
                        color: Theme.res.solidBackgroundFillColorBase
                        border.color: Qt.rgba(0.67, 0.67, 0.67, 0.0)
                        radius: 0
                        Layout.topMargin: -10
                        Layout.minimumHeight: 20
                        Layout.bottomMargin: -20
                        Layout.leftMargin: -20
                        Layout.rightMargin: -20
                    }
                }
            }
        }
    }
    ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        ColumnLayout {
            id:settingsLayout
            Rectangle {
                id:restSet
                Layout.preferredHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width
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
                    width:restSet.width-itemSet.implicitWidth-80

                    Label {
                        text: backend.get_element_loc("enable_conditional_run")
                        horizontalAlignment: Qt.AlignLeft
                        font: Typography.body
                    }
                    Label {
                        text: backend.get_element_loc("enable_conditional_run_tip")
                        horizontalAlignment: Qt.AlignLeft
                        font: Typography.caption
                        wrapMode:Text.Wrap
                        color: Theme.res.textFillColorSecondary
                        Layout.fillWidth:true
                        Layout.preferredWidth:restSet.width-itemSet.implicitWidth-80
                    }
                }

                Item {
                    Layout.fillHeight: true
                    width:itemSet.implicitWidth+80
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 15
                    }

                    Switch {
                        id:itemSet
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        text: checked ? backend.get_element_loc("on_") : backend.get_element_loc("off")
                        checked: backend.getBool('GLOBAL', 'conditionenabled')
                        enabled: canRun
                        onClicked: {
                            if (checked) {
                                systemProcessHelper.start_process_checker()
                                backend.toggleBool('GLOBAL', 'conditionenabled', true)
                            } else {
                                systemProcessHelper.stop_process_checker()
                                backend.toggleBool('GLOBAL', 'conditionenabled', false)
                            }
                        }
                    }
                }

            }
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.controlFillColorDefault
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 6
                Layout.minimumHeight: 68
                Layout.preferredHeight:clmn.height+20

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
                            text: backend.get_element_loc("conditional_util_check")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                        }

                        Label {
                            id:lbl2
                            Layout.fillWidth: true
                            text: backend.get_element_loc("conditional_util_check_tip")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
                            wrapMode: Text.Wrap
                        }
                    }

                    ComboBox {
                        id:cmbox
                        Layout.preferredWidth: rwlay.width < 450 ? rwlay.width-200 : 250
                        Layout.fillWidth: false
                        enabled:canEdit
                        editable: true
                        model: ListModel {
                            id: model
                            ListElement { text: "10" }
                            ListElement { text: "30" }
                            ListElement { text: "60" }
                            ListElement { text: "120" }
                            ListElement { text: "3600" }
                        }
                        property var isInit1:true
                        property var isInit2:true
                        onCurrentIndexChanged: {
                            if (editText != '' && !isInit1) {
                                backend.changeValue('GLOBAL', 'conditiontimeout', editText)
                            }
                            isInit1 = false
                        }
                        onEditTextChanged: {
                            if (!editText.match(/^\d*$/)) {
                                editText = editText.replace(/\D/g, ""); 
                            }
                            if (editText != '' && !isInit2) {
                                backend.changeValue('GLOBAL', 'conditiontimeout', editText)
                            }
                            isInit2 = false
                        }
                        onAccepted: {
                            if (find(editText) === -1)
                                model.append({text: editText})
                        }
                        Component.onCompleted: {
                            if (find(backend.getValue('GLOBAL', 'conditiontimeout')) === -1) {
                                model.append({text: backend.getValue('GLOBAL', 'conditiontimeout')})
                                currentIndex = model.count-1
                            } else {
                                currentIndex = find(backend.getValue('GLOBAL', 'conditiontimeout'))
                            }
                            editText = backend.getValue('GLOBAL', 'conditiontimeout')
                        }

                    }
                }
            }

        }
        ColumnLayout {
            id:conditionListLayout
            visible:false
            Layout.fillWidth: true
            Layout.fillHeight: true
            RowLayout {
                id: rowLayout
                Item{
                    Layout.fillWidth: true
                }
                Button {
                    text: backend.get_element_loc('add_condition')
                    Layout.maximumWidth:implicitWidth
                    icon.name: FluentIcons.graph_Add
                    icon.height: 20
                    icon.width:20
                    onClicked: {
                        drawer.open()
                    }
                }
            }
            Flickable {
                id: flickable
                clip: true
                Layout.preferredWidth:page.width-50
                Layout.preferredHeight:page.height-rowLayout.height-header.height-85
                contentHeight: ficcolumn.implicitHeight
                ColumnLayout {
                    id:ficcolumn
                    spacing: 5
                    width: flickable.width-10

                    ColumnLayout{
                        id:splashScreen
                        visible:tasksListModel.count === 0
                        Layout.preferredHeight:page.height-rowLayout.height-header.height-85
                        Layout.alignment: Qt.AlignHCenter
                        ColumnLayout{
                            Image {
                                id: findErrorImage
                                visible:true
                                width:55
                                height:55
                                Layout.alignment: Qt.AlignHCenter
                                source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/find_error.png" 
                            }
                            Label {
                                id:label
                                text:backend.get_element_loc("nothing_to_view")
                            }
                        }
                    }
                    ListModel {
                        id: tasksListModel
                        Component.onCompleted: {
                            systemProcessHelper.update_task_list()
                        }
                    }
                    Repeater {
                        model: tasksListModel
                        
                        delegate: ColumnLayout {
                            Layout.fillWidth: true
                            Layout.preferredWidth: ficcolumn.width
                            Layout.alignment: Qt.AlignHCenter
                            
                            Loader {
                                id: itemLoader
                                
                                Layout.preferredWidth: ficcolumn.width
                                sourceComponent: taskComponent
                                property var modelData: model
                                property int modelIndex: index

                                onLoaded: {
                                }
                            }

                        }
                        
                    }
                }
                ScrollBar.vertical: ScrollBar {
                    id: verticalScrollBar
                    orientation: Qt.Vertical
                    visible:true
                    
                }
            }
        }
        ColumnLayout {
            id:notificationsLayout
            visible:false
            Flickable {
                id: notificationsFlickable
                clip: true
                Layout.preferredWidth:page.width-50
                Layout.preferredHeight:page.height-rowLayout.height-header.height-85
                contentHeight: notificationsFlickableColumn.implicitHeight
                ColumnLayout {
                    id:notificationsFlickableColumn
                    spacing: 5
                    width: notificationsFlickable.width-10

                    ColumnLayout{
                        visible:notificationsModel.count === 0
                        Layout.preferredHeight:page.height-rowLayout.height-header.height-85
                        Layout.alignment: Qt.AlignHCenter
                        ColumnLayout{
                            Image {
                                visible:true
                                width:55
                                height:55
                                Layout.alignment: Qt.AlignHCenter
                                source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/find_error.png" 
                            }
                            Label {
                                text:backend.get_element_loc("nothing_to_view")
                            }
                        }
                    }
                    ListModel {
                        id: notificationsModel
                        Component.onCompleted: {
                        }
                    }
                    Repeater {
                        model: notificationsModel
                        
                        delegate: ColumnLayout {
                            Layout.fillWidth: true
                            Layout.preferredWidth: notificationsFlickableColumn.width
                            Layout.alignment: Qt.AlignHCenter
                            
                            Loader {
                                id: itemLoader
                                
                                Layout.preferredWidth: notificationsFlickableColumn.width
                                sourceComponent: taskComponent
                                property var modelData: model
                                property int modelIndex: index

                                onLoaded: {
                                }
                            }

                        }
                        
                    }
                }
                ScrollBar.vertical: ScrollBar {}
            }
        }
        ColumnLayout {
            id:aboutLayout
            visible:false
            ColumnLayout {
                Layout.topMargin:5
                Layout.bottomMargin:5
                RowLayout {
                    
                    spacing: 20
                    Layout.leftMargin: 15
                    Image {
                        source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/c_logo.png"
                        width: 100
                        height: 100
                        fillMode: Image.PreserveAspectFit
                        Layout.alignment: Qt.AlignVCenter
                    }

                    Column {
                        
                        spacing: 10
                        Layout.alignment: Qt.AlignVCenter
                        Label {
                            text: "GOODBYEDPI UI - CONDITION UTIL"
                            font: Typography.bodyLarge
                            Layout.preferredWidth: Math.min(350, page.width-250)
                        }
                    }
                }
                
                
            }
            Label {
                text:backend.get_element_loc('help')
                font:Typography.bodyStrong
            }
            Button{
                Layout.preferredHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    ColumnLayout{
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignLeft
                            text: backend.get_element_loc('goto_wiki')
                            font: Typography.body
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
                            source: FluentIcons.graph_OpenInNewWindow
                            width: 15
                            height: 15
                        }
                        onClicked: {
                            Qt.openUrlExternally("https://storik4pro.github.io/wiki/condition-util/")
                        }
                    }
                }
                
                onClicked: {
                    Qt.openUrlExternally("https://storik4pro.github.io/wiki/condition-util/")
                }
            }
            Button{
                Layout.preferredHeight: 68
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width
                Layout.alignment: Qt.AlignHCenter
                RowLayout{
                    anchors.fill: parent
                    anchors{
                        leftMargin: 20
                        rightMargin: 20
                    }
                    spacing: 10
                    ColumnLayout{
                        Layout.fillWidth: true
                        spacing: 2
                        Label{
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignLeft
                            text: backend.get_element_loc('report_a_problem')
                            font: Typography.body
                            wrapMode:Text.Wrap
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
                            Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/discussions/categories/conditional-launch")
                        }
                    }
                }
                
                onClicked: {
                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/discussions/categories/conditional-launch")
                }
            }
        }
    }
    Component {
        id: appComponent

        ColumnLayout {
            id: rest
            Layout.fillWidth: true
            Rectangle {
                Layout.preferredHeight: Math.max(60, columnLayout.implicitHeight + 20)
                Layout.fillWidth: true
                color: modelData && modelData.index % 2 === 0 ? 
                        Theme.res.subtleFillColorSecondary : Theme.res.subtleFillColorTertiary
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 0
                ColumnLayout {
                    
                    anchors.fill: parent
                    anchors{
                        leftMargin: 10
                        rightMargin: 10
                    }
                    spacing: 0
                    RowLayout {
                        id: columnLayout
                        spacing: 5
                        Image {
                            Layout.preferredHeight: 40
                            Layout.preferredWidth: 40
                            visible: modelData && modelData.icon
                            source: modelData ? modelData.icon : "qrc:/qt/qml/GoodbyeDPI_UI/res/image/app.png"
                            onStatusChanged: {
                                if (status == Image.Error) {
                                    visible = false
                                    itemIcon.visible = true
                                }
                            }
                        }
                        Icon {
                            id: itemIcon
                            visible: modelData && !modelData.icon
                            Layout.preferredHeight: 40
                            Layout.preferredWidth: 40
                            source: FluentIcons.graph_AppIconDefault
                        }
                        Label {
                            id: itemLabel
                            text: modelData ? modelData.name : ""
                            font: Typography.bodyStrong
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                            height: 20
                            Layout.maximumHeight: 20
                            Layout.preferredWidth: parent.width
                        
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        Button {
                            id: deleteButton
                            text: backend.get_element_loc('delete')
                            icon.name: FluentIcons.graph_Delete
                            FluentUI.radius: 0
                            icon.height: 20
                            icon.width:20
                            onClicked:{
                                appsModel.remove(modelData.index)
                            }
                        }
                    }
                }
            }
        }
    }
    Component {
        id: taskComponent
        ColumnLayout {
            Layout.fillWidth: true

            property var isTaskEnabled: systemProcessHelper.is_task_enabled(modelData.file)
            Rectangle {
                Layout.preferredHeight: Math.max(60, columnLayout.implicitHeight + 20)
                Layout.fillWidth: true
                color: modelData && modelData.index % 2 === 0 ? 
                        Theme.res.subtleFillColorSecondary : Theme.res.subtleFillColorTertiary
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius: 0
                ColumnLayout {
                    
                    anchors.fill: parent
                    anchors{
                        leftMargin: 10
                        rightMargin: 10
                    }
                    spacing: 0
                    RowLayout {
                        id: columnLayout
                        spacing: 5
                        Item {
                            Layout.preferredHeight: 40
                            Layout.preferredWidth: 40

                            Image {
                                id: itemImage
                                height:40
                                width:40
                                visible: modelData && modelData.icon
                                source: {
                                    var appIcon = "qrc:/qt/qml/GoodbyeDPI_UI/res/image/app.png";
                                    var exe_path = modelData?modelData.icon +  
                                        (qsTr(modelData.icon).endsWith('.exe')||
                                        backend.is_uwp_folder(modelData.icon)?'':'.exe'):""
                                    appIcon = 'image://icons/'+exe_path
                                    
                                    return appIcon;
                                    }
                                onStatusChanged: {
                                    if (status == Image.Error) {
                                        visible = false
                                        itemIcon.visible = true
                                    }
                                }
                            }
                            ColumnLayout {
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                width:20
                                height:20
                                anchors.bottomMargin: -2
                                anchors.rightMargin: -2
                                Rectangle {
                                    id: stateRect
                                    Layout.preferredHeight: 20
                                    Layout.preferredWidth: 20
                                    border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                                    color: isTaskEnabled? 
                                           "#107C10":"#A80000"
                                }
                            }
                            Icon {
                                id: stateIcon
                                visible: true
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                width:15
                                height:15
                                source: isTaskEnabled? 
                                    FluentIcons.graph_PlaySolid: 
                                    FluentIcons.graph_PauseBold
                            }
                        }
                        Icon {
                            id: itemIcon
                            visible: modelData && !modelData.icon
                            Layout.preferredHeight: 40
                            Layout.preferredWidth: 40
                            source: FluentIcons.graph_AppIconDefault
                            color: Theme.accentColor.defaultBrushFor()
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignHCenter
                            Label {
                                id: itemLabel
                                text: backend.get_element_loc('app') + ": " + modelData?modelData.apps:""
                                font: Typography.bodyStrong
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                                height: 20
                                Layout.maximumHeight: 20
                                Layout.preferredWidth: parent.width
                                Component.onCompleted: {
                                }

                            
                            }
                            Flickable {
                                clip: true
                                boundsBehavior: Flickable.StopAtBounds
                                Layout.fillWidth: true
                                Layout.preferredHeight: 20
                                Layout.rightMargin: 10
                                RowLayout {
                                    Label {
                                        text: backend.get_element_loc('priority') + ": " + locPriority[modelData?modelData.priority:0]
                                        font: Typography.body
                                    }
                                    Label {
                                        text: "|"
                                        font: Typography.bodyStrong
                                    }
                                    Label {
                                        text: backend.get_element_loc('action') + ": " +
                                            locAction[modelData?modelData.action:0] + " " + locActionEngine[modelData?modelData.action_engine-1:0]
                                        font: Typography.body
                                    }
                                    Label {
                                        text: "|"
                                        font: Typography.bodyStrong
                                    }
                                    Label{
                                        text: locType[modelData?modelData.type:0]
                                        font: Typography.body
                                    }
                                }
                            }
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        RowLayout {
                            id:buttonsLayout
                            Button {
                                id: playButton
                                text: isTaskEnabled?
                                    backend.get_element_loc('pause'):backend.get_element_loc('play')
                                display: Button.IconOnly
                                enabled:canEdit
                                icon.name: isTaskEnabled?
                                    FluentIcons.graph_Pause:FluentIcons.graph_Play
                                FluentUI.radius: 0
                                icon.height: 20
                                icon.width:20
                                ToolTip.visible: hovered
                                ToolTip.text: text
                                ToolTip.delay: 500
                                onClicked:{
                                    if (systemProcessHelper.is_task_enabled(modelData.file)){
                                        systemProcessHelper.set_task_enabled(modelData.file, false)
                                    } else {
                                        systemProcessHelper.set_task_enabled(modelData.file, true)
                                    }
                                    isTaskEnabled = systemProcessHelper.is_task_enabled(modelData.file)
                                    setCanRun()
                                }
                            }
                            Button {
                                id: editButton
                                text: backend.get_element_loc('edit')
                                display: Button.IconOnly
                                icon.name: FluentIcons.graph_Edit
                                FluentUI.radius: 0
                                icon.height: 20
                                icon.width:20
                                ToolTip.visible: hovered
                                ToolTip.text: text
                                ToolTip.delay: 500
                                onClicked:{
                                    fileNowEdit = modelData.file
                                    drawer.open()
                                    
                                }
                            }
                            Button {
                                id: deleteButton
                                text: backend.get_element_loc('delete')
                                display: Button.IconOnly
                                enabled:canEdit
                                icon.name: FluentIcons.graph_Delete
                                FluentUI.radius: 0
                                icon.height: 20
                                icon.width:20
                                ToolTip.visible: hovered
                                ToolTip.text: text
                                ToolTip.delay: 500
                                onClicked:{
                                    systemProcessHelper.delete_task(modelData.file)   
                                    setCanRun()                                 
                                }
                            }
                        }
                        
                    }
                }
            }
        }
    }

    function setCanRun(){
        canRun = systemProcessHelper.is_start_process_checker_availible()
    }

    Connections {
        target: systemProcessHelper
        function onTasksLoaded(taskslist){
            tasksListModel.clear()
            for (var i = 0; i < taskslist.length; i++) {
                var task = taskslist[i]
                if (task) {
                    var apps_str = task.apps[0][0] + " " + (task.apps.length > 1 ? backend.get_element_loc("conditional_util_and").arg(task.apps[0].length-1) : "")
                    tasksListModel.append({
                        "file": task.file,
                        "action": task.action,
                        "action_engine": task.action_engine,
                        "apps": apps_str,
                        "icon": task.apps[0][1],
                        "priority": task.priority,
                        "state": task.state,
                        "type": task.type
                    })
                }
            }
            canRun = systemProcessHelper.is_start_process_checker_availible()

        }
        function onProcessCheckedStarted(){
            canEdit = false
        }
        function onProcessCheckedStopped(){
            itemSet.checked = false
            canEdit = true
            backend.toggleBool('GLOBAL', 'conditionenabled', false)
            canRun = systemProcessHelper.is_start_process_checker_availible()
        }
    }
}