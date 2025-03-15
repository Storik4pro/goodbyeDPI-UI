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
    property var currentError: ""
    property var currentErrorCode: ""
    property var tourSteps: []
    property var engine: backend.getValue('GLOBAL', 'engine')
    property var _height: backend.getInt("APPEARANCE_MODE", 'height')
    property var _width: backend.getInt("APPEARANCE_MODE", 'width')
    property var screenGeometryx: Screen.desktopAvailableHeight
    property var screenGeometryy: Screen.desktopAvailableWidth
    property bool isProcessCanStart:true
    property bool isMaximized: backend.getBool("APPEARANCE_MODE", "is_maximized")
    visibility:isMaximized ? Window.Maximized : undefined
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
    property var processStarted: process.is_process_alive()
    property var windowState: true
    initialItem: resolvedUrl("res/qml/screen/MainScreen.qml")
    appBar: AppBar{
        implicitHeight: 48
        windowIcon: Item{}
    }
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

    Dialog {
        id: errorDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("error")
        Flickable {
            id: errorFlickable
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
                        text: backend.get_element_loc("error_info_title")
                        wrapMode:Text.Wrap
                        font:Typography.bodyLarge
                        Layout.preferredWidth:askColumn.width-20
                        Layout.bottomMargin:10
                    }
                    Label {
                        text: backend.get_element_loc("error_info_tip")
                        wrapMode:Text.Wrap
                        font:Typography.bodyStrong
                        Layout.preferredWidth:askColumn.width-20
                    }
                    CopyableText {
                        id:askBlacklistDialogSubTitle
                        text: currentError
                        wrapMode:Text.Wrap
                        font:Typography.body
                        Layout.preferredWidth:askColumn.width-20
                    }
                    Label {
                        text: backend.get_element_loc("error_info_code")
                        wrapMode:Text.Wrap
                        font:Typography.bodyStrong
                        Layout.preferredWidth:askColumn.width-20
                    }
                    CopyableText {
                        text: currentErrorCode
                        wrapMode:Text.Wrap
                        font:Typography.body
                        Layout.preferredWidth:askColumn.width-20
                    }
                }            
            }
            ScrollBar.vertical: ScrollBar {
                
            }
        }
        footer: DialogButtonBox{
            Button{
                text: "OK"
                width:(errorDialog.width / 2) - 10
                highlighted: true
                visible:true
                onClicked: {
                    errorDialog.close()

                }
            }
            
        }
    }

    Dialog {
        id:pcRestart
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("restart_need")
        Column {
            spacing: 20
            anchors.fill: parent
            Label {
                width: 350
                wrapMode: Text.Wrap
                text: backend.get_element_loc("restart_need_tip")
            }
        }
        footer: DialogButtonBox{
            Button{
                text: backend.get_element_loc("restart_later")
                onClicked: {
                    pcRestart.close()
                }
            }
            Button{
                text: backend.get_element_loc("restart_now")
                highlighted:true
                onClicked: {
                    
                }
            }
        }
    }

    Dialog{
        id: proxySetupDialog
        x: Math.ceil((parent.width - width) / 2)
        y: Math.ceil((parent.height - height) / 2)
        width: 500
        contentHeight: 300
        parent: Overlay.overlay
        closePolicy: Popup.NoAutoClose
        modal: true
        title: backend.get_element_loc("first_proxy_setup")
        Flickable {
            id: proxySetupFlickable
            clip: true
            anchors.fill: parent
            anchors.rightMargin:-10
            anchors.leftMargin:-10
            contentHeight: proxySetupContentColumn.implicitHeight
            ColumnLayout {
                anchors.fill: parent
                anchors.rightMargin:20
                ColumnLayout {
                    id:proxySetupContentColumn
                    Layout.leftMargin:10
                    Layout.rightMargin:-10
                    Label {
                        text: backend.get_element_loc("first_proxy_setup_tip").arg(backend.getValue("PROXY", "proxy_addr")+ ":" + backend.getValue("PROXY", "proxy_port"))
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                    Button{
                        id:btn2
                        Layout.preferredHeight: Math.max(68, udpLay.implicitHeight + 10)
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
                                source: FluentIcons.graph_Network
                                Layout.preferredHeight:20
                            }
                            ColumnLayout{
                                id:udpLay
                                Layout.fillWidth: true
                                spacing: 2
                                Label{
                                    Layout.fillWidth: true
                                    text: backend.get_element_loc('setup_btn')
                                    horizontalAlignment: Text.AlignLeft
                                    wrapMode:Text.Wrap
                                    font: Typography.body
                                }
                                Label {
                                    text: backend.get_element_loc('first_setup_proxy_btn_tip')
                                    Layout.fillWidth: true
                                    font: Typography.caption
                                    color: "#c0c0c0"
                                    horizontalAlignment: Text.AlignLeft
                                    wrapMode:Text.Wrap
                                }
                            }
                            IconButton {
                                id: btn_icon1
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
                                    proxyHelper.open_setup()
                                    proxySetupDialog.close()
                                }
                            }
                        }
                        
                        onClicked: {
                            proxyHelper.open_setup()
                            proxySetupDialog.close()
                        }
                        
                    }
                }
            }
            ScrollBar.vertical: ScrollBar {}
        }
        footer: DialogButtonBox{
            Button{
                text: backend.get_element_loc("cancel")
                onClicked: {
                    backend.changeValue("PROXY", "proxy_now_used", "manual")
                    proxySetupDialog.close()
                }
            }
        }
    }
    function exit() {
        console.log(isMaximized)
        if (window.visibility !== Window.Maximized && 
            window.visibility !== Window.Minimized && 
            !isMaximized) {
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
        }
        
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
                    enabled:isProcessCanStart
                    text: processStarted ? backend.get_element_loc("_off"):backend.get_element_loc("on")
                    //icon.source: "qrc:/qt/qml/GoodbyeDPI_UI/res/image/tray_logo_red.png"
                    onTriggered: {
                        if (processStarted) {
                            var success = process.stop_process();
                            if (!success){
                                toast.show_error("#NOTF_FAI_retry", text.inAppText['error_title'],
                                            backend.get_element_loc('close_error') + " " + 
                                            process.get_executable() + " " + 
                                            backend.get_element_loc('close_error2'),
                                            backend.get_element_loc('retry'), "")
                            }
                            processStarted = false;
                        } else {
                            process.start_process();
                            processStarted = true;
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
                    enabled:!windowState
                    font.bold: true
                    onTriggered: {
                        windowState = true
                        window.show()
                        window.raise()
                        window.requestActivate()
                        if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
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
                    windowState = true
                    window.raise()
                    window.requestActivate()
                    if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
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
        }
        processStarted = process.is_process_alive()
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
        if (system_tray) {
            system_tray.destroy()
        }
        system_tray = trayIconComponent.createObject(window)
        updateIcon()
        window.hide()
        windowState = false
        var qw = window.width - _width
        var qh = window.height - _height
        console.log(isMaximized)
        if (!isMaximized) {
            if (backend.getBool("APPEARANCE_MODE", "use_custom_window_size") ){
                if (-100 > qw || qw > 100) {
                    backend.changeValue("APPEARANCE_MODE", 'width', window.width)
                }
                if (-100 > qh || qh > 100) {
                    backend.changeValue("APPEARANCE_MODE", 'height', window.height)
                }
            }
            var x = window.x
            var y = window.y + appBar.height - 17
            backend.changeValue("APPEARANCE_MODE", 'x', x)
            backend.changeValue("APPEARANCE_MODE", 'y', y)
        }
        if (backend.getBool('NOTIFICATIONS', "hide_in_tray")) {
            toast.show_notification("#NOTF_MAXIMIZE", "GoodbyeDPI UI", backend.get_element_loc("tray_icon"))
        }
    }

    onVisibilityChanged: {
        if (window.visibility === Window.Minimized) {
            if (backend.getValue("APPEARANCE_MODE", "quit_to") !== 'tray') {
                trayHide()
            }

        } else if (window.visibility === Window.Maximized) {
            backend.toggleBool("APPEARANCE_MODE", "is_maximized", true)
            isMaximized = true
        } else if (window.visibility !== Window.Hidden) {
            backend.toggleBool("APPEARANCE_MODE", "is_maximized", false)
            isMaximized = false
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

    Connections {
        target:proxyHelper
        function onStateChanged(state) {
            if (state == 'VS_RESTART') {
                pcRestart.open()
            } 
        }
    }

    Connections{
        target: process
        function onError_happens(){
            window.show()
            windowState = true
            window.raise()
            window.requestActivate()
            if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
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
        function onProcess_need_setup() {
            window.show()
            windowState = true
            window.raise()
            window.requestActivate()
            if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
                system_tray.destroy()
            }
            proxySetupDialog.open()
        }
        function onProcess_stopped() {
            updateIcon()
        }
    }
    Item {
        id: blocker
        anchors.fill: parent
        z: 99999
        enabled: false
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
        function onStarted(){
            isProcessCanStart = false;
        }
        function onProcess_finished_signal () {
            if (backend.getBool('NOTIFICATIONS', 'goodcheck_complete')) {
                Qt.callLater(toast.show_notification, "#NOTF_GOODCHECK_OPEN", "GoodCheck", backend.get_element_loc("goodcheck_complete"))
            }
            isProcessCanStart = true;
        }
    }
    
    Connections {
        target:proxyHelper
        function onErrorHappens(text, code) {
            currentError = text
            currentErrorCode = code
            errorDialog.open()
        }
    }
    Connections {
        target:backend
        function onLanguage_change() {
            window.show()
            windowState = true
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

        function onErrorHappens(text, code) {
            currentError = text
            currentErrorCode = code
            errorDialog.open()
        }
    }
    Connections {
        target:toast
        function onNotificationAction(notificationId, action) {
            if (notificationId === "#NOTF_FAI_pseudoconsoleOpen") {
                if (action === "user_not_dismissed") {
                    windowState = true
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
                        system_tray.destroy()
                    }
                    WindowRouter.go("/pseudoconsole");
                }
            } else if (notificationId === "#NOTF_MAXIMIZE") {
                if (action === "user_not_dismissed") {
                    windowState = true
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
                        system_tray.destroy()
                    }
                }
            } else if (notificationId === "#NOTF_UPDATE") {
                if (action === "user_not_dismissed") {
                    windowState = true
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
                        system_tray.destroy()
                    }
                }
            } else if (notificationId === "#NOTF_COMP_UPDATE") {
                if (action === "user_not_dismissed") {
                    windowState = true
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
                        system_tray.destroy()
                    }
                }
            } else if (notificationId == '#NOTF_GOODCHECK_OPEN') {
                if (action === "user_not_dismissed") {
                    windowState = true
                    window.show()
                    window.raise()
                    window.requestActivate()
                    if (system_tray && backend.getValue("APPEARANCE_MODE", "quit_to") !== "tray") {
                        system_tray.destroy()
                    }               
                }
            } else if (notificationId == '#NOTF_SERT_INFO_OPEN') {
                if (!backend.is_debug()) {
                    backend.toggleBool("NOTIFICATIONS", "is_sert_info_shown", true)
                }
                if (action === "user_not_dismissed") {
                    Qt.openUrlExternally("https://storik4pro.github.io/wiki/cert/")
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
            windowState = false
            
        } else if (backend.getValue("APPEARANCE_MODE", "quit_to") == "tray") {
            system_tray = trayIconComponent.createObject(window)
            updateIcon()
        }
        if (backend.check_updates()) {
            delayTimer.start()
        }
        /*
        if (!backend.getBool('NOTIFICATIONS', 'is_sert_info_shown')) {
            Qt.callLater(toast.show_sert_info, "#NOTF_SERT_INFO_OPEN", backend.get_element_loc('sert_title'), backend.get_element_loc("sert_info"), backend.get_element_loc('help'))
        }
        */

        updateIcon()
        backend.start_check_component_updates()
        
    }
   
    
}

