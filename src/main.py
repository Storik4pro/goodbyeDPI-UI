from logger import AppLogger, hot_debugger

try:
    import asyncio
    import ctypes
    import getopt
    import logging
    import multiprocessing
    import os
    import sys
    import traceback

    from qasync import QEventLoop
    from _data import BACKUP_SETTINGS_FILE_PATH, BYEDPI_EXECUTABLE, DEBUG, DIRECTORY, \
            GOODBYE_DPI_PATH, LOG_LEVEL, SETTINGS_FILE_PATH, SPOOFDPI_EXECUTABLE, VERSION, \
            ZAPRET_EXECUTABLE, settings, text
    import resource_rc
    from PySide6.QtCore import QProcess
    from PySide6.QtGui import QGuiApplication, QIcon
    from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

    from FluentUI import FluentUIPlugin
    import Logger
    import GlobalConfig
    from Components import CircularReveal
    from AppInfo import AppInfo
    from Backend import Backend, Process, MultiWindow, GoodCheckHelper, AfterUpdateHelper, \
        Patcher, ProxyHelper, IconImageProvider, SystemProcessHelper
    from Backend.notification import Toast

    from quick_start import after_update_actions, check_app_is_runned, chk_directory, first_run_actions, kill_update, merge_settings, merge_blacklist, rename_update_exe, merge_settings_to_json
    logger = AppLogger(VERSION, "goodbyeDPI", LOG_LEVEL if not DEBUG else logging.DEBUG)
except:
    import traceback
    logger = AppLogger("-x-", "goodbyeDPI", logging.CRITICAL)
    logger.raise_critical(traceback.format_exc())

try:
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def run_app(first_run):
        hot_debugger.log('Getting ready backend...')
        backend = Backend(first_run)
        process = Process()
        toast = Toast()
        multiWindow = MultiWindow()
        goodCheck = GoodCheckHelper(process)
        afterUpdate = AfterUpdateHelper()
        patcher = Patcher()
        iconImageProvider = IconImageProvider()
        proxyHelper = ProxyHelper(iconImageProvider)
        systemProcessHelper = SystemProcessHelper(process)
        hot_debugger.log('Getting ready backend complete')
        
        print(sys.argv)
        hot_debugger.log('Getting ready style and app config...')
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "FluentUI"
        QGuiApplication.setOrganizationName(GlobalConfig.application_company)
        QGuiApplication.setOrganizationDomain(GlobalConfig.application_domain)
        QGuiApplication.setApplicationName(GlobalConfig.application_name)
        QGuiApplication.setApplicationDisplayName(GlobalConfig.application_name)
        QGuiApplication.setApplicationVersion(GlobalConfig.application_version)
        hot_debugger.log('Getting ready style and app config complete')
        
        hot_debugger.log('Setup logger...')
        Logger.setup("GoodbyeDPI_UI", level=LOG_LEVEL if not DEBUG else logging.DEBUG)
        hot_debugger.log('Setup logger complete')
        
        hot_debugger.log('Getting ready app...')
        app = QGuiApplication(sys.argv)
        engine = QQmlApplicationEngine()
        hot_debugger.log('Getting ready app complete')
        
        hot_debugger.log('Register backend in GoodbyeDPI_UI namespace...')
        engine.rootContext().setContextProperty("backend", backend)
        engine.rootContext().setContextProperty("process", process)
        engine.rootContext().setContextProperty("toast", toast)
        engine.rootContext().setContextProperty("appArguments", sys.argv)
        engine.rootContext().setContextProperty("multiWindow", multiWindow)
        engine.rootContext().setContextProperty("goodCheck", goodCheck)
        engine.rootContext().setContextProperty("updateHelper", afterUpdate)
        engine.rootContext().setContextProperty("patcher", patcher)
        engine.rootContext().setContextProperty("proxyHelper", proxyHelper)
        engine.rootContext().setContextProperty("systemProcessHelper", systemProcessHelper)
        engine.addImageProvider("icons", iconImageProvider)
        hot_debugger.log('Register complete')

        hot_debugger.log('Setup windows...')
        engine.addImportPath(":/qt/qml")
        
        icon = QIcon(DIRECTORY+"data/icon.ico")
        QGuiApplication.setWindowIcon(icon)

        AppInfo().init(engine)
        FluentUIPlugin.registerTypes()
        qml_file = "qrc:/qt/qml/GoodbyeDPI_UI/res/qml/App.qml"
        engine.load(qml_file)

        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        hot_debugger.log('Setup windows complte')

        if not engine.rootObjects():
            hot_debugger.log('rootObjects is None. Kill...')
            sys.exit(-1)

        hot_debugger.log('Loop started...')
        with loop:
            sys.exit(loop.run_forever())

    if __name__ == "__main__":
        if not DEBUG: multiprocessing.freeze_support()
        argv = sys.argv[1:]
        try:
            options, args = getopt.getopt(argv, "", ["after-update", "autorun", 
                                                     "after-patching", "after-failed-update", 
                                                     "debug", "enable-hot-debug-mode"])
        except getopt.GetoptError as err:
            pass

        autorun = 'False'
        after_update = False
        hot_debug = False
        first_run = settings.settings.getboolean('GLOBAL', 'is_first_run') if not DEBUG else False
        pompt = ' '

        for name, value in options:
            if name == '--after-update':
                after_update = True
                settings.change_setting('GLOBAL', 'update_complete', "False")
            if name == '--enable-hot-debug-mode':
                hot_debug = True
                hot_debugger.setup()
            pompt+=name+value

        is_run_as_admin = is_admin()
        hot_debugger.log(f"isRunAsAdmin: {is_run_as_admin}; isDebug: {DEBUG}")
        
        if not is_run_as_admin and not DEBUG:
            logger.raise_warning(text.inAppText['run_as_admin'])
            sys.exit(-1)
            
        hot_debugger.log(f"isAppRunAsAdmin check pass.")
        logger.create_debug_log("Getting ready for start application.")

        # ==> Getting ready
        hot_debugger.log(f"Checking other app instance...")
        check_app_is_runned(logger)
        hot_debugger.log(f"Checking other app instance complete")

        if settings.settings['GLOBAL']['hide_to_tray'] == "True":
            autorun = 'True'
        
        hot_debugger.log(f"autorun is {autorun}")
        try:
            if not DEBUG:
                # first run actions
                hot_debugger.log("First run actions...")
                first_run_actions()
                hot_debugger.log("First run actions complete")

                # check work directory 
                hot_debugger.log("Check work directory (cwd)...")
                chk_directory()
                hot_debugger.log("Check work directory (cwd) complete")

                # check components installed
                config = settings.settings
                config.set('GLOBAL', 'is_first_run', 'False')

                components_to_check = {
                    'spoofdpi': SPOOFDPI_EXECUTABLE,
                    'byedpi': BYEDPI_EXECUTABLE,
                    'zapret':ZAPRET_EXECUTABLE,
                }
                hot_debugger.log("Check components...")
                for component, executable in components_to_check.items():
                    component_path = os.path.join(DIRECTORY, "data", component, executable)
                    if config.getboolean('COMPONENTS', component) and not os.path.exists(component_path):
                        settings.change_setting('COMPONENTS', component, 'False')
                        logger.create_info_log(f'Component {component} will be unregistered, because {executable} not exist')

                hot_debugger.log("Check components complete")
                
                # check after update 
                hot_debugger.log("After update actions...")
                if not settings.settings.getboolean('GLOBAL', 'update_complete'):
                    after_update_actions(logger)
                hot_debugger.log("After update actions complete")
            
            hot_debugger.log("Saving settings...")
            settings.save_settings()
            hot_debugger.log("Saving settings complete")
        except:
            logger.raise_critical(traceback.format_exc())

        # ==> Running Qt
        hot_debugger.log("Running Qt...")
        try:
            run_app(first_run)
        except SystemExit:
            pass
        hot_debugger.log("Qt app is died. Cleanup logs...")
        logger.cleanup_logs()
        hot_debugger.log("Cleanup logs complete")
except SystemExit as ex:
    pass
except:
    import traceback
    logger.raise_critical(traceback.format_exc())