import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl

Rectangle {
    id: control
    property string codeSnippet
    property bool showDisabled: true
    color: Colors.transparent
    width: 300
    implicitHeight: layout_column.height
    border.width: 1
    radius: 8
    border.color: Theme.res.controlStrokeColorSecondary
    onCodeSnippetChanged: {
        try{
            for (var i = item_preview_content.children.length - 1; i >= 0; i--) {
                var child = item_preview_content.children[i]
                child.destroy()
            }
            Qt.createQmlObject(codeSnippet,item_preview_content)
        }catch(e){
            label_error.text = e.message
        }
    }
    ColumnLayout{
        id: layout_column
        spacing: 0
        width: parent.width - 2
        anchors.centerIn: parent
        Item{
            id: item_preview
            Layout.fillWidth: true
            implicitHeight: Math.max(64,item_preview_content.height + 40)
            Item{
                id: item_preview_content
                height: childrenRect.height
                enabled: !switch_disabled.checked
                anchors{
                    top: parent.top
                    left: parent.left
                    right: parent.right
                    leftMargin: 20
                    rightMargin: 20
                    topMargin: 20
                }
            }
            Label{
                id: label_error
                color: Colors.errorPrimaryColor
                anchors.centerIn: parent
                visible: item_preview_content.children.length === 0
            }
            Row{
                visible: control.showDisabled
                anchors{
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 20
                }
                Label{
                    text: qsTr("Disabled")
                    anchors.verticalCenter: parent.verticalCenter
                }
                Switch{
                    id: switch_disabled
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
        }
        Expander{
            id: expander
            Layout.fillWidth: true
            header: Label{
                text: qsTr("Source code")
                verticalAlignment: Qt.AlignVCenter
            }
            trailing: Button{
                anchors.centerIn: parent
                text: qsTr("Copy")
                visible: expander.expanded
                icon.name: FluentIcons.graph_Copy
                icon.width: 18
                icon.height: 18
                spacing: 5
                onClicked: {
                    Tools.clipText(codeSnippet)
                    infoBarManager.showSuccess(qsTr("Copy Success"))
                }
            }
            content: SyntaxView{
                id: syntax_view
                text: codeSnippet
                height: Math.max(textArea.implicitHeight,120)
                visible: expander.expanded
                onVisibleChanged: {
                    if(!visible){
                        syntax_view.textArea.focus = false
                    }
                }
                onTextChanged: {
                    control.codeSnippet = text
                }
            }
        }
    }
}
