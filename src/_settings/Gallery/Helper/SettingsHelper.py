from PySide6.QtCore import QObject, Slot, QStandardPaths, QSettings
from PySide6.QtQml import QmlSingleton, QmlNamedElement

QML_IMPORT_NAME = "Gallery"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlNamedElement("SettingsHelper")
@QmlSingleton
class __SettingsHelper(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__settings = QSettings()
        ini_file_name = "FluentUI-Gallery.ini"
        ini_file_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation) + "/" + ini_file_name
        self.__settings = QSettings(ini_file_path, QSettings.Format.IniFormat)

    @staticmethod
    def create(_):
        return SettingsHelper()

    def __save(self, key, val):
        self.__settings.setValue(key, val)

    def __get(self, key, default):
        data = self.__settings.value(key)
        if data is None:
            return default
        return data

    @Slot(result=int)
    def getDarkMode(self):
        return int(self.__get("darkMode", 0))

    @Slot(int)
    def saveDarkMode(self, val: int):
        self.__save("darkMode", val)

    @Slot(result=bool)
    def getUseSystemAppBar(self):
        return bool(self.__get('useSystemAppBar', "false") == "true")

    @Slot(bool)
    def saveUseSystemAppBar(self, val: bool):
        self.__save("useSystemAppBar", val)

    @Slot(result=str)
    def getLocale(self):
        return str(self.__get("locale", "en_US"))

    @Slot(str)
    def saveLocale(self, val: str):
        self.__save("locale", val)


__settingsHelper = None


def SettingsHelper():
    global __settingsHelper
    if __settingsHelper is None:
        __settingsHelper = __SettingsHelper()
    return __settingsHelper
