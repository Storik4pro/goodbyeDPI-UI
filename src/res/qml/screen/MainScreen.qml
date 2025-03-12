import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI

Item{
    property list<QtObject> originalItems : [
        PaneItem{
            key: "/"
            title: backend.get_element_loc('home')
            icon.name: FluentIcons.graph_Home
        },
        PaneItemHeader{
            title: backend.get_element_loc('settings')
        },
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
            "/": {url: resolvedUrl("res/qml/page/T_Home.qml"),singleton:true},
            "/about": resolvedUrl("res/qml/page/T_About.qml"),
            "/system": {url: resolvedUrl("res/qml/page/T_System.qml")},
            "/goodbyedpi/advanced": resolvedUrl("res/qml/page/T_GoodbyedpiAdvanced.qml"),
            "/additional": resolvedUrl("res/qml/page/T_AdditionalUtils.qml"),
            "/personalize": resolvedUrl("res/qml/page/T_Personalize.qml"),
            "/goodbyedpi": resolvedUrl("res/qml/page/T_Goodbyedpi.qml"),
            "/zapret": resolvedUrl("res/qml/page/T_Zapret.qml"),
            "/spoofdpi": resolvedUrl("res/qml/page/T_Spoofdpi.qml"),
            "/byedpi": resolvedUrl("res/qml/page/T_Byedpi.qml"),
            "/update": resolvedUrl("res/qml/page/T_Update.qml"),
            "/proxy": resolvedUrl("res/qml/page/T_Proxy.qml"),
        }
    }
    Menu{
        id: item_menu
        property var item
        MenuItem{
            text: backend.get_element_loc("open_in_new_window")
            enabled: item_menu.item.key !== "/system" && item_menu.item.key !== "/"
            onClicked: {
                var url = page_router.toUrl(item_menu.item.key)
                var title = item_menu.item.title
                if(url && !multiWindow.check_window_init(title) && item_menu.item.key !== "/system"){
                    WindowRouter.go("/page",{url:url,title:title})
                }
            }
        }
        function showMenu(item){
            item_menu.item = item
            item_menu.popup()
        }
    }
    NavigationView{
        id: navigation_view
        router: page_router
        anchors.fill: parent
        logo: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/logo.png"
        title: "GoodbyeDPI UI"
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
        onRightTap:
            (item)=>{
                if(item.key){
                    item_menu.showMenu(item)
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
    Connections {
        target:proxyHelper
        function onOpenProxySettings(){
            page_router.go("/proxy")
        }
    }
    Connections {
        target:toast
        function onNotificationAction(notificationId, action) {
            if (notificationId === "#NOTF_UPDATE") {
                if (action === "user_not_dismissed") {
                    Qt.callLater(page_router.go, "/update")
                }
            } else if (notificationId === "#NOTF_COMP_UPDATE") {
                if (action === "user_not_dismissed") {
                    Qt.callLater(page_router.go, "/system")
                }
            }  else if (notificationId == '#NOTF_GOODCHECK_OPEN') {
                if (action === "user_not_dismissed") {
                    page_router.go("/additional",{info:"GoodCheck"})
                    
                }
            }
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
