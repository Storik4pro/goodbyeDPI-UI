import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

ScrollablePage {
    id: page
    title: backend.get_element_loc('additional')

    header: ColumnLayout {
    ColumnLayout {
        id:heade
        Layout.topMargin: 0
        Layout.leftMargin: 24
        Layout.rightMargin: 24
        Layout.fillWidth: true

        Label {
            text: qsTr(backend.get_element_loc('after_update_title'))
            font: Typography.title
        }
        Label {
            text: qsTr(backend.get_element_loc('after_update_info'))
            font: Typography.bodyLarge
        }
    }
    }
    ColumnLayout{
        Layout.fillHeight:true
        Label {
            text: qsTr(backend.get_element_loc('after_update_total'))
            font: Typography.bodyStrong
        }
        RowLayout {
            Layout.fillHeight:true
            ProgressRing{
                id: progressRingMovingSettings
                indeterminate: true
                strokeWidth:3
                Layout.preferredWidth: 20
                Layout.preferredHeight: 20
                visible:true
            }
            Icon {
                id: iconMovingSettings
                source:FluentIcons.graph_CompletedSolid
                color: Theme.res.systemFillColorSuccess
                Layout.preferredWidth: 20
                Layout.preferredHeight: 20
                visible:false
            }
            Label {
                Layout.preferredHeight: 20
                text: qsTr(backend.get_element_loc('after_update_moving_settings'))
            }
        }
        RowLayout {
            Layout.fillHeight:true
            ProgressRing{
                id: progressRingCleanup
                indeterminate: true
                strokeWidth:3
                Layout.preferredWidth: 20
                Layout.preferredHeight: 20
                visible:true
            }
            Icon {
                id: iconCleanup
                source:FluentIcons.graph_CompletedSolid
                color: Theme.res.systemFillColorSuccess
                Layout.preferredWidth: 20
                Layout.preferredHeight: 20
                visible:false
            }
            Label {
                Layout.preferredHeight: 20
                text: qsTr(backend.get_element_loc('after_update_cleanup'))
            }
        }
        RowLayout {
            Layout.fillHeight:true
            ProgressRing{
                id: progressRingUpdatingComponents
                indeterminate: true
                strokeWidth:3
                Layout.preferredWidth: 20
                Layout.preferredHeight: 20
                visible:true
            }
            Icon {
                id: iconUpdatingComponents
                source:FluentIcons.graph_CompletedSolid
                color: Theme.res.systemFillColorSuccess
                Layout.preferredWidth: 20
                Layout.preferredHeight: 20
                visible:false
            }
            Label {
                Layout.preferredHeight: 20
                text: qsTr(backend.get_element_loc('after_update_finish'))
            }
        }
    }

    footer: ColumnLayout {
        id: qfooter
    ColumnLayout{
        Layout.bottomMargin: 24
        Layout.leftMargin: 24
        Layout.rightMargin: 12
        Layout.fillWidth: true
        
        Label {
            id:lbl
            text: backend.get_element_loc('after_update_moving_settings')
            font: Typography.bodyStrong
        }

        ProgressBar {
            id: prgBrInd
            visible:false
            Layout.fillWidth: true
            Layout.rightMargin: 12
            indeterminate:true
            Layout.bottomMargin: 2
        }
        ProgressBar {
            id: prgBr
            visible:false
            Layout.fillWidth: true
            Layout.rightMargin:12
            from: 0
            to: 100
            value:0
            Layout.bottomMargin: 2
        }
        CopyableText {
            id:status
            text: backend.get_element_loc('working_on_it')
            Layout.bottomMargin: 12
        }
        RowLayout {
            Layout.rightMargin: 12
            Layout.fillWidth: true
            spacing: 24

            Button {
                id: copy_button
                text: qsTr(backend.get_element_loc('quit'))
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth: 200
                enabled:false
                spacing: 5
                onClicked: {
                }
            }

            Item { Layout.fillWidth: true }

            IconButton {
                id: restart_button
                text: qsTr(backend.get_element_loc('get_help'))
                icon.name: FluentIcons.graph_FavoriteStar
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth: 200
                onClicked: {
                    Qt.openUrlExternally("https://github.com/Storik4pro/goodbyeDPI-UI/discussions")
                }
            }

            Button {
                id: stop_button
                visible:false
                text: qsTr(backend.get_element_loc('next_button'))
                icon.width: 18
                icon.height: 18
                Layout.preferredWidth: 200
                onClicked: {

                }
                ToolTip.visible: hovered
                ToolTip.delay: 500
                ToolTip.text: qsTr(backend.get_element_loc('pseudoconsole_stop'))
            }
        }
    
    }
    
    }
    Connections {
        target: updateHelper

        function onProgressIndeterminateVisibleChanged(visible) {
            prgBrInd.visible = visible;
            prgBr.visible = !visible;
        }
        function onProgressVisibleChanged(visible) {
            prgBrInd.visible = !visible;
            prgBr.visible = visible;
        }
        function onProgressValueChanged(value) {
            prgBr.value = value;
        }
        function onUpdateMovingSettingsCompleted() {
            prgBrInd.visible = true;
            progressRingMovingSettings.visible = false;
            iconMovingSettings.visible = true;
        }
        function onUpdateCleanupStarted() {
            progressRingCleanup.visible = true;
            iconCleanup.visible = false;
            lbl.text = backend.get_element_loc('after_update_cleanup');
        }
        function onUpdateCleanupCompleted() {
            progressRingCleanup.visible = false;
            iconCleanup.visible = true;

        }
        function onUpdateComponentsStarted() {
            progressRingUpdatingComponents.visible = true;
            iconUpdatingComponents.visible = false;
            lbl.text = backend.get_element_loc('after_update_updating_components');
        }
        function onUpdateComponentsCompleted() {
            progressRingUpdatingComponents.visible = false;
            iconUpdatingComponents.visible = true;
        }
        function onRemainingTimeChanged(remainingTime) {
        if (remainingTime[0] !== "") {
            if (remainingTime[1] !== 0){
                status.text = qsTr(backend.get_element_loc(remainingTime[0])).arg(remainingTime[1])
            } else {
                status.text = qsTr(backend.get_element_loc(remainingTime[0]))
            }
        } else {
            status.text = backend.get_element_loc("working_on_it")
        }
    }
    }
    Component.onCompleted: {
        updateHelper.startUpdateProcess()
        prgBrInd.visible = true;
    }
}
