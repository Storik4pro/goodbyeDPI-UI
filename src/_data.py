import configparser
import os
import sys

DEBUG = False

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

DIRECTORY = f'{application_path}/' if not DEBUG else ''

VERSION = "1.1.0"

SETTINGS_FILE_PATH = DIRECTORY+'data/settings/settings.ini'
BACKUP_SETTINGS_FILE_PATH = DIRECTORY+'data/settings/_settings.ini'
LOCALE_FILE_PATH =  DIRECTORY+'data/loc/loc.ini'
GOODBYE_DPI_PATH =  DIRECTORY+'data/goodbyeDPI/'
FONT = 'Nunito SemiBold'

PARAMETER_MAPPING = {
    'blockpassivedpi': '-p',
    'blockquic': '-q',
    'replacehost': '-r',
    'removespace': '-s',
    'mixhostcase': '-m',
    'donotwaitack': '-n',
    'additionalspace': '-a',
    'processallports': '-w',
    'allownosni': '--allow-no-sni',
    'dnsverbose': '--dns-verb',
    'wrongchecksum': '--wrong-chksum',
    'wrongseq': '--wrong-seq',
    'nativefrag': '--native-frag',
    'reversefrag': '--reverse-frag',
    'blacklist': '--blacklist',
}
VALUE_PARAMETERS = {
    'dns': '--dns-addr',
    'dns_port': '--dns-port',
    'dnsv6': '--dnsv6-addr',
    'dnsv6_port': '--dnsv6-port',
    'httpfragmentation': '-f',
    'httpkeepalive': '-k',
    'httpsfragmentation': '-e',
    'maxpayload': '--max-payload',
    'additionalport': '--port',
    'ipid': '--ip-id',
    'fakefromhex': '--fake-from-hex',
    'fakegen': '--fake-gen',
    'fakeresend': '--fake-resend',
    'autottl': '--auto-ttl',
    'minttl': '--min-ttl',
    'setttl': '--set-ttl',
        
}


REPO_OWNER = "Storik4pro"
REPO_NAME = "goodbyeDPI-UI"

class Settings:
    def __init__(self) -> None:
        self.settings = self.reload_settings()
    
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

