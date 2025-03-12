import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import QtQuick.Dialogs 
import GoodbyeDPI_UI
import QtQuick.Templates as T

ScrollablePage {
    title: backend.get_element_loc('setup_udp')
    id:page
    header:Item{}
    property bool isAppChoosed: false
    property bool isParamIncorrect: false
    property int currentStep: 0
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
                            Layout.preferredWidth:askColumn.width-20
                        }
                        Label {
                            text: backend.get_element_loc("add_classic_app_tip")
                            font: Typography.body
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:askColumn.width-20
                        }
                        RowLayout {
                            Layout.preferredWidth:askColumn.width-20
                            TextField {
                                id: exeNameInput
                                placeholderText: backend.get_element_loc("add_classic_app_placeholder")
                                Layout.preferredWidth:askColumn.width-addEXEButton.implicitWidth-5
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
                            Layout.preferredWidth:askColumn.width-20
                        }
                        Label {
                            text: backend.get_element_loc("add_uwp_app_tip")
                            font: Typography.body
                            wrapMode:Text.Wrap
                            Layout.preferredWidth:askColumn.width-20
                        }
                        RowLayout {
                            Layout.preferredWidth:askColumn.width-20
                            TextField {
                                id: uwpPathInput
                                placeholderText: backend.get_element_loc("add_uwp_app_placeholder")
                                Layout.preferredWidth:askColumn.width-addFolderButton.implicitWidth-5
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
                            Layout.preferredWidth:askColumn.width-20
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
                        if (app.exe_name.toLowerCase() === previewLabel.text.replace(/\//g, "\\").toLowerCase()) {
                            proxyHelper.add_app(app.path, app.exe_name)
                            proxyHelper.get_apps()
                            addAppDialog.close()
                            return;
                        }
                    }
                    proxyHelper.add_app(appName, appName)
                    proxyHelper.get_apps()

                    addAppDialog.close()
                }
            }
            Button {
                id:cancelButton
                text: backend.get_element_loc("cancel")
                visible:true
                onClicked: {
                    addAppDialog.close()
                }
            }
            
        }
    }
    ColumnLayout {
        Layout.fillWidth: true
        Layout.preferredWidth: Math.min(1000, parent.width * 0.9) 
        Layout.minimumWidth: 300 
        Layout.maximumWidth: 1000
        Layout.alignment: Qt.AlignHCenter
        Rectangle {
            id:rest1
            visible: currentStep !== 2
            Layout.preferredHeight: Math.max(80, infoColumnLayout.implicitHeight + 20)
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.alignment: Qt.AlignHCenter
            color: Theme.res.controlFillColorDefault
            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
            radius: 6
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
                            text:backend.get_element_loc('udp_tip')
                            font: Typography.body
                            wrapMode:Text.Wrap
                        }
                        HyperlinkButton {
                            id:btn
                            text: backend.get_element_loc("help")
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
                                Qt.openUrlExternally("https://storik4pro.github.io/wiki/proxy-install-util/")
                            }
                        }
                    }

                }
                
            }
            
        }
        ColumnLayout {
            id:firstStep
            visible: currentStep === 0
            Label {
                text: backend.get_element_loc("apps_list")
                font: Typography.bodyStrong
                Layout.topMargin: 5
            }
            ColumnLayout {
                id:selectAppLayout
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                
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
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignRight
                    }

                    TextBox{
                        id: search
                        placeholderText: backend.get_element_loc("search_tip")
                        Layout.preferredWidth:Math.max(150, selectAppLayout.width - addAppButton.width - 10) 
                        Layout.maximumWidth:400
                        Layout.rightMargin: 10
                        leading: IconButton{
                            implicitWidth: 30
                            implicitHeight: 20
                            icon.name: FluentIcons.graph_Search
                            icon.width: 14
                            icon.height: 14
                            padding: 0
                        }
                        onTextChanged: {
                            filterAppsModel()
                        }
                    }
                }
                
                Flickable {
                    id: flickable
                    clip: true
                    Layout.preferredWidth: parent.width
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.minimumHeight:150
                    Layout.preferredHeight: (page.height-headerLayout.height-
                                            rest1.height-footerColumn.implicitHeight-85)
                    contentHeight: column.implicitHeight
                    ColumnLayout {
                        id:column
                        spacing: 5
                        width: flickable.width-10

                        ColumnLayout{
                            id:splashScreen
                            visible:true
                            Layout.preferredHeight: 290
                            Layout.alignment: Qt.AlignHCenter
                            ColumnLayout{
                                AnimatedImage { 
                                    id: animation
                                    Layout.alignment: Qt.AlignHCenter
                                    source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/find.gif" 
                                    speed: 2
                                }
                                Image {
                                    id: findErrorImage
                                    visible:false
                                    width:55
                                    height:55
                                    Layout.alignment: Qt.AlignHCenter
                                    source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/find_error.png" 
                                }
                                Label {
                                    id:label
                                    text:backend.get_element_loc("update_in_process")
                                }
                            }
                        }

                        ListModel {
                            id: appsModel
                            Component.onCompleted: {
                                splashScreen.visible = true
                                proxyHelper.get_apps()
                            }
                        }
                        ListModel {
                            id: filteredAppsModel
                        }
                        Repeater {
                            model: filteredAppsModel
                            
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
                        id: verticalScrollBar
                        orientation: Qt.Vertical
                        visible:true
                        
                    }


                }
            }
        }
        ColumnLayout {
            id:secondStep
            visible:currentStep === 1
            Rectangle {
                Layout.minimumHeight: 68
                Layout.preferredHeight:clmn.height+20
                Layout.fillWidth: true
                Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                Layout.minimumWidth: 300
                Layout.maximumWidth: 1000
                Layout.alignment: Qt.AlignHCenter
                color: Theme.res.controlFillColorDefault
                border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                radius:6
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
                            text: backend.get_element_loc("proxifyre_mode")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.body
                            wrapMode: Text.Wrap
                            Layout.preferredWidth: rwlay.width - element.width - 40
                        }

                        Label {
                            id:lbl2
                            text: backend.get_element_loc("proxifyre_mode_tip")
                            horizontalAlignment: Text.AlignLeft
                            font: Typography.caption
                            color: "#c0c0c0"
                            wrapMode: Text.Wrap
                            Layout.preferredWidth: rwlay.width - element.width - 40
                        }
                    }
                }

                Item {
                    
                    Layout.fillHeight: true
                    anchors {
                        verticalCenter: parent.verticalCenter
                        right: parent.right
                        rightMargin: 20
                    }

                    ComboBox {
                        id:element
                        anchors {
                            verticalCenter: parent.verticalCenter
                            right: parent.right
                            rightMargin: 0
                        }
                        width:page.width < 700 ? page.width - 350 : 350
                        model: [
                            backend.get_element_loc("udp_n_tcp") + " (" + backend.get_element_loc("recommended") + ")",
                            backend.get_element_loc("udp"),
                            backend.get_element_loc("tcp"),
                        ]
                        currentIndex: proxyHelper.get_current_mode()
                        onActivated: {
                            proxyHelper.set_mode(currentIndex)
                        }
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
                        text:proxyHelper.get_ip("ip")
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
                                proxyHelper.set_ip("ip", text)
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
                        text:proxyHelper.get_ip("port")
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
                                proxyHelper.set_ip("port", text)
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
            visible:currentStep === 2
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
            Layout.fillWidth: true
            Layout.preferredWidth: Math.min(1000, page.width * 0.9)
            Layout.minimumWidth: 300
            Layout.maximumWidth: 1000
            Layout.leftMargin:25
            Layout.rightMargin:25
            Layout.alignment: Qt.AlignHCenter
            Rectangle {
                id:restWarn
                visible: !isAppChoosed || isParamIncorrect
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
                                text:!isAppChoosed?
                                        backend.get_element_loc('apply_udp_proxy_warning') : 
                                        backend.get_element_loc('apply_udp_proxy_invalid_param')
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
                    enabled:(isAppChoosed&&currentStep == 0) || (!isParamIncorrect && currentStep == 1)
                    Layout.alignment:Qt.AlignRight
                    Layout.minimumWidth:page.width > 650 ? 300 : (page.width - 50) / 2
                    Layout.bottomMargin:30
                    text:backend.get_element_loc("next_button")
                    onClicked: {
                        if (currentStep === 1) {
                            backend.changeValue("PROXY", "proxy_now_used", "proxifyre")
                            backend.changeValue("PROXY", "proxy_addr", ip_addr.text)
                            backend.changeValue("PROXY", "proxy_port", port.text)
                            proxyHelper.proxyTypeChange()
                            if (process.is_process_alive() && (process.is_proxifyre_used()||process.is_proxy_running())) {
                                process.stop_process()
                                Qt.callLater(process.start_process)
                            }
                        }
                        currentStep ++;
                    }
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
                        CheckBox {
                            text: ""
                            checked: modelData ? modelData.checked : false
                            onClicked: {
                                if (checked) {
                                    proxyHelper.add_app(modelData.path, modelData.exe_name)
                                } else {
                                    proxyHelper.remove_app(modelData.path, modelData.exe_name)
                                }
                                
                                proxyHelper.get_apps()
                            }
                        }
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
                    }
                }
            }
        }
    }
    function loadApps(data) {
        appsModel.clear()
        isAppChoosed = false

        for (var i = 0; i < data.length; ++i) {
            var entry = data[i]
            if (!entry.exe_name) {
                continue;
            }
            if (entry.checked){
                console.log(entry.display_name)
            }
            appsModel.append({
                'name': entry.display_name,
                'path': entry.exe,
                'exe_name': entry.exe_name,
                'icon': entry.exe ? "image://icons/" + entry.exe : FluentIcons.graph_AppIconDefault,
                'checked': entry.checked
            })
            if (entry.checked) {
                isAppChoosed = true
            }
                
        }
        filterAppsModel()
    }

    function filterAppsModel() {
        filteredAppsModel.clear()
        var searchText = search.text.toLowerCase()
        var filteredApps = []

        for (var i = 0; i < appsModel.count; ++i) {
            var app = appsModel.get(i)
            if (app.name.toLowerCase().indexOf(searchText) !== -1) {
                filteredApps.push(app)
            }
        }
        
        filteredApps.sort(function(a, b) {
            return b.checked - a.checked
        })

        for (var j = 0; j < filteredApps.length; ++j) {
            filteredAppsModel.append(filteredApps[j])
        }
        if (filteredAppsModel.count !== 0) {
            splashScreen.visible = false
            label.text = backend.get_element_loc("update_in_process")
            animation.visible = true
            findErrorImage.visible = false
        } else {
            splashScreen.visible = true
            animation.visible = false
            findErrorImage.visible = true
            label.text = backend.get_element_loc("nothing_to_view")
        }
    }

    Connections {
        target:proxyHelper
        function onAppsLoaded(appsList){
            loadApps(appsList)
            splashScreen.visible = false
        }
    }
}