import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import FluentUI.Controls
import FluentUI.impl
import GoodbyeDPI_UI
import Qt.labs.platform as P
import QtQuick.Window

FramelessWindow {
    id: window
    property alias infoBarManager: infobar_manager
    property var tourSteps: []
    property var engine: backend.getValue('GLOBAL', 'engine')
    property var _height: backend.getInt("APPEARANCE_MODE", 'height')
    property var _width: backend.getInt("APPEARANCE_MODE", 'width')
    property var screenGeometryx: Screen.desktopAvailableHeight
    property var screenGeometryy: Screen.desktopAvailableWidth
    width: backend.getBool("APPEARANCE_MODE", "use_custom_window_size") ? _width : 838
    height: backend.getBool("APPEARANCE_MODE", "use_custom_window_size") ? _height : 652
    x: backend.get_first_run() ? undefined:backend.getValue("APPEARANCE_MODE", "x")
    y: backend.get_first_run() ? undefined:backend.getValue("APPEARANCE_MODE", "y")
    minimumWidth: 484
    minimumHeight: 300
    visible: true
    fitsAppBarWindows: true
    launchMode: WindowType.SingleInstance
    windowEffect: Global.windowEffect
    autoDestroy: false
    appBar: AppBar{
        implicitHeight: 48
        windowIcon: Item{}
    }
    initialItem: resolvedUrl("res/qml/screen/MainScreen.qml")
    /*onNewInit:
        (argument)=>{
            if(argument.type===0){
                dialog_program_already.argsText = argument.args
                dialog_program_already.open()
            }
        }
    */
    Dialog {
        id: dialog_close
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        parent: Overlay.overlay
        modal: true
        title: backend.get_element_loc("hide_to_tray_title")
        Column {
            spacing: 20
            anchors.fill: parent
            Label {
                width: 350
                wrapMode: Text.Wrap
                text: backend.get_element_loc("hide_to_tray")
            }
            CheckBox {
                id: checkBoxA
                text: backend.get_element_loc("do_not_ask")
                checked: backend.getBool("OTHER", "do_not_ask_quit_dialog")
                onClicked: {
                    backend.toggleBool("OTHER", "do_not_ask_quit_dialog", checked)
                }
            }
        }
        footer: DialogButtonBox{
            Button{
                text: backend.get_element_loc("cancel")
                onClicked: {
                    dialog_close.close()
                }
            }
            Button{
                text: backend.get_element_loc("minimize")
                onClicked: {
                    if (checkBoxA.checked) {
                        backend.changeValue("APPEARANCE_MODE", 'quit_to', 'tray')
                    }
                    trayHide()
                    dialog_close.close()
                }
            }
            Button{
                text: backend.get_element_loc("quit")
                highlighted: true
                onClicked: {
                    if (checkBoxA.checked) {
                        backend.changeValue("APPEARANCE_MODE", 'quit_to', 'system')
                    }
                    exit()
                }
            }
        }
    }
    function exit() {
        var qw = window.width - _width
        var qh = window.height - _height
        if (backend.getBool("APPEARANCE_MODE", "use_custom_window_size")) {
            if (-50 > qw || qw > 50) {
                backend.changeValue("APPEARANCE_MODE", 'width', window.width)
            }
            if (-50 > qh || qh > 50) {
                backend.changeValue("APPEARANCE_MODE", 'height', window.height)
            }
        }
        var x = window.x
        var y = window.y + appBar.height - 17
        backend.changeValue("APPEARANCE_MODE", 'x', x)
        backend.changeValue("APPEARANCE_MODE", 'y', y)
        
        goodCheck.stop_process()
        process.stop_process()
        WindowRouter.exit(0)
    }
    onCloseListener: function(event){
        if (window.visibility !== Window.Minimized) {
            if (backend.getValue("APPEARANCE_MODE", "quit_to") === 'unknown') {
                dialog_close.open()
            } else if (backend.getValue("APPEARANCE_MODE", "quit_to") === 'tray') {
                trayHide()
            } else {
                exit()
            }
            
            event.accepted = false
        }
    }
    property var toolTip: "GoodbyeDPI UI - " + qsTr(backend.get_element_loc('state')).arg(engine) + " " +
                          (process.is_process_alive() ? backend.get_element_loc('runned') : backend.get_element_loc('stopped'))
    Component {
        id: trayIconComponent
        P.SystemTrayIcon {
            id: system_tray
            visible: true
            icon.source: process.is_process_alive() ? "qrc:/qt/qml/GoodbyeDPI_UI/res/image/tray_logo_green.png" : 
                                                      "qrc:/qt/qml/GoodbyeDPI_UI/res/image/tray_logo_red.png" 
            tooltip: toolTip
            menu: P.Menu {
                /*
                P.Menu {
                    title: backend.get_element_loc("open_settings")
                    P.MenuItem {
                        text: backend.get_element_loc("additional")
                        onTriggered: {
                        }
                    }
                    P.MenuItem {
                        text: backend.get_element_loc("update")
                        onTriggered: {
                        }
                    }
                    P.MenuSeparator {}
                    P.MenuItem {
                        text: qsTr("GoodbyeDPI")
                        onTriggered: {
                        }
                    }
                    P.MenuItem {
                        text: qsTr("Zapret")
                        onTriggered: {
                        }
                    }
                    P.MenuItem {
                        text: qsTr("ByeDPI")
                        onTriggered: {
                        }
                    }
                    P.MenuItem {
                        text: qsTr("SpoofDPI")
                        onTriggered: {
                        }
                    }
                }
                */
                P.MenuItem {
                    id:onItem
                    text: _checked? backend.get_element_loc("_off"):backend.get_element_loc("on")
                    //icon.source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/tray_logo_red.png"
                    property var _checked: process.is_process_alive()
                    onTriggered: {
                        if (_checked) {
                            var success = process.stop_process();
                            if (!success){
                                toast.show_error("#NOTF_FAI_retry", text.inAppText['error_title'],
                                            backend.get_element_loc('close_error') + " " + 
                                            process.get_executable() + " " + 
                                            backend.get_element_loc('close_error2'),
                                            backend.get_element_loc('retry'), "")
                            }
                            _checked = false;
                        } else {
                            process.start_process();
                            _checked = true;
                        }
                        
                    }
                }
                P.MenuSeparator {}
                P.Menu {
                    title: backend.get_element_loc("additional")
                    P.MenuItem {
                        text: qsTr(backend.get_element_loc("pseudoconsole_title")).arg(engine)
                        onTriggered: {
                            WindowRouter.go("/pseudoconsole")
                        }
                    }
                }
                P.Menu {
                    title: backend.get_element_loc("component")

                    P.MenuItem {
                        text: qsTr("GoodbyeDPI")
                        checkable:true
                        checked:engine === 'goodbyeDPI'
                        enabled:backend.getBool('COMPONENTS', 'goodbyedpi')
                        onTriggered: {
                            changeEngine('goodbyeDPI');
                        }
                    }
                    P.MenuItem {
                        text: qsTr("Zapret")
                        checkable:true
                        checked:engine === 'zapret'
                        enabled:backend.getBool('COMPONENTS', 'zapret')
                        onTriggered: {
                            changeEngine('zapret');
                        }
                    }
                    P.MenuItem {
                        text: qsTr("ByeDPI")
                        checked:engine === 'byedpi'
                        checkable:true
                        enabled:backend.getBool('COMPONENTS', 'byedpi')
                        onTriggered: {
                            changeEngine('byedpi');
                        }
                    }
                    P.MenuItem {
                        text: qsTr("SpoofDPI")
                        checked:engine === 'spoofdpi'
                        checkable:true
                        enabled:backend.getBool('COMPONENTS', 'spoofdpi')
                        onTriggered: {
                            changeEngine('spoofdpi');
                        }
                    }
                }
                P.MenuSeparator {}
                P.MenuItem {
                    text: backend.get_element_loc("maximize")
                    font.bold: true
                    onTriggered: {
                        window.show()
                        window.raise()
                        window.requestActivate()
                        if (system_tray) {
                            system_tray.destroy()
                        }
                    }
                }
                P.MenuItem {
                    text: backend.get_element_loc("quit")
                    onTriggered: {
                        process.stop_process();
                        Qt.callLater(WindowRouter.exit, 0)
                    }
                }
                
                
            }
            onActivated: (reason) => {
                if (reason === P.SystemTrayIcon.Trigger) {
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray) {
                        system_tray.destroy()
                    }
                }
            }
        }
    }
    function updateIcon() {
        if (system_tray) {
            system_tray.icon.source = process.is_process_alive() ? "qrc:/qt/qml/GoodbyeDPI_UI/res/image/tray_logo_green.png" : 
                                                                   "qrc:/qt/qml/GoodbyeDPI_UI/res/image/tray_logo_red.png"
            onItem._checked = process.is_process_alive()
            
        }
        toolTip = "GoodbyeDPI UI - " + qsTr(backend.get_element_loc('state')).arg(engine) + " " +
                          (process.is_process_alive() ? backend.get_element_loc('runned') : backend.get_element_loc('stopped'))
    }

    function changeEngine(_engine) {
        engine = _engine;
        if (process.is_process_alive()){
            process.stop_process();
            Qt.callLater(process.change_engine, _engine);
            Qt.callLater(process.start_process);
        } else {
            process.change_engine(_engine);
        }

    }

    property var system_tray

    function trayHide() {
        system_tray = trayIconComponent.createObject(window)
        updateIcon()
        window.hide()
        var qw = window.width - _width
        var qh = window.height - _height

        if (backend.getBool("APPEARANCE_MODE", "use_custom_window_size") ){
            if (-100 > qw || qw > 100) {
                backend.changeValue("APPEARANCE_MODE", 'width', window.width)
            }
            if (-100 > qh || qh > 100) {
                backend.changeValue("APPEARANCE_MODE", 'height', window.height)
            }
        }
        if (backend.getBool('NOTIFICATIONS', "hide_in_tray")) {
            toast.show_notification("#NOTF_MAXIMIZE", "GoodbyeDPI UI", backend.get_element_loc("tray_icon"))
        }
    }

    onVisibilityChanged: {
        if (window.visibility === Window.Minimized) {
            trayHide()
        } 
    }
    
    Component{
        id: comp_reveal
        CircularReveal{
            id: reveal
            target: window.contentItem
            anchors.fill: parent
            onAnimationFinished:{
                loader_reveal.sourceComponent = undefined
            }
            onImageChanged: {
                changeDark()
            }
        }
    }
    InfoBarManager{
        id: infobar_manager
        target: window.contentItem
        messageMaximumWidth: 380
    }
    AutoLoader{
        id:loader_reveal
        anchors.fill: parent
        z: 65535
    }
    function distance(x1,y1,x2,y2){
        return Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    }
    function handleDarkChanged(button){
        if(loader_reveal.sourceComponent){
            return
        }
        loader_reveal.sourceComponent = comp_reveal
        var target = window.contentItem
        var pos = button.mapToItem(target,0,0)
        var centerX = pos.x + button.width/2
        var centerY = pos.y + button.height/2
        var radius = Math.max(distance(centerX,centerY,0,0),distance(centerX,centerY,target.width,0),distance(centerX,centerY,0,target.height),distance(centerX,centerY,target.width,target.height))
        var reveal = loader_reveal.item
        reveal.start(reveal.width*Screen.devicePixelRatio,reveal.height*Screen.devicePixelRatio,Qt.point(centerX,centerY),radius,Theme.dark)
    }
    function changeDark(){
        if(Theme.dark){
            Theme.darkMode = FluentUI.Light
        }else{
            Theme.darkMode = FluentUI.Dark
        }
    }

    Connections{
        target: process
        function onError_happens(){
            window.show()
            window.raise()
            window.requestActivate()
            if (system_tray) {
                system_tray.destroy()
            }
            WindowRouter.go("/pseudoconsole");
        } 
        function onEngine_changed() {
            engine = backend.getValue('GLOBAL', 'engine');
            updateIcon()
        }
        function onProcess_started() {
            updateIcon()
        }
        function onProcess_stopped() {
            updateIcon()
        }
    }
    Item {
        id: blocker
        anchors.fill: parent
        z: 99999
        visible: false
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            onClicked: {
                backend.play_sound_grab()
            }
            hoverEnabled: true
            onEntered: {}
        }
    }

    Connections {
        target:goodCheck
        function onStarted() {
            WindowRouter.go("/goodcheck");
            blocker.visible = true;

        }
        function onProcess_finished_signal () {
            blocker.visible = false;
        }
        function onProcess_stopped_signal() {
            blocker.visible = false;
        }
    }
    Connections {
        target:backend
        function onLanguage_change() {
            window.show()
            window.raise()
            window.requestActivate()
            if (system_tray) {
                system_tray.destroy()
            }
            WindowRouter.removeWindow(window)
            Qt.callLater(WindowRouter.go, "/");
        }
        function onUpdates_checked(result) {
            if (result && backend.getBool('NOTIFICATIONS', 'comp_upd')) {
                delayTimer1.start()
                
            }
        }
    }
    Connections {
        target:toast
        function onNotificationAction(notificationId, action) {
            if (notificationId === "#NOTF_FAI_pseudoconsoleOpen") {
                if (action === "user_not_dismissed") {
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray) {
                        system_tray.destroy()
                    }
                    WindowRouter.go("/pseudoconsole");
                }
            } else if (notificationId === "#NOTF_MAXIMIZE") {
                if (action === "user_not_dismissed") {
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray) {
                        system_tray.destroy()
                    }
                }
            } else if (notificationId === "#NOTF_UPDATE") {
                if (action === "user_not_dismissed") {
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray) {
                        system_tray.destroy()
                    }
                }
            } else if (notificationId === "#NOTF_COMP_UPDATE") {
                if (action === "user_not_dismissed") {
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray) {
                        system_tray.destroy()
                    }
                }
            }
        }
    }

    Timer {
        id: delayTimer
        interval: 180000
        repeat: false
        onTriggered: {
            Qt.callLater(toast.show_notification, "#NOTF_UPDATE", "GoodbyeDPI UI", backend.get_element_loc("update_available_info"))
        }
    }
    Timer {
        id: delayTimer1
        interval: 100000
        repeat: false
        onTriggered: {
            Qt.callLater(toast.show_notification, "#NOTF_COMP_UPDATE", "GoodbyeDPI UI", backend.get_element_loc("update_c_available_info"))
        }
    }

    Component.onCompleted :{
        console.log(appArguments.indexOf("--autorun")) 
        if (appArguments.indexOf("--autorun") !== -1 || backend.getBool("GLOBAL", "hide_to_tray")) {
            Qt.callLater(process.start_process)
            if (backend.getBool('NOTIFICATIONS', "hide_in_tray")) {
                Qt.callLater(toast.show_notification, "#NOTF_MAXIMIZE", "GoodbyeDPI UI", backend.get_element_loc("tray_icon"))
            }
            system_tray = trayIconComponent.createObject(window)
            window.hide()
            
        }
        if (backend.check_updates()) {
            delayTimer.start()
        }
        updateIcon()
        backend.start_check_component_updates()
        
    }
   
    
}

