import configparser

SETTINGS_FILE_PATH = 'data/settings/settings.ini'
LOCALE_FILE_PATH = 'data/loc/loc.ini'
GOODBYE_DPI_PATH = 'data/goodbyeDPI/'
FONT = 'Nunito SemiBold'

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

