import os
from pathlib import Path
import platform
import shutil
import sys
import time

from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
import requests

from ..FluentUI import FluentUIPlugin
from ..Gallery import GlobalConfig
from ..Gallery.AppInfo import AppInfo
from ..Gallery.Helper import Logger

from utils import change_setting, change_settings, get_latest_release, get_download_url, download_update, open_custom_blacklist
from _data import REPO_NAME, REPO_OWNER, VERSION, settings, DEBUG, DIRECTORY, text


KEY = 'GOODBYEDPI'

class Backend(QObject):
    download_url_ready = Signal(str)  
    download_progress = Signal(float)
    download_finished = Signal(str)

    def __init__(self, pipe, parent: QObject | None = ...) -> None:
        super().__init__()
        self.pipe = pipe

    @Slot(str, result=str)
    def get_element_loc(self, element_name):
        try:return text.inAppText[element_name]
        except:return "<globallocalize."+element_name+">"

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
    
    @Slot(str, str, result=bool)
    def getBool(self, key, setting):
        return True if settings.settings[key][setting] == 'True' else False
    
    @Slot(str, str, str)  
    def changeValue(self, key, setting, value):
        change_setting(key, setting, str(value))
    
    @Slot(str, str, result=str)
    def getValue(self, key, setting):
        return settings.settings[key][setting]

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
    
    @Slot(str)
    def update_preset(self, preset:str):
        value = preset.split(".")[0]
        change_setting('GOODBYEDPI', 'preset', value)

    @Slot(result=str)
    def load_logo(self):
        print(os.path.abspath('data/icon.png'))
        return 'file:///'+os.path.abspath('data/icon.png')

    # Opening Utils
    @Slot(result=str)
    def get_GDPI_version(self):
        return "0.2.3rc3"
    @Slot()
    def open_pseudoconsole(self):
        self.pipe.send('OPEN_PSEUDOCONSOLE')

    @Slot()
    def add_to_autorun(self):
        self.pipe.send('ADD_TO_AUTORUN')

    @Slot()
    def remove_from_autorun(self):
        self.pipe.send('REMOVE_FROM_AUTORUN')

    @Slot()
    def _update(self):
        self.pipe.send('UPDATE_INSTALL')

    @Slot(str)
    def changeMode(self, mode):
        self.pipe.send('SET_MODE')

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

        return version if version != settings.settings['GLOBAL']['version'] else 'false'
    
    
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
        filename = '_portable.zip'
        directory = os.path.join(('E:/ByeDPI/' if DEBUG else settings.settings['GLOBAL']['work_directory']), filename)
        try:
            url = get_download_url(get_latest_release())
        except KeyError:
            return 'ERR_IVALID_SERVER_RESPONSE'

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

_uri = "Gallery"
_major = 1
_minor = 0

def run_qt_app(pipe):
    backend = Backend(pipe=pipe)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "FluentUI"
    QGuiApplication.setOrganizationName(GlobalConfig.application_company)
    QGuiApplication.setOrganizationDomain(GlobalConfig.application_domain)
    QGuiApplication.setApplicationName('GoodbyeDPI UI')
    QGuiApplication.setApplicationDisplayName('Settings')
    QGuiApplication.setApplicationVersion(GlobalConfig.application_version)
    Logger.setup("Gallery")
    app = QGuiApplication([DIRECTORY+'_settings/Gallery/main.py'] if not DEBUG else ['E:/ByeDPI/src/_settings/main.py'])
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    icon = QIcon(DIRECTORY+"data/icon.ico")
    QGuiApplication.setApplicationName('GoodbyeDPI UI')
    QGuiApplication.setWindowIcon(icon)
    engine.addImportPath(":/qt/qml")
    AppInfo().init(engine)
    FluentUIPlugin.registerTypes()
    qml_file = "qrc:/qt/qml/Gallery/res/qml/App.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    result = QGuiApplication.exec()
    if result == 931:
        QProcess.startDetached(QGuiApplication.instance().applicationFilePath(), QGuiApplication.instance().arguments())


