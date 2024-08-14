import configparser
import os

DEBUG = False

DIRECTORY = f'{os.path.dirname(os.path.abspath(__file__))}/' if not DEBUG else ''

SETTINGS_FILE_PATH = DIRECTORY+'data/settings/settings.ini'
BACKUP_SETTINGS_FILE_PATH = DIRECTORY+'data/settings/_settings.ini'
LOCALE_FILE_PATH =  DIRECTORY+'data/loc/loc.ini'
GOODBYE_DPI_PATH =  DIRECTORY+'data/goodbyeDPI/'
FONT = 'Nunito SemiBold'

REPO_OWNER = "Storik4pro"
REPO_NAME = "goodbyeDPI-UI"

class Settings:
    def __init__(self) -> None:
        self.reload_settings()
    
    def reload_settings(self):
        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE_PATH, encoding='utf-8')
        self.settings = config
        return self.settings
    
settings = Settings()


class Text:
    def __init__(self, language) -> None:
        self.inAppText = {'': ''}
        self.reload_text(language)

    def reload_text(self, language=None):
        self.selectLanguage = language if language else settings.settings['GLOBAL']['language'] 
        config = configparser.ConfigParser()
        config.read(LOCALE_FILE_PATH, encoding='utf-8')
        self.inAppText = config[f'{self.selectLanguage}']

text = Text(settings.settings['GLOBAL']['language'])

