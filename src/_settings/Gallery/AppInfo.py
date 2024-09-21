from PySide6.QtCore import QObject, Signal, Property, QTranslator, QLocale
from PySide6.QtQml import QmlNamedElement, QmlSingleton, QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
from ..Gallery.Helper.SettingsHelper import SettingsHelper
from ..Gallery import GlobalConfig

QML_IMPORT_NAME = "Gallery"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlNamedElement("AppInfo")
@QmlSingleton
class __AppInfo(QObject):
    versionChanged = Signal()
    localeChanged = Signal()
    localesChanged = Signal()
    appIdChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__version = GlobalConfig.application_version
        self.__locales = ['en_US', 'zh_CN']
        self.__locale = SettingsHelper().getLocale()
        self.__translator = QTranslator()
        self.__appId = GlobalConfig.application_id

    @Property(str, notify=appIdChanged)
    def appId(self):
        return self.__appId

    @appId.setter
    def appId(self, value):
        if self.__appId == value:
            return
        self.__appId = value
        self.appIdChanged.emit()

    @Property(str, notify=versionChanged)
    def version(self):
        return self.__version

    @version.setter
    def version(self, value):
        if self.__version == value:
            return
        self.__version = value
        self.versionChanged.emit()

    @Property(str, notify=localeChanged)
    def locale(self):
        return self.__locale

    @locale.setter
    def locale(self, value):
        if self.__locale == value:
            return
        self.__locale = value
        self.localeChanged.emit()

    @Property(list, notify=localesChanged)
    def locales(self):
        return self.__locales

    @locales.setter
    def locales(self, value):
        if self.__locales == value:
            return
        self.__locales = value
        self.localesChanged.emit()

    def init(self, engine: QQmlApplicationEngine):
        self.__init_translator()

        engine.setBaseUrl("qrc:/qt/qml/Gallery/")

    def __init_translator(self):
        if self.__translator.load(f":/qt/qml/Gallery/Gallery_{self.__locale}.qm"):
            QGuiApplication.installTranslator(self.__translator)
        QLocale.setDefault(QLocale(self.__locale))


__appInfo = None


def AppInfo():
    global __appInfo
    if __appInfo is None:
        __appInfo = __AppInfo()
    return __appInfo
