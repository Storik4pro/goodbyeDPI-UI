import os
import platform
import socket
import sys
import threading
import time

from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from ..FluentUI import FluentUIPlugin
from ..Gallery import GlobalConfig
from ..Gallery.AppInfo import AppInfo
from ..Gallery.Helper import Logger

from utils import change_setting, change_settings, check_version, check_winpty, delete_file, extract_zip, get_component_download_url, get_latest_release, get_download_url, download_update, open_custom_blacklist, open_folder, register_component, stop_servise, unregister_component
from _data import CONFIG_PATH, DEBUG_PATH, EXECUTABLES, REPO_NAME, REPO_OWNER, VERSION, settings, DEBUG, DIRECTORY, configs, text


KEY = 'GOODBYEDPI'

class Backend(QObject):
    download_url_ready = Signal(str)  
    download_progress = Signal(float)
    download_finished = Signal(str)
    component_installing_finished = Signal(str)

    def __init__(self, pipe, parent: QObject | None = ...) -> None:
        super().__init__()
        self.pipe = pipe

    @Slot(str, result=str)
    def get_element_loc(self, element_name):
        try:return text.inAppText[element_name]
        except:return "<globallocalize."+element_name+">"

    @Slot(result=list)
    def getComponentsList(self):
        return [
            {
                'key': '/goodbyedpi',
                'title': 'GoodbyeDPI',
                '_icon': "qrc:/qt/qml/Gallery/res/image/logo.png",
            },
            {
                'key': '/zapret',
                'title': 'Zapret',
                '_icon': "qrc:/qt/qml/Gallery/res/image/zapret.png",
            },
            {
                'key': '/byedpi',
                'title': 'ByeDPI',
                '_icon': "qrc:/qt/qml/Gallery/res/image/ByeDPI.png",
            },
            {
                'key': '/spoofdpi',
                'title': 'SpoofDPI',
                '_icon': "",
            },
        ]
    
    @Slot(str, str, result=bool)
    def load_preset(self, engine, path):
        print(">>>>>>>>>>>>>>>>>>>>>>>>\n\n\n"+path)
        try:
            change_setting('CONFIG', f'{engine.lower()}_config_path', path)
            configs[engine].configfile = path
            configs[engine].reload_config()
            return True
        except:
            change_setting('CONFIG', f'{engine.lower()}_config_path', "")
            return False
        
    @Slot(str, str)
    def save_preset(self, engine, path):
        configs[engine].copy_to(path)

    @Slot(str)
    def return_to_default(self, engine):
        change_setting('CONFIG', f'{engine.lower()}_config_path', "")
        configs[engine].configfile = CONFIG_PATH+f"/{engine.lower()}/user.json"
        configs[engine].reload_config()

    @Slot(result=str)
    def get_version(self):
        return VERSION

    @Slot(result=str)
    def getDnsV4(self):
        return settings.settings[KEY]['dns_value']

    @Slot(result=str)
    def getPortV4(self):
        return settings.settings[KEY]['dns_port_value']

    @Slot(result=str)
    def getDnsV6(self):
        return settings.settings[KEY]['dnsv6_value']

    @Slot(result=str)
    def getPortV6(self):
        return settings.settings[KEY]['dnsv6_port_value']
    
    @Slot(result=int)
    def getPreset(self):
        value = int(settings.settings[KEY]['preset'])
        return value if value <= 9 else value+1
    
    @Slot(str, str, bool)  
    def toggleBool(self, key, setting, value):
        change_setting(key, setting, str(value))

    @Slot()
    def changeLanguage(self):
        settings.reload_settings()
        text.reload_text()
        self.pipe.send('SETTINGS_UPDATE_NEED')
    
    @Slot(str, str, result=bool)
    def getBool(self, key, setting):
        if setting == '': return False
        sett = settings.settings[key][setting]
        if setting == "usebetafeatures" and DEBUG: sett = "True"
        return True if sett == 'True' else False
    
    @Slot(str, str, str)  
    def changeValue(self, key, setting, value):
        change_setting(key, setting, str(value))
    
    @Slot(str, str, result=str)
    def getValue(self, key, setting):
        return settings.settings[key][setting]
    
    @Slot(str, str, result=str)
    def get_from_config(self, config, key:str):
        return str(configs[config.lower()].get_value(key.lower()))
        
    @Slot(str, str, result=bool)
    def get_bool_from_config(self, config, key:str):
        return configs[config.lower()].get_value(key.lower())
        
    @Slot(str, str, str)
    def set_to_config(self, config, key:str, value:str):
        print(value, type(value))
        if value == "true": value = True
        elif value == "false": value = False
        elif value.isdigit(): value = int(value)
        configs[config.lower()].set_value(key.lower(), value)
    
    @Slot(str, str, result=int)
    def getInt(self, key, setting):
        return int(settings.settings[key][setting])

    @Slot()  
    def edit_custom_blacklist(self):
        open_custom_blacklist()
    
    @Slot()  
    def update_list(self):
        self.pipe.send('UPDATE_TXT')
    
    @Slot(str, str, str, str)
    def update_dns(self, currentDnsV4, currentPortV4, currentDnsV6, currentPortV6):
        print(currentDnsV4, currentPortV4, currentDnsV6, currentPortV6)
        change_settings('GOODBYEDPI', [
            ['dns_value', currentDnsV4],
            ['dns_port_value',currentPortV4], 
            ['dnsv6_value', currentDnsV6],
            ['dnsv6_port_value', currentPortV6], 
        ])
    
    @Slot(str, str)
    def update_preset(self, preset:str, engine:str):
        value = preset.split(".")[0]
        change_setting(engine, 'preset', value)

    @Slot(str)
    def zapret_update_preset(self, preset:str):
        value = preset.split(".")[0]
        change_setting('ZAPRET', 'preset', value)

    @Slot(result=str)
    def load_logo(self):
        print(os.path.abspath('data/icon.png'))
        return "qrc:/qt/qml/Gallery/res/image/logo.png" 

    # Opening Utils
    @Slot(result=str)
    def get_GDPI_version(self):
        return check_version()
    
    @Slot()
    def open_pseudoconsole(self):
        self.pipe.send('OPEN_PSEUDOCONSOLE')

    @Slot()
    def open_chkpreset(self):
        self.pipe.send('OPEN_CHKPRESET')

    @Slot(result=bool)
    def check_winpty(self):
        return check_winpty()

    @Slot()
    def add_to_autorun(self):
        self.pipe.send('ADD_TO_AUTORUN')

    @Slot()
    def remove_from_autorun(self):
        self.pipe.send('REMOVE_FROM_AUTORUN')

    @Slot()
    def _update(self):
        if not DEBUG:self.pipe.send('UPDATE_INSTALL')

    @Slot(str)
    def changeMode(self, mode):
        self.pipe.send('SET_MODE')

    @Slot(str)
    def open_component_folder(self, component_name:str):
        open_folder((DIRECTORY if not DEBUG else DEBUG_PATH)+\
                    f'data/'+('goodbyeDPI' if component_name == 'goodbyedpi' else component_name))
        
    @Slot(str, result=str)
    def remove_component(self, component_name:str):
        component_name = 'goodbyeDPI' if component_name == 'goodbyedpi' else component_name
        directory = os.path.join('E:/_component/' if DEBUG else settings.settings['GLOBAL']['work_directory']+f'data', component_name)
        print(directory)
        result = delete_file(directory)
        if result: return result
        return unregister_component(component_name)

    @Slot(str)
    def download_component(self, component_name:str):
        self.pipe.send('STOP_PROCESS')
        self.qthread = QThread()
        self.worker = DownloadComponent(component_name)
        self.worker.moveToThread(self.qthread)

        self.qthread.started.connect(self.worker.run)
        self.worker.downloadFinished.connect(self.component_installing_finished)
        self.worker.workFinished.connect(self.qthread.quit)
        self.worker.workFinished.connect(self.worker.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)
        

        self.qthread.start()

    @Slot()
    def get_download_url(self):
        self.qthread = QThread()
        self.worker = DownloadWorker()
        self.worker.moveToThread(self.qthread)

        self.qthread.started.connect(self.worker.run)
        self.worker.workFinished.connect(self.qthread.quit)
        self.worker.workFinished.connect(self.worker.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)
        self.worker.resultReady.connect(self.download_url_ready)

        self.qthread.start()

    @Slot()
    def download_update(self):
        self.qthread = QThread()
        self.worker = UpdateDownloadWorker()
        self.worker.moveToThread(self.qthread)

        self.qthread.started.connect(self.worker.run)
        self.worker.progressChanged.connect(self.download_progress)
        self.worker.downloadFinished.connect(self.download_finished)
        self.worker.workFinished.connect(self.qthread.quit)
        self.worker.workFinished.connect(self.worker.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)

        self.qthread.start()

    @Slot(result=bool)
    def check_mica(self):
        version = platform.version()
        major, minor, build = map(int, version.split('.'))
        return build >= 22000
    
class DownloadWorker(QObject):
    workFinished  = Signal()
    resultReady = Signal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        result = self._get_download_url()
        self.resultReady.emit(result)

        self.workFinished.emit()

    def _get_download_url(self):

        version = get_latest_release()

        time.sleep(5)

        return version if version != VERSION else 'false'
    
    
class UpdateDownloadWorker(QObject):
    progressChanged = Signal(float)
    downloadFinished = Signal(str)
    workFinished = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        success = self._download_update()
        self.downloadFinished.emit(success)
        self.workFinished.emit()

    def _download_update(self):
        import requests
        filename = '_portable.zip'
        directory = os.path.join((DEBUG_PATH if DEBUG else settings.settings['GLOBAL']['work_directory']), filename)
        try:
            url = get_download_url(get_latest_release())
        except KeyError:
            return 'ERR_INVALID_SERVER_RESPONSE'

        if "ERR" in url:
            self.progressChanged.emit(0.0)
            return url
        
        try:
            download_update(url, directory, self.progressChanged)
            change_setting('GLOBAL', 'after_update', "True")
        except requests.ConnectionError:
            return 'ERR_CONNECTION_LOST'
        except IOError:
            return 'ERR_FILE_WRITE'
        except Exception as ex:
            return 'ERR_UNKNOWN'

        return 'True'  
    
class DownloadComponent(QObject):
    downloadFinished = Signal(str)
    workFinished = Signal()

    def __init__(self, component_name:str) -> None:
        super().__init__()
        self.component_name = 'goodbyeDPI' if component_name == 'goodbyedpi' else component_name
    
    def run(self):
        success = self._download_component()
        self.downloadFinished.emit(success)
        self.workFinished.emit()

    def _download_component(self):
        import requests
        try:
            url = get_component_download_url(self.component_name)
        except KeyError as ex:
            return 'ERR_INVALID_SERVER_RESPONSE'
        
        filename = 'unknown_component.zip' if url.endswith(".zip") else\
                   EXECUTABLES[self.component_name]
        _dir = 'E:/_component/' if DEBUG else settings.settings['GLOBAL']['work_directory']+f'data/{self.component_name}'
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        directory = os.path.join(_dir, filename)

        if "ERR" in url:
            return url
        
        try:
            download_update(url, directory)
            if filename.endswith(".zip"):
                if not DEBUG: stop_servise()
                skipfiles = [
                    '.cmd', '.bat', '.vbs',
                ]
                extract_to = f"{DIRECTORY}/data/{self.component_name}" if not DEBUG else f"E:/_component/{self.component_name}"
                if self.component_name == 'zapret':
                    folder_to_unpack = "zapret-win-bundle-master/zapret-winws/"

                elif self.component_name == 'goodbyeDPI':
                    folder_to_unpack = "/"

                elif self.component_name == 'byedpi':
                    folder_to_unpack = ""

                result = extract_zip(zip_file=directory, zip_folder_to_unpack=folder_to_unpack, 
                                     extract_to=extract_to, files_to_skip=skipfiles)
                if result: return result

                delete_file(file_path=directory)

                result = register_component(self.component_name)
                if result: return result
            elif filename.endswith(".exe"):
                if not DEBUG: stop_servise()
                result = register_component(self.component_name)
                if result: return result
            print("END")

        except requests.ConnectionError:
            return 'ERR_CONNECTION_LOST'
        except IOError:
            return 'ERR_FILE_WRITE'
        except Exception as ex:
            return 'ERR_UNKNOWN'

        return 'True'  

_uri = "Gallery"
_major = 1
_minor = 0

def run_qt_app(pipe):
    start_time = time.time()
    
    backend = Backend(pipe=pipe)
    print(f"Backend initialized in {time.time() - start_time} seconds")
    
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "FluentUI"
    QGuiApplication.setOrganizationName(GlobalConfig.application_company)
    QGuiApplication.setOrganizationDomain(GlobalConfig.application_domain)
    QGuiApplication.setApplicationName('GoodbyeDPI UI')
    QGuiApplication.setApplicationDisplayName('Settings')
    QGuiApplication.setApplicationVersion(GlobalConfig.application_version)
    
    if DEBUG:
        Logger.setup("Gallery")
    print(f"Settings configured in {time.time() - start_time} seconds")
    
    app = QGuiApplication([DIRECTORY+'_settings/Gallery/main.py'] if not DEBUG else [f'{DEBUG_PATH}/src/_settings/main.py'])
    print(f"QGuiApplication initialized in {time.time() - start_time} seconds")
    
    engine = QQmlApplicationEngine()
    print(f"QQmlApplicationEngine initialized in {time.time() - start_time} seconds")
    
    engine.rootContext().setContextProperty("backend", backend)
    icon = QIcon(DIRECTORY+"data/icon.ico")
    QGuiApplication.setWindowIcon(icon)
    engine.addImportPath(":/qt/qml")
    
    AppInfo().init(engine)
    print(f"AppInfo initialized in {time.time() - start_time} seconds")
    
    FluentUIPlugin.registerTypes()
    print(f"FluentUIPlugin registered in {time.time() - start_time} seconds")
    
    qml_file = "qrc:/qt/qml/Gallery/res/qml/App.qml"
    engine.load(qml_file)
    print(f"QML file loaded in {time.time() - start_time} seconds")
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())
    print(f"Total startup time: {time.time() - start_time} seconds")


