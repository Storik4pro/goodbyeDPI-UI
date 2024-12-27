from logger import AppLogger

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
    from Backend import Backend, Process, Toast, MultiWindow, GoodCheckHelper, AfterUpdateHelper, \
        Patcher

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
        backend = Backend(first_run)
        process = Process()
        toast = Toast()
        multiWindow = MultiWindow()
        goodCheck = GoodCheckHelper()
        afterUpdate = AfterUpdateHelper()
        patcher = Patcher()
        print(sys.argv)
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "FluentUI"
        QGuiApplication.setOrganizationName(GlobalConfig.application_company)
        QGuiApplication.setOrganizationDomain(GlobalConfig.application_domain)
        QGuiApplication.setApplicationName(GlobalConfig.application_name)
        QGuiApplication.setApplicationDisplayName(GlobalConfig.application_name)
        QGuiApplication.setApplicationVersion(GlobalConfig.application_version)
        Logger.setup("GoodbyeDPI_UI", level=LOG_LEVEL if not DEBUG else logging.DEBUG)
        app = QGuiApplication(sys.argv)
        engine = QQmlApplicationEngine()
        
        engine.rootContext().setContextProperty("backend", backend)
        engine.rootContext().setContextProperty("process", process)
        engine.rootContext().setContextProperty("toast", toast)
        engine.rootContext().setContextProperty("appArguments", sys.argv)
        engine.rootContext().setContextProperty("multiWindow", multiWindow)
        engine.rootContext().setContextProperty("goodCheck", goodCheck)
        engine.rootContext().setContextProperty("updateHelper", afterUpdate)
        engine.rootContext().setContextProperty("patcher", patcher)

        engine.addImportPath(":/qt/qml")
        
        icon = QIcon(DIRECTORY+"data/icon.ico")
        QGuiApplication.setWindowIcon(icon)

        AppInfo().init(engine)
        FluentUIPlugin.registerTypes()
        qml_file = "qrc:/qt/qml/GoodbyeDPI_UI/res/qml/App.qml"
        engine.load(qml_file)

        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)

        if not engine.rootObjects():
            sys.exit(-1)

        with loop:
            sys.exit(loop.run_forever())

    if __name__ == "__main__":
        if not DEBUG: multiprocessing.freeze_support()
        argv = sys.argv[1:]
        try:
            options, args = getopt.getopt(argv, "", ["after-update", "autorun", 
                                                     "after-patching", "after-failed-update"])
        except getopt.GetoptError as err:
            pass

        autorun = 'False'
        after_update = False
        first_run = settings.settings.getboolean('GLOBAL', 'is_first_run') if not DEBUG else False
        pompt = ' '

        for name, value in options:
            if name == '--after-update':
                after_update = True
                settings.change_setting('GLOBAL', 'update_complete', "False")
            pompt+=name+value

        if not is_admin() and not DEBUG:
            logger.raise_warning(text.inAppText['run_as_admin'])
            sys.exit(-1)
            
        
        logger.create_debug_log("Getting ready for start application.")

        # ==> Getting ready

        check_app_is_runned(logger)

        if settings.settings['GLOBAL']['hide_to_tray'] == "True":
            autorun = 'True'
        try:
            if not DEBUG:
                # first run actions
                first_run_actions()

                # check work directory 
                chk_directory()

                # check components installed
                config = settings.settings
                config.set('GLOBAL', 'is_first_run', 'False')

                components_to_check = {
                    'spoofdpi': SPOOFDPI_EXECUTABLE,
                    'byedpi': BYEDPI_EXECUTABLE,
                    'zapret':ZAPRET_EXECUTABLE,
                }

                for component, executable in components_to_check.items():
                    component_path = os.path.join(DIRECTORY, "data", component, executable)
                    if config.getboolean('COMPONENTS', component) and not os.path.exists(component_path):
                        settings.change_setting('COMPONENTS', component, 'False')
                        logger.create_info_log(f'Component {component} will be unregistered, because {executable} not exist')

                # check after update actions
                if not settings.settings.getboolean('GLOBAL', 'update_complete'):
                    after_update_actions(logger)

                
            settings.save_settings()
        except:
            logger.raise_critical(traceback.format_exc())

        # ==> Running Qt
        try:
            run_app(first_run)
        except SystemExit:
            pass

        logger.cleanup_logs()
except SystemExit as ex:
    pass
except:
    import traceback
    logger.raise_critical(traceback.format_exc())