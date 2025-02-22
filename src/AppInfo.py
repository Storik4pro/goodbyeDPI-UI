import GlobalConfig
from PySide6.QtCore import Property, QLocale, QObject, QTranslator, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlNamedElement, QmlSingleton, QQmlApplicationEngine

from Helper.SettingsHelper import SettingsHelper


QML_IMPORT_NAME = "GoodbyeDPI_UI"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlNamedElement("AppInfo")
@QmlSingleton
class __AppInfo(QObject):
    version_changed = Signal()
    locale_changed = Signal()
    locales_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__version = GlobalConfig.application_version
        self.__locales = ["en_US", "zh_CN"]
        self.__locale = SettingsHelper().getLocale()
        self.__translator = QTranslator()

    @Property(str, notify=version_changed)
    def version(self):
        return self.__version

    @version.setter
    def version(self, value):
        if self.__version == value:
            return
        self.__version = value
        self.version_changed.emit()

    @Property(str, notify=locale_changed)
    def locale(self):
        return self.__locale

    @locale.setter
    def locale(self, value):
        if self.__locale == value:
            return
        self.__locale = value
        self.locale_changed.emit()

    @Property(list, notify=locales_changed)
    def locales(self):
        return self.__locales

    @locales.setter
    def locales(self, value):
        if self.__locales == value:
            return
        self.__locales = value
        self.locales_changed.emit()

    def init(self, engine: QQmlApplicationEngine):
        self.__init_translator()
        if "ON" == GlobalConfig.build_hotreload:
            engine.setBaseUrl(f"file:///{GlobalConfig.build_project_path}/")
        else:
            engine.setBaseUrl("qrc:/qt/qml/GoodbyeDPI_UI/")

    def __init_translator(self):
        if self.__translator.load(
            f":/qt/qml/GoodbyeDPI_UI/GoodbyeDPI_UI_{self.__locale}.qm",
        ):
            QGuiApplication.installTranslator(self.__translator)
        QLocale.setDefault(QLocale(self.__locale))


__appInfo = None  # noqa: N816


def AppInfo():  # noqa: N802
    global __appInfo
    if __appInfo is None:
        __appInfo = __AppInfo()
    return __appInfo  # noqa: R504
