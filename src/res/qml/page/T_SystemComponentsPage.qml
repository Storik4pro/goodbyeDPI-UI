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
                                        process.change_engine('goodbyeDPI')
                                    } else {
                                        process.change_engine(component)
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
                        expanded: true
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
                            color: "#c0c0c0"
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
                    InfoBar {
                        id:errorLabel
                        severity: InfoBarType.Error
                        visible:false
                        title: backend.get_element_loc("component_not_installed_e")
                        message: ""
                    }
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
                    process.stop_process()
                    backend.download_component(componentName);
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
                        } else {
                            errorLabel.visible = true;
                            errorLabel.message = success;
                        }
                    }
                }

            }

        }
    }
    
}
