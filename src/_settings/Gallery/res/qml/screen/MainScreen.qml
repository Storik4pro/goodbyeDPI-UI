import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import Gallery

Item{
    property list<QtObject> originalItems : [
        PaneItem{
            key: "/personalize"
            title: backend.get_element_loc('personalize')
            icon.name: FluentIcons.graph_Personalize
        },
        PaneItem{
                key: "/system"
                title: backend.get_element_loc('system')
                icon.name: FluentIcons.graph_System
        },
        PaneItem{
                key: "/additional"
                title: backend.get_element_loc('additional')
                icon.name: FluentIcons.graph_Package
        },
        PaneItem{
                key: "/update"
                title: backend.get_element_loc('_update')
                icon.name: FluentIcons.graph_Sync
        },
        PaneItemHeader{
            title: backend.get_element_loc('components')
        }

    ]
    property list<QtObject> originalFooterItems : [
        PaneItem{
            icon.name: FluentIcons.graph_Info
            key: "/about"
            title: backend.get_element_loc('about')
        }
    ]
    PageRouter{
        id: page_router
        routes: {
            "/": {url: resolvedUrl("res/qml/page/T_Personalize.qml"),singleton:true},
            "/about": resolvedUrl("res/qml/page/T_About.qml"),
            "/system": resolvedUrl("res/qml/page/T_System.qml"),
            "/goodbyedpi/advanced": resolvedUrl("res/qml/page/T_GoodbyedpiAdvanced.qml"),
            "/additional": resolvedUrl("res/qml/page/T_AdditionalUtils.qml"),
            "/personalize": resolvedUrl("res/qml/page/T_Personalize.qml"),
            "/goodbyedpi": resolvedUrl("res/qml/page/T_Goodbyedpi.qml"),
            "/zapret": resolvedUrl("res/qml/page/T_Zapret.qml"),
            "/spoofdpi": resolvedUrl("res/qml/page/T_Spoofdpi.qml"),
            "/byedpi": resolvedUrl("res/qml/page/T_Byedpi.qml"),
            "/update": resolvedUrl("res/qml/page/T_Update.qml"),
        }
    }
    NavigationView{
        id: navigation_view
        router: page_router
        anchors.fill: parent
        logo: "qrc:/qt/qml/Gallery/res/image/logo.png"
        title: "GoodbyeDPI UI - Settings"
        items: originalItems
        footerItems: originalFooterItems
        displayMode: Global.displayMode
        appBarHeight: Qt.platform.os === "osx" ? 68 : 48
        titleBarTopMargin: Qt.platform.os === "osx" ? 20 : 0
        autoSuggestBox: AutoSuggestBox{
            id: auto_suggset_search
            placeholderText: backend.get_element_loc('search')
            items: []
            trailing: RowLayout{
                IconButton{
                    implicitWidth: 30
                    implicitHeight: 20
                    icon.name: FluentIcons.graph_ChromeClose
                    icon.width: 10
                    icon.height: 10
                    visible: auto_suggset_search.text !== ""
                    onClicked: {
                        auto_suggset_search.clear()
                    }
                }
                IconButton{
                    implicitWidth: 30
                    implicitHeight: 20
                    icon.name: FluentIcons.graph_Search
                    enabled: false
                    icon.width: 14
                    icon.height: 14
                }
            }
            onTap:
                (item)=>{
                    if(item.key){
                        page_router.go(item.key)
                    }
                }
            Connections{
                target: navigation_view
                function onSourceItemsChanged(data){
                    auto_suggset_search.items = data.filter((item)=>{ return item instanceof PaneItem})
                }
            }
        }

        onTap:
            (item)=>{
                if(item.key){
                    page_router.go(item.key)
                }
            }
    }
    Component {
        id: paneItemComponent
        PaneItem {
            property var data 
            property var key: componentKey
            property var title: componentTitle
            property var _icon
        }
    }

    Component.onCompleted:{
        var components = backend.getComponentsList();
        for (var i = 0; i < components.length; i++) {
            var component = components[i];

            var paneItem = paneItemComponent.createObject(navigation_view, {
                "key": component.key,
                "title": component.title,
                "icon.name": component._icon === "" ? FluentIcons.graph_Ethernet : component._icon,
            });
            if (paneItem !== null) {
                originalItems.push(paneItem);
            } else {
                console.error("Error PaneItem");
            }
        }
        page_router.go("/")
    }
}
