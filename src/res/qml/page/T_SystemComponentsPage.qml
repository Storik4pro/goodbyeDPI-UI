import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI
import QtQuick.Dialogs

Page {
    id: page
    header: Item {}
    title: backend.get_element_loc('components')
    padding: 0
    topPadding: 24

    InfoBarManager {
        id: info_manager_bottomright
        target: page
        edge: Qt.BottomEdge | Qt.RightEdge
    }

    Dialog{
        id: proxifyreInstallDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("install_proxifyre")
        Flickable {
            id: addAppFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: contentColumn.implicitHeight
            ColumnLayout {
                anchors.fill: parent
                anchors.rightMargin:20
                ColumnLayout {
                    id:contentColumn
                    spacing: 5
                    Layout.preferredWidth:400
                    Layout.leftMargin:10
                    Layout.rightMargin:10
                    ColumnLayout {
                        id: licenseLayout
                        visible:true
                        Label {
                            text:qsTr(backend.get_element_loc("install_vs_tip"))
                            wrapMode:Text.Wrap
                            Layout.maximumWidth:contentColumn.width - 10
                        }
                        HyperlinkButton {
                            id:vsBtn
                            text: backend.get_element_loc("about_license") + ": VS Redistributable"
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
                                visible:vsBtn.hovered
                                radius:2
                            }
                            onClicked:{
                                Qt.openUrlExternally("https://visualstudio.microsoft.com/license-terms/vs2022-cruntime/")
                            }
                        }
                        Rectangle {
                            id:restInfo
                            Layout.preferredHeight: Math.max(80, infoColumnLayoutLic.implicitHeight + 20)
                            Layout.fillWidth: true
                            Layout.alignment: Qt.AlignHCenter
                            color: Theme.res.controlFillColorDefault
                            border.color: Qt.rgba(0.67, 0.67, 0.67, 0.2)
                            radius: 6
                            Layout.preferredWidth:proxifyreInstallDialog.fillWidth
                            Layout.rightMargin:-20
                            ColumnLayout{
                                id:infoColumnLayoutLic
                                anchors.verticalCenter: parent.verticalCenter  
                                RowLayout{
                                    spacing:10
                                    height:20
                                    Layout.leftMargin:20
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
                                            Layout.preferredWidth:restInfo.width - 100
                                            text:backend.get_element_loc('ELUA_tip')
                                            font: Typography.body
                                            wrapMode:Text.Wrap
                                        }
                                    }

                                }
                                
                            }
                            
                        }
                        HyperlinkButton{
                            id:infoButton
                            text:backend.get_element_loc('about_license')
                            onClicked:{
                                backend.edit_blacklist("", "WPF_ELUA")
                            }
                        }
                        CheckBox {
                            id:acceptLicense
                            text: backend.get_element_loc("accept_license")
                            checked: false
                            onCheckedChanged: {
                                addButton.enabled = checked
                            }
                        }
                    }
                    ColumnLayout {
                        id:loadingColumnLayout
                        visible:false
                        RowLayout {
                            ProgressRing {
                                id: progressBar
                                indeterminate: true
                                Layout.preferredWidth:30
                                Layout.preferredHeight:30
                                strokeWidth:4
                                visible: true
                            }
                            Label {
                                text:backend.get_element_loc("update_in_process")
                                font:Typography.bodyStrong
                            }
                        }
                        Label {
                            text:backend.get_element_loc("after_update_title")
                            Layout.leftMargin:35
                        }
                        RowLayout {
                            CopyableText {
                                id:sttext
                                text:backend.get_element_loc("state_now")
                                Layout.leftMargin:35
                            }
                            ColumnLayout {
                                CopyableText {
                                    id:state_text
                                    text:''
                                    wrapMode:Text.Wrap
                                    Layout.preferredWidth: contentColumn.width - sttext.width
                                }
                            }
                        }
                    }
                    ColumnLayout {
                        id: base_layout_after_error
                        visible: false
                        Layout.fillHeight:true
                        RowLayout{
                            Icon {
                                Layout.alignment: Qt.AlignTop | Qt.AlignLeft
                                Layout.topMargin: 2
                                source: FluentIcons.graph_StatusErrorFull
                                color: Theme.res.systemFillColorCritical
                                Layout.preferredWidth: 30
                                Layout.preferredHeight: 30
                            }
                            ColumnLayout {
                                Label {
                                    text: qsTr(backend.get_element_loc('install_error'))
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                    Layout.rightMargin:20
                                }
                                CopyableText {
                                    id:errorText
                                    text:"ERR_UNKNOWN"
                                }
                            }
                        }
                        
                    }
                    ColumnLayout {
                        id: base_layout_complete
                        visible: false
                        Layout.fillHeight:true
                        RowLayout{
                            Icon {
                                Layout.alignment: Qt.AlignTop | Qt.AlignLeft
                                Layout.topMargin: 2
                                source: FluentIcons.graph_CompletedSolid
                                color: Theme.res.systemFillColorSuccess
                                Layout.preferredWidth: 30
                                Layout.preferredHeight: 30
                            }
                            ColumnLayout {
                                Label {
                                    text: qsTr(backend.get_element_loc('install_complete_exit'))
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                    Layout.rightMargin:20
                                }
                            }
                        }
                    }
                }
            }
            ScrollBar.vertical: ScrollBar {}
        }
        
        footer: DialogButtonBox{
            Button {
                id:addButton
                text: "OK"
                visible:true
                highlighted:true
                enabled:false
                width: (proxifyreInstallDialog.width-40) / 2
                onClicked: {
                    if (licenseLayout.visible) {
                        if (!acceptLicense.checked) {
                            return
                        }
                        licenseLayout.visible = false
                        loadingColumnLayout.visible = true
                        cancelButton.visible = false
                        enabled = false
                        proxyHelper.download_proxifyre()
                    }else if (base_layout_complete.visible) {
                        pageLoader.sourceComponent = null;
                        pageLoader.sourceComponent = pageComponent;
                        proxifyreInstallDialog.close()
                        cancelButton.visible = true
                    } else {
                        proxifyreInstallDialog.close()
                        cancelButton.visible = true
                    }
                }
            }  
            Button {
                id:cancelButton
                text: backend.get_element_loc("cancel")
                width: (proxifyreInstallDialog.width-40) / 2
                onClicked: {
                    proxifyreInstallDialog.close()
                }
            }  
        }
        
    }

    Loader {
        id: pageLoader
        anchors.fill: parent
        sourceComponent: pageComponent

        Component {
            id: pageComponent

            ScrollablePage {
                topPadding: 0
                leftPadding: 20
                rightPadding: 20

                property var buttonArray: []

                ColumnLayout {
                    id: mainLayout
                    anchors.margins: 20
                    spacing: 15
                    Layout.fillWidth: true
                    Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                    Layout.minimumWidth: 300
                    Layout.maximumWidth: 1000
                    Layout.alignment: Qt.AlignHCenter

                    Rectangle {
                        id:rest1
                        Layout.preferredHeight: Math.max(60, infoColumnLayout.implicitHeight + 20)
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignHCenter
                        color: Theme.res.systemFillColorCautionBackground
                        radius: 6
                        border.color: Theme.res.cardStrokeColorDefault

                        visible: !backend.getBool('GLOBAL', 'check_complete')
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
                                        text:backend.get_element_loc('component_not_checked_e')
                                        font: Typography.body
                                        wrapMode:Text.Wrap
                                    }
                                }

                            }
                        }
                    }
                    InfoBar {
                        id:errorLabel
                        severity: InfoBarType.Error
                        visible:false
                        title: backend.get_element_loc("component_not_installed_e")
                        message: ""
                    }

                    ButtonGroup {
                        id: buttonGroup
                        buttons: []
                    }

                    Component {
                        id: componentRow
                        RowLayout {
                            property string componentId
                            property string buttonId: componentId+"Button"
                            property string removeButtonId: componentId+"RemoveButton"
                            property string componentName
                            property bool componentChecked
                            property string component
                            property bool removable

                            Layout.fillWidth: true
                            spacing: 10

                            RadioButton {
                                id: componentId
                                checked: backend.getValue('GLOBAL', 'engine').toLowerCase() === component
                                text: qsTr("")
                                enabled: backend.getBool('COMPONENTS', component)
                                ToolTip.visible: hovered
                                ToolTip.delay: 500
                                ToolTip.text: backend.get_element_loc("set_as_engine_by_default")
                                Layout.leftMargin: 15
                                onClicked: {
                                    if (component === 'goodbyedpi'){
                                        change_engine('goodbyeDPI')
                                    } else {
                                        change_engine(component)
                                    }
                                }
                                Component.onCompleted: {
                                    buttonGroup.addButton(componentId);
                                }
                            }
                            ColumnLayout {
                                CopyableText {
                                    text: componentName
                                    Layout.fillWidth: true
                                }
                                CopyableText {
                                    text: backend.get_element_loc("version") + ": " + backend.getValue("COMPONENTS", component+"_version")
                                    Layout.fillWidth: true
                                    wrapMode:Text.Wrap
                                    visible: backend.getBool('COMPONENTS', component)
                                }
                                CopyableText {
                                    text: backend.get_element_loc("server_version") + ": " + backend.check_component_version(component)
                                    wrapMode:Text.Wrap
                                    Layout.fillWidth: true
                                    visible: backend.getBool('COMPONENTS', component)
                                }
                                Rectangle {
                                    id:rest2
                                    Layout.preferredHeight: Math.max(30, infoColumnLayout.implicitHeight + 0)
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignHCenter
                                    color: Qt.rgba(0, 0, 0, 0.0)
                                    radius: 6
                                    border.color: Qt.rgba(0, 0, 0, 0.0)
                                    visible: (backend.check_component_version(component) !== '0.2.3rc3' && (backend.check_component_version(component) !== 
                                              backend.getValue("COMPONENTS", component+"_version")) && 
                                              backend.getBool('COMPONENTS', component))
                                    ColumnLayout{
                                        id:infoColumnLayout
                                        anchors.verticalCenter: parent.verticalCenter  
                                        RowLayout{    
                                            spacing:10
                                            height:20
                                            Layout.leftMargin:0
                                            
                                            Icon{
                                                id: icon_info

                                                Layout.preferredHeight:20
                                                source:FluentIcons.graph_InfoSolid
                                                color:Theme.accentColor.defaultBrushFor()
                                            }
                                            ColumnLayout{
                                                CopyableText{
                                                    Layout.preferredWidth:rest2.width - 50
                                                    text:backend.get_element_loc('update_available_t')
                                                    font: Typography.body
                                                    wrapMode:Text.Wrap
                                                }
                                            }

                                        }
                                    }
                                }
                            }
                            ColumnLayout{
                                Layout.fillWidth:true
                                ProgressButton {
                                    id:buttonId
                                    text: backend.getBool('COMPONENTS', component) ? backend.get_element_loc("component_update") : backend.get_element_loc("update_available_btn_t")
                                    Layout.rightMargin: 25
                                    highlighted: false
                                    indeterminate:true
                                    value:0.0
                                    onClicked: {
                                        if (!ready){
                                            download_component(component, buttonId);
                                            
                                        }
                                    }
                                    Component.onCompleted: {
                                        buttonArray.push(buttonId);
                                    }
                                }
                                RowLayout{
                                    Layout.fillWidth:true
                                    Layout.alignment:Qt.AlignRight
                                    visible: backend.getBool('COMPONENTS', component)
                                    Button {
                                        id:settingsButtonId
                                        text: backend.get_element_loc("open_settings")
                                        icon.name: FluentIcons.graph_Settings
                                        width: 20
                                        icon.width: 18
                                        icon.height: 18
                                        display: Button.IconOnly
                                        ToolTip.visible: hovered
                                        ToolTip.delay: 500
                                        ToolTip.text: text
                                        onClicked: {
                                            page_router.go("/"+component)
                                        }
                                    }
                                    Button {
                                        text: backend.get_element_loc("open_component_folder")
                                        icon.name: FluentIcons.graph_FolderOpen
                                        width: 20
                                        icon.width: 18
                                        icon.height: 18
                                        display: Button.IconOnly
                                        ToolTip.visible: hovered
                                        ToolTip.delay: 500
                                        ToolTip.text: text
                                        onClicked: {
                                            backend.open_component_folder(component)
                                        }
                                    }

                                    Button {
                                        id:removeButtonId
                                        text: backend.get_element_loc("remove_component")
                                        enabled:removable
                                        icon.name: FluentIcons.graph_Delete
                                        width: 20
                                        icon.width: 18
                                        icon.height: 18
                                        display: Button.IconOnly
                                        ToolTip.visible: hovered
                                        ToolTip.delay: 500
                                        ToolTip.text: text
                                        Layout.rightMargin: 25
                                        onClicked: {
                                            remove_component(component, removeButtonId)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Expander {
                        id: exp
                        expanded: !goodCheck.is_process_alive()
                        enabled:!goodCheck.is_process_alive()
                        Layout.fillWidth: true
                        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                        Layout.minimumWidth: 300
                        Layout.maximumWidth: 1000
                        Layout.alignment: Qt.AlignHCenter
                        _height:68

                        header: Label {
                            text: backend.get_element_loc("component_settings")
                            horizontalAlignment: Qt.AlignVCenter
                            font: Typography.body
                        }
                        subHeader: Label {
                            id:shead
                            text: backend.get_element_loc("component_settings_tip")
                            horizontalAlignment: Qt.AlignVCenter
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
                            width: exp.width - 30 - 20 - 50
                            wrapMode: Text.Wrap
                        }

                        content: ColumnLayout {
                            id: cnt
                            spacing: 5
                            Layout.fillWidth: true

                            ListModel {
                                id: componentModel
                                ListElement {
                                    componentId: "goodbyedpi"
                                    component: "goodbyedpi"
                                    componentName: "GoodbyeDPI"
                                    componentChecked: true
                                    removable: false
                                }
                                ListElement {
                                    componentId: "zapret"
                                    component: "zapret"
                                    componentName: "Zapret"
                                    componentChecked: false
                                    removable: true
                                }
                                ListElement {
                                    componentId: "byedpi"
                                    component: "byedpi"
                                    componentName: "ByeDPI"
                                    removable: true
                                    componentChecked: false
                                }
                                ListElement {
                                    componentId: "spoofdpi"
                                    component: "spoofdpi"
                                    componentName: "SpoofDPI"
                                    removable: true
                                    componentChecked: false
                                }
                            }

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
                                        Layout.fillWidth: true
                                        sourceComponent: componentRow
                                        onLoaded: {
                                            item.componentId = model.componentId
                                            item.componentName = model.componentName
                                            item.componentChecked = model.componentChecked
                                            item.component = model.component
                                            item.removable = model.removable
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.leftMargin: -15
                                        Layout.topMargin: 5
                                        Layout.bottomMargin: 5
                                        visible: componentId === 'spoofdpi' ? false : true
                                        height: 3
                                        color: Qt.rgba(0.0, 0.0, 0.0, 0.3)
                                        opacity: componentId === 'spoofdpi' ? 0.0 : 0.3
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
                    }                    
                    Expander {
                        expanded: false
                        Layout.fillWidth: true
                        Layout.preferredWidth: Math.min(1000, parent.width * 0.9)
                        Layout.minimumWidth: 300
                        Layout.maximumWidth: 1000
                        Layout.alignment: Qt.AlignHCenter
                        _height:68

                        header: Label {
                            text: backend.get_element_loc("other_component_settings")
                            horizontalAlignment: Qt.AlignVCenter
                            font: Typography.body
                        }
                        subHeader: Label {
                            id:shead
                            text: backend.get_element_loc("other_component_settings_tip")
                            horizontalAlignment: Qt.AlignVCenter
                            font: Typography.caption
                            color: Theme.res.textFillColorSecondary
                            width: exp.width - 30 - 20 - 50
                            wrapMode: Text.Wrap
                        }

                        content: ColumnLayout {
                            id: cnt
                            spacing: 5
                            Rectangle {
                                width: parent.width
                                height: 10
                                Layout.bottomMargin: 5
                                opacity: 0.0
                            }
                            RowLayout {
                                Layout.leftMargin: 25
                                ColumnLayout {
                                    Layout.maximumWidth:cnt.width - buttonLayout.implicitWidth - 25
                                    CopyableText {
                                        text: "ProxiFyre"
                                        Layout.fillWidth: true
                                    }
                                    CopyableText {
                                        text: backend.get_element_loc("version") + ": " + proxyHelper.get_version("basic")
                                        Layout.fillWidth: true
                                        wrapMode:Text.Wrap
                                        visible: proxyHelper.check_install()
                                    }
                                }
                                ColumnLayout{
                                    id:buttonLayout
                                    Layout.fillWidth:true
                                    ProgressButton {
                                        id:buttonId
                                        text: proxyHelper.check_install() ? backend.get_element_loc("component_reinstall") : backend.get_element_loc("update_available_btn_t")
                                        Layout.rightMargin: 25
                                        Layout.alignment:Qt.AlignRight
                                        highlighted: false
                                        indeterminate:true
                                        value:0.0
                                        onClicked: {
                                            licenseLayout.visible = true
                                            
                                            loadingColumnLayout.visible = false
                                            base_layout_after_error.visible = false
                                            base_layout_complete.visible = false
                                            proxifyreInstallDialog.open()
                                            
                                        }
                                    }
                                    RowLayout{
                                        Layout.fillWidth:true
                                        Layout.alignment:Qt.AlignRight
                                        visible: proxyHelper.check_install()
                                        Button {
                                            id:linkButtonId
                                            text: backend.get_element_loc("goto_github")
                                            icon.name: FluentIcons.graph_Globe
                                            width: 20
                                            icon.width: 18
                                            icon.height: 18
                                            display: Button.IconOnly
                                            ToolTip.visible: hovered
                                            ToolTip.delay: 500
                                            ToolTip.text: text
                                            onClicked: {
                                                Qt.openUrlExternally("https://github.com/wiresock/proxifyre")
                                            }
                                        }
                                        Button {
                                            id:settingsButtonId
                                            text: backend.get_element_loc("open_settings")
                                            icon.name: FluentIcons.graph_Settings
                                            width: 20
                                            icon.width: 18
                                            icon.height: 18
                                            display: Button.IconOnly
                                            ToolTip.visible: hovered
                                            ToolTip.delay: 500
                                            ToolTip.text: text
                                            onClicked: {
                                                page_router.go("/proxy")
                                            }
                                        }
                                        Button {
                                            text: backend.get_element_loc("open_component_folder")
                                            icon.name: FluentIcons.graph_FolderOpen
                                            width: 20
                                            icon.width: 18
                                            icon.height: 18
                                            display: Button.IconOnly
                                            ToolTip.visible: hovered
                                            ToolTip.delay: 500
                                            ToolTip.text: text
                                            onClicked: {
                                                backend.open_component_folder("proxifyre")
                                            }
                                        }

                                        Button {
                                            id:removeButtonId
                                            text: backend.get_element_loc("remove_component")
                                            icon.name: FluentIcons.graph_Delete
                                            width: 20
                                            icon.width: 18
                                            icon.height: 18
                                            display: Button.IconOnly
                                            ToolTip.visible: hovered
                                            ToolTip.delay: 500
                                            ToolTip.text: text
                                            Layout.rightMargin: 25
                                            onClicked: {
                                                if (process.is_process_alive() && process.is_proxifyre_used()) {
                                                    process.stop_process()
                                                }
                                                proxyHelper.uninstall_proxifyre()
                                                pageLoader.sourceComponent = null;
                                                pageLoader.sourceComponent = pageComponent;
                                            }
                                        }
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
                    }
                }
                function change_engine(componentName) {
                    process.change_engine(componentName)
                    if (process.is_process_alive()) {
                        process.stop_process()
                        Qt.callLater(process.start_process)
                    }
                }

                function remove_component(componentName, button) {
                    for (var i = 0; i < buttonArray.length; i++) {
                        if (buttonArray[i].enabled !== true){
                            return;
                        }
                    }
                    button.enabled = false;
                    errorLabel.message = "";
                    errorLabel.title = backend.get_element_loc("component_remove_e");
                    process.stop_service()
                    var result = backend.remove_component(componentName);
                    if (result === 'True') {
                        pageLoader.sourceComponent = null;
                        pageLoader.sourceComponent = pageComponent;
                        process.update_preset()
                    } else {
                        button.enabled = true;
                        errorLabel.visible = true;
                        errorLabel.message = result;
                    }
                }
                function download_component(componentName, button) {
                    for (var i = 0; i < buttonArray.length; i++) {
                        if (buttonArray[i] !== button){
                            buttonArray[i].enabled = false;
                        }
                    }
                    button.value += 0.02;
                    errorLabel.message = "";
                    errorLabel.title = backend.get_element_loc("component_not_installed_e");
                    var process_need_reload = process.is_process_alive()
                    process.stop_process()
                    backend.download_component(componentName, process_need_reload);
                }
                Connections {
                    target: backend
                    function onComponent_installing_finished() {
                        var success = arguments[0];
                        console.log(success);
                        for (var i = 0; i < buttonArray.length; i++) {
                            buttonArray[i].value = 0;
                            buttonArray[i].enabled = true;
                        }
                        if (success === 'True') {
                            pageLoader.sourceComponent = null;
                            pageLoader.sourceComponent = pageComponent;
                        } else if (success === 'reload_need') {
                            Qt.callLater(process.start_process)
                            pageLoader.sourceComponent = null;
                            pageLoader.sourceComponent = pageComponent;
                        }else {
                            errorLabel.visible = true;
                            errorLabel.message = success;
                        }
                    }
                }

            }

        }
    }

    Connections {
        target:goodCheck
        function onStarted(){
            exp.enabled = false;
        }
        function onProcess_finished_signal(){
            exp.enabled = true;
        }
    }

    Connections {
        target:proxyHelper
        function onProgressChanged(value) {
            value = Math.floor(value);
            if (state == 'PRXF_d') {
                state_text.text = qsTr(backend.get_element_loc("state_proxifyre_download")).arg(value)
            } else if (state == 'NDSA_d') {
                state_text.text = qsTr(backend.get_element_loc("state_ndsapi_download")).arg(value)
            } else if (state == 'NDSA_MSI_d') {
                state_text.text = qsTr(backend.get_element_loc('state_ndsapi_msi_download')).arg(value)
            }
        } 
        function onStateChanged(_state) {

            state = _state
            if (state == 'GETR') {
                state_text.text = backend.get_element_loc('getting_ready')
            } else if (state == 'PRXF_i') {
                state_text.text = backend.get_element_loc('state_proxifyre_installing')
            } else if (state == 'NDSA_i') {
                state_text.text = backend.get_element_loc('state_ndsapi_installing')
            } else if (state == 'NDSA_MSI_i') {
                state_text.text = backend.get_element_loc('state_ndsapi_msi_installing')
            }
        }
        function onDownloadFinished(errorCode) {
            loadingColumnLayout.visible = false
            addButton.enabled = true
            if (errorCode == 'True') {
                base_layout_complete.visible = true
            } else {
                base_layout_after_error.visible = true
                errorText.text = errorCode
            }
        }
    }
    
}
