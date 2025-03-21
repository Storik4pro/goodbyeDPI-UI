import configparser
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import random
import re
import shlex
import shutil
import string
import subprocess
import sys
import time
import traceback

from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from logger import AppLogger
from utils import ProgressToast, background_sound, change_setting, change_settings, check_version, check_winpty, convert_bat_file, create_xml, delete_file, download_blacklist, error_sound, extract_zip, get_component_download_url, get_latest_release, get_download_url, download_update, move_settings_file, open_custom_blacklist, open_folder, pretty_path, register_component, remove_xml, start_process, stop_servise, unregister_component
from _data import BACKUP_SETTINGS_FILE_PATH, BLACKLIST_PROVIDERS, COMPONENTS_URLS, CONFIG_PATH, DEBUG_PATH, EXECUTABLES, LOG_LEVEL, PRESETS, PRESETS_DEFAULT, REPO_NAME, REPO_OWNER, SETTINGS_FILE_PATH, VERSION, Settings, UserConfig, settings, DEBUG, DIRECTORY, configs, text

KEY = 'GOODBYEDPI'
PATH = 'GoodbyeDPI_UI'

logger = AppLogger(VERSION, "QT:Backend", LOG_LEVEL)

class Backend(QObject):
    download_url_ready = Signal(str)  
    download_progress = Signal(float)
    download_finished = Signal(str)
    component_installing_finished = Signal(str)
    language_change = Signal()
    updates_checked = Signal(bool)
    information_requested = Signal(str, 'QVariantList')
    errorHappens = Signal(str, str)

    def __init__(self, first_run=False, parent: QObject | None = ...) -> None:
        super().__init__()
        self.first_run = first_run
        self.process_need_reload = False
        self.last_load_folder = ""
        self.last_preset_used = None

    @Slot(str, result=str)
    def get_element_loc(self, element_name) -> str:
        try:
            return text.inAppText[element_name].replace("{executable}", "%1")
        except:return "<globallocalize."+element_name+">"
        
    @Slot(result=bool)
    def is_debug(self):
        return DEBUG
        
    @Slot(result=str)
    def get_fact(self):
        if not self.first_run:
            facts = tuple(self.get_element_loc(f'fact{i}') for i in range(1, 19))
            random_fact = random.choice(facts)
        else:
            random_fact = self.get_element_loc("first_run_tip")
        
        return random_fact
    
    @Slot(result=bool)
    def get_first_run(self):
        return self.first_run
    
    @Slot(result=list)
    def getComponentsList(self):
        return [
            {
                'key': '/goodbyedpi',
                'title': 'GoodbyeDPI',
                '_icon': f"qrc:/qt/qml/{PATH}/res/image/logo.png",
            },
            {
                'key': '/zapret',
                'title': 'Zapret',
                '_icon': f"qrc:/qt/qml/{PATH}/res/image/zapret.png",
            },
            {
                'key': '/byedpi',
                'title': 'ByeDPI',
                '_icon': f"qrc:/qt/qml/{PATH}/res/image/ByeDPI.png",
            },
            {
                'key': '/spoofdpi',
                'title': 'SpoofDPI',
                '_icon': "",
            },
        ]
        
    @Slot()
    def restart_pc(self):
        try:
            subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
        except subprocess.CalledProcessError as e:
            logger.create_error_log(f"Failed to restart PC: {e}")
            self.errorHappens.emit("Failed to restart PC", "ERR_RESTART_FAILURE")
            
    @Slot(str)
    def save_config_to_bbd(self, filepath):
        config = configs['byedpi']
        bbd_config = {
            "app": "io.github.romanvht.byedpi",
            "apps": [],
            "history": [],
            "settings": {
                "byedpi_cmd_args": config.get_value('custom_parameters'),
                "byedpi_enable_cmd_settings": True,
            },
            "version": f"CDPIUI-{VERSION}"
        }
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(bbd_config, file, ensure_ascii=False, indent=4)
        file.close()
  
    @Slot()
    def share_config_to_bbd(self):
        filepath = Path(DEBUG_PATH+DIRECTORY, 'data', 'share', 'sharedConfig.json')
        str_filepath = str(filepath)
        self.save_config_to_bbd(filepath)
        share_app_path = Path(DEBUG_PATH+DIRECTORY, 'data', 'share')
        share_app_exe = Path(share_app_path, 'WindowsFormsApp2.exe')
        if os.path.exists(share_app_exe):
            start_process(*(str_filepath), path=share_app_exe, cwd=share_app_path)
        else:
            self.errorHappens.emit(
                'Program cannot find WindowsFormsApp2.exe in "data/share/"',
                'ERR_SHARE_FILE_NOT_FOUND'
                )
        
    @Slot(str, result=bool)
    def is_exe_file(self, path:str):
        return os.path.isfile(path) and path.lower().endswith(".exe") and os.path.exists(path)
    
    @Slot(str, result=bool)
    def is_uwp_folder(self, path:str):
        appx_manifest = Path(path, 'AppxManifest.xml')
        return os.path.isdir(path) and os.path.exists(path) and os.path.exists(appx_manifest)
    
    @Slot(str, str, result=bool)
    def load_preset(self, engine, path):
        self.last_preset_used = configs[engine].configfile
        self.last_load_folder = os.path.dirname(path)
        
        if path.endswith(".bat") or path.endswith(".cmd"):
            try:
                path = convert_bat_file(path, DEBUG_PATH+DIRECTORY+"converted", engine)
            except Exception as ex:
                logger.create_error_log(traceback.format_exc())
                self.errorHappens.emit(f"{ex}", "ERR_CONVERT_FAILURE")
                return False
        
        params = self.analyze_custom_parameters(_path=path)
        lists_for_add = []
        for param in params:
            if not os.path.exists(DEBUG_PATH+DIRECTORY+f'data/{engine}/{param["blacklist_name"]}'):
                lists_for_add.append({'blacklist_name':param["blacklist_name"], 'type':'blacklist'})     
        
        custom_params = self.analyze_custom_parameters(_path=path, _mode='custom_params_only')
        
        bins_for_add = re.findall(
            r'(?:\s|^)(?:"|\')?((?:[^\s"\']+|(?<=["\'])[^"\']+)\.bin)(?:"|\')?(?=\s|$)', 
            custom_params
            )

        for i, binfile in enumerate(bins_for_add):
            if not os.path.exists(DEBUG_PATH+DIRECTORY+f'data/{engine}/{binfile}'):
                lists_for_add.append({'blacklist_name':binfile, 'type':'bin'})                
        
        print(">>>>>>>>>>>>>>>>>>>>>>>>\n\n\n"+path)
        try:
            is_bbd = False
            if engine == 'byedpi':
                bbd_config = UserConfig(path)
                filename = os.path.basename(path)
                converted_path = Path(
                    CONFIG_PATH, 'byedpi', 'converted', 
                )
                if not os.path.exists(converted_path):
                    os.makedirs(converted_path)
                
                converted_filepath = Path(
                   converted_path, filename
                )
                is_bbd = bbd_config.get_value('app') == 'io.github.romanvht.byedpi'
                if is_bbd:
                    settings = bbd_config.get_value('settings')['byedpi_cmd_args']
                    byedpi_converted_config = {
                        "custom_parameters":settings
                    }
                    with open(converted_filepath, 'w', encoding='utf-8') as file:
                        json.dump(byedpi_converted_config, 
                                  file, 
                                  ensure_ascii=False, 
                                  indent=4
                        )
                    file.close()
                del bbd_config
                    
            change_setting('CONFIG', 
                           f'{engine.lower()}_config_path', 
                           path if not is_bbd else str(converted_filepath)
            )
            configs[engine].configfile = path if not is_bbd else str(converted_filepath)
            configs[engine].reload_config()
            
            if lists_for_add != []:
                self.information_requested.emit(f"load_preset:{engine}", lists_for_add)
                
            return True
        except Exception as ex:
            self.errorHappens.emit(f"{ex}", "ERR_LOAD_FAILURE")
            change_setting('CONFIG', f'{engine.lower()}_config_path', "")
            return False
          
    @Slot(str, str, result=str)
    def get_load_preset_autocorrect_vars(self, engine, blacklist):
        if os.path.exists(DEBUG_PATH+DIRECTORY+f'data/{engine}/{blacklist}'):
            return ""
        
        blacklist_clear = blacklist.split("\\")[-1]
        if os.path.exists(DEBUG_PATH+DIRECTORY+f'data/{engine}/{blacklist_clear}'):
            return os.path.join(engine, blacklist_clear)
        
        if self.last_load_folder and os.path.exists(os.path.join(self.last_load_folder, blacklist)):
            return os.path.join(self.last_load_folder, blacklist)
        
        return ""    
        
    @Slot(str, str, str, result=str)
    def apply_autocorrect(self, engine, old_blacklist_file, new_blacklist_file:str):
        params = configs[engine].get_value("custom_parameters")
        try:
            convert_folder = convert_folder_name = ''
            if os.path.dirname(new_blacklist_file) != \
               os.path.join(DEBUG_PATH+DIRECTORY, 'data', engine) and \
               (len(new_blacklist_file.split("\\")) < 2 or 
                new_blacklist_file.split("\\")[-2] != engine):
                
                _filename = os.path.basename(
                    configs[engine].configfile).split(".")[0].replace(" ", "_")
                _filename = pretty_path(_filename)
                
                convert_folder_name = f'converted{_filename}'
                
                convert_folder =  os.path.join(DEBUG_PATH+DIRECTORY, 
                                            'data', engine, convert_folder_name)
                
                if not os.path.exists(convert_folder): os.makedirs(convert_folder)
                
                shutil.copyfile(
                    os.path.join(new_blacklist_file), 
                    os.path.join(convert_folder, os.path.basename(new_blacklist_file))
                    )
                
            configs[engine].set_value("custom_parameters", params.replace(
                old_blacklist_file, 
                os.path.join(
                    convert_folder_name, 
                    os.path.basename(new_blacklist_file))))
            configs[engine].reload_config()
            
            return 'True'
        except IOError as ex:
            logger.create_error_log(traceback.format_exc())
            return 'ERR_FILE_WRITE'
        except Exception as ex:
            logger.create_error_log(traceback.format_exc())
            return 'ERR_UNKNOWN'
    
    @Slot(str)
    def return_autocorrect_to_default(self, engine):
        if self.last_preset_used:
            change_setting('CONFIG', f'{engine.lower()}_config_path', self.last_preset_used)
            configs[engine].configfile = self.last_preset_used
            configs[engine].reload_config()
            self.last_preset_used = None
        else:
            self.return_to_default(engine)   
            
    @Slot(str, str, result=bool)
    def create_config(self, engine, params):
        try:
            chkpreset_path = Path(DEBUG_PATH+DIRECTORY, 'chkpreset')
            if not os.path.exists(chkpreset_path):
                os.makedirs(chkpreset_path)
            
            filename = datetime.now().strftime("%H_%M_%S_%d_%m_%Y") + '.json'
            filepath = Path(chkpreset_path, filename)
            
            data = {
                'custom_parameters':params
            }
            
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                file.close()
            else:
                config = UserConfig(filepath)
                config.set_value('custom_parameters', params)
                del config
            
        except IOError:
            self.errorHappens.emit(
                f'Filesystem is damaged or program has no access. '
                'Continuation is impossible.', 
                'ERR_FILE_WRITE'
            )
            logger.create_error_log(traceback.format_exc())
            return False
        except Exception as e:
            self.errorHappens.emit(
                f'Something went wrong. View logs/settings_import.log for more information', 
                'ERR_UNKNOWN'
            )
            logger.create_error_log(traceback.format_exc())
            return False
        return self.load_preset(engine.lower(), str(filepath))
        
    @Slot(str, str)
    def save_preset(self, engine, path):
        configs[engine].copy_to(path)

    @Slot(str)
    def return_to_default(self, engine):
        change_setting('CONFIG', f'{engine.lower()}_config_path', "")
        configs[engine].configfile = CONFIG_PATH+f"/{engine.lower()}/user.json"
        configs[engine].reload_config()
    
    @Slot(str, str, result=str)
    def analyze_params_for_engine(self, engine:str, params:str):
        new_params_list = []
        if engine.lower() == 'byedpi':
            configfile = Path(CONFIG_PATH, 'byedpi', '_supported_params.json')
            config = UserConfig(configfile)
            i = 0
            params_list = params.replace("=", " ").split(' ')
            supported_params = config.get_value('params')
            if len(params_list) < 2:
                return params
            while i < len(params_list):
                if not "-" in params_list[i]:
                    i+=1
                    continue

                if any(params_list[i].startswith(param) for param in supported_params):
                    new_params_list.append(params_list[i])
                    if (
                        "-" in params_list[i] and 
                        i+1 < len(params_list) and 
                        not "-" in params_list[i+1]
                        ):
                        new_params_list.append(params_list[i+1])
                        i+=2
                        continue
                    else:
                        i+=1
                        continue
                else:
                    if (
                        "-" in params_list[i] and 
                        i+1 < len(params_list) and 
                        not "-" in params_list[i+1]
                        ):
                        i+=2
                        continue
                    else:
                        i+=1
                        continue
        return ' '.join(new_params_list)

    @Slot(str, bool, result='QVariantList')
    def analyze_custom_parameters(self, filename=None, unique=True, _path=None, _mode='analyze'):
        path = _path if _path else DEBUG_PATH+CONFIG_PATH+ "/zapret/" + filename + ".json"
        
        if not os.path.exists(path) and filename: path = DEBUG_PATH+CONFIG_PATH+ "/zapret/" + str(int(filename)-1) + ".json"
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        custom_params = data.get("custom_parameters", "")
        
        if _mode == 'custom_params_only': return custom_params

        windows = [window.strip() for window in custom_params.split('--new') if window.strip()]

        blacklists = {} 

        for window in windows:
            tokens = shlex.split(window, posix=False)

            i = 0
            found_blacklist = False
            while i < len(tokens):
                if tokens[i] == '--hostlist' and i + 1 < len(tokens):
                    blacklist_type = 'blacklist'
                    blacklist_name = tokens[i + 1]
                    index = i
                    i += 2
                    found_blacklist = True
                elif tokens[i] == '--ipset' and i + 1 < len(tokens):
                    blacklist_type = 'iplist'
                    blacklist_name = tokens[i + 1]
                    index = i
                    i += 2
                    found_blacklist = True
                elif tokens[i] == '--hostlist-auto' and i + 1 < len(tokens):
                    blacklist_type = 'autoblacklist'
                    blacklist_name = tokens[i + 1]
                    index = i
                    i += 2
                    found_blacklist = True
                else:
                    i += 1
                    continue
                if i < len(tokens) and tokens[i] in ['--hostlist', '--ipset', '--hostlist-auto'] and not unique:
                    blacklist_name += " + " + tokens[i + 1]
                    i += 2
                    found_blacklist = True
                    
                values_before = ' '.join(tokens[:index])
                values_after = ' '.join(tokens[index + 2:])

                window_params = {
                    'values_before': values_before,
                    'values_after': values_after,
                    'full_args': window.strip()
                }

                key = (blacklist_name, blacklist_type)

                if key not in blacklists:
                    blacklists[key] = {
                        'blacklist_name': blacklist_name,
                        'type': blacklist_type,
                        'windows': [window_params]
                    }
                else:
                    blacklists[key]['windows'].append(window_params)
                    
            if not found_blacklist and not unique:
                window_params = {
                    'values_before': "",
                    'values_after': "",
                    'full_args': window.strip()
                }
                key = ("", "NULL")

                if key not in blacklists:
                    blacklists[key] = {
                        'blacklist_name': "",
                        'type': "NULL",
                        'windows': [window_params]
                    }
                else:
                    blacklists[key]['windows'].append(window_params)

                continue
        unique_entries = []
        for idx, ((blacklist_name, blacklist_type), data) in enumerate(blacklists.items()):
            data['componentId'] = idx
            unique_entries.append(data)


        return unique_entries
    
    @Slot(str, 'QVariantList')
    def save_custom_parameters(self, filename:str, updated_data):
        json_file_path = CONFIG_PATH + "/zapret/" + filename + ".json"

        custom_parameters_list = []
        for item in updated_data:
            custom_parameters_list.append(item['args'])

        custom_parameters = ' --new '.join(custom_parameters_list)

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        data['custom_parameters'] = custom_parameters.strip()

        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
    @Slot()
    def play_sound(self):
        error_sound()

    @Slot()
    def play_sound_grab(self):
        background_sound()
    
    @Slot(str, str, result=str)
    def getBackupValue(self, group, key):
        try:
            return Settings(BACKUP_SETTINGS_FILE_PATH).get_value(group, key)
        except:
            return settings.get_value(group, key)
    
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
        return value
    
    @Slot(str, str, bool)  
    def toggleBool(self, key, setting, value):
        change_setting(key, setting, str(value))

    @Slot()
    def changeLanguage(self):
        if text.selectLanguage != settings.settings['GLOBAL']['language']:
            settings.reload_settings()
            text.reload_text()
            self.language_change.emit() 

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
        _value = str(configs[config.lower()].get_value(key.lower()))
        if _value != 'None': return _value
        else: return "" 
        
    @Slot(str, str, result=int)
    def get_int_from_config(self, config, key:str):
        _value = int(configs[config.lower()].get_value(key.lower()))
        if _value: return _value
        else: return 0
    
    @Slot(str, str, result=bool)
    def get_bool_from_config(self, config, key:str):
        _value = configs[config.lower()].get_value(key.lower())
        if _value is not None: return _value
        else: return False
        
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
        
    @Slot(str, str)
    def edit_blacklist(self, component, file):
        os.startfile(DEBUG_PATH + f"{DIRECTORY}/data/{component}/{file}")
    
    @Slot(str)  
    def update_list(self, component):
        progress_toast = ProgressToast('GoodbyeDPI_app', text.inAppText['update_in_process'], text.inAppText['update_in_process_info'] + f"\n[{component}]", 'russia_blacklist.txt')
        try:
            download_blacklist(BLACKLIST_PROVIDERS[self.getValue('GLOBAL', 'blacklist_provider')], progress_toast, 
                               local_filename=DEBUG_PATH+DIRECTORY+f"data/{component}/russia-blacklist.txt")
        except Exception as ex:
            logger.raise_warning(traceback.format_exc())
    
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
        return f"qrc:/qt/qml/{PATH}/res/image/logo.png" 

    # Opening Utils
    @Slot(result=str)
    def get_GDPI_version(self):
        return check_version()

    @Slot()
    def open_chkpreset(self):
        print('OPEN_CHKPRESET')

    @Slot(result=bool)
    def check_winpty(self):
        return check_winpty()

    @Slot()
    def add_to_autorun(self):
        try:
            task_name = "GoodbyeDPI_UI_Autostart"
            executable = sys.executable
            arguments = '--autorun'

            temp_xml_path = create_xml("GoodbyeDPI UI", executable, arguments)
            
            command = [
                'schtasks', '/create',
                '/tn', task_name,
                '/xml', temp_xml_path,
                '/f'
            ]

            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False
            )

            remove_xml(temp_xml_path)
            
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE_PATH, encoding='utf-8')
            config['GLOBAL']['autorun'] = 'True'
            with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            settings.reload_settings()
            self.autorun = True

        except subprocess.CalledProcessError as ex:
            error_output = str(ex.stdout.decode('cp866', errors='replace'))
            logger.raise_warning(text.inAppText['autorun_error'] + "\n" + error_output)
        except Exception as ex:
            error_output = traceback.format_exc()
            logger.raise_warning(error_output)
    @Slot()
    def remove_from_autorun(self):
        try:
            task_name = "GoodbyeDPI_UI_Autostart"

            command = f'schtasks /delete /tn "{task_name}" /f'

            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False
            )
            
            config = configparser.ConfigParser()
            config.read(SETTINGS_FILE_PATH, encoding='utf-8')
            config['GLOBAL']['autorun'] = 'False'
            with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            settings.reload_settings()
            self.autorun = False

        except subprocess.CalledProcessError as ex:
            error_output = str(ex.stdout.decode('cp866', errors='replace'))
            logger.raise_warning(text.inAppText['autorun_error'] + "\n" + error_output)

        except Exception as ex:
            error_output = traceback.format_exc()
            logger.raise_warning(error_output)

    @Slot()
    def _update(self):
        if not DEBUG:
            move_settings_file(SETTINGS_FILE_PATH, BACKUP_SETTINGS_FILE_PATH)
            subprocess.Popen(f'update.exe -directory-to-unpack "'+ DIRECTORY.replace("_internal/", "") + \
                '" -directory-to-zip "' + DIRECTORY + "_portable.zip" + \
                '" -localize ' + settings.settings['GLOBAL']['language'])

    @Slot()
    def changeMode(self):
        if settings.settings['APPEARANCE_MODE']["mode"] == 'dark':
            ch = 'light'
        else:
            ch = 'dark'
        change_setting('APPEARANCE_MODE', 'mode', ch)

    @Slot(result=bool)
    def check_updates(self):
        updates_availible = False
        try:
            if settings.settings['GLOBAL']['notifyaboutupdates'] == "True":
                version_to_update = get_latest_release()
                if "ERR" in version_to_update:
                    return False
                updates_availible = True if VERSION != version_to_update else False
                change_setting('GLOBAL', 'lastcheckedtime', datetime.now().strftime("%H:%M %d.%m.%Y"))
                if updates_availible: 
                    change_setting('GLOBAL', 'version_to_update', version_to_update)
                    change_setting('GLOBAL', 'updatesavailable', "True")
                else:
                    change_setting('GLOBAL', 'updatesavailable', "False")
                    change_setting('GLOBAL', 'version_to_update', "")

        except Exception as ex:
            print(ex)
            return False
        return updates_availible
    
    @Slot(str)
    def open_folder(self, folder_name):
        if not os.path.exists(folder_name):
            open_folder(os.path.join(DEBUG_PATH+DIRECTORY, 'data', folder_name))
        else:
            open_folder(folder_name)

    @Slot(str)
    def open_component_folder(self, component_name:str):
        open_folder((DIRECTORY if not DEBUG else DEBUG_PATH)+\
                    f'data/'+('goodbyeDPI' if component_name == 'goodbyedpi' else component_name))
    
    @Slot(str, result=list)
    def get_presets(self, component_name):
        folder_path = CONFIG_PATH+f"/{component_name}"

        presets_list = []
        standard_presets = []
        loaded_presets = []

        files = os.listdir(folder_path)

        json_files = [f for f in files if f.endswith('.json') and f[:-5].isdigit()]

        json_files.sort(key=lambda x: int(x[:-5]))
        d1 = ''
        n = 0
        for file_name in json_files:
            number = int(file_name[:-5])
            description = self.get_element_loc(PRESETS[component_name].format(i = number))
            if not "<globallocalize." in description:
                if d1 == description:
                    n += 1
                    description += " ("+ self.get_element_loc("alt") + " №"+ str(n) + ") "
                else: n = 0
                if number == PRESETS_DEFAULT[component_name]:
                    description += " ("+ self.get_element_loc("default") + ") "    
                standard_presets.append(f"{number}. {description}")
            else:
                loaded_presets.append(f"{number}. {self.get_element_loc('loaded_tip')} {number}")
            d1 = description.split(" (")[0]

        if standard_presets:
            presets_list.append(f"<separator>{self.get_element_loc('standart').upper()}")
            presets_list.extend(standard_presets)

        if loaded_presets:
            presets_list.append(f"<separator>{self.get_element_loc('loaded').upper()}")
            presets_list.extend(loaded_presets)

        return presets_list
    
    @Slot()
    def start_check_component_updates(self):
        self.thread = QThread()
        self.worker = UpdateCheckerWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.check_updates)
        self.worker.finished.connect(self.updates_checked)
        self.worker.progress.connect(self.on_update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


    def on_update_progress(self, value):
        pass
    
    @Slot(str, result=str)
    def check_component_version(self, component_name):
        return self.getValue("COMPONENTS", component_name+"_server_version")

    @Slot(str, result=str)
    def remove_component(self, component_name:str):
        component_name = 'goodbyeDPI' if component_name == 'goodbyedpi' else component_name
        directory = os.path.join('E:/_component/' if DEBUG else settings.settings['GLOBAL']['work_directory']+f'data', component_name)
        print(directory)
        result = delete_file(directory)
        if result: return result
        return unregister_component(component_name)
    
    @Slot(str)
    def _component_installing_finished(self, result):
        if self.process_need_reload and result == 'True':
            self.process_need_reload = False
            self.component_installing_finished.emit("reload_need")
        else:
            self.process_need_reload = False
            self.component_installing_finished.emit(result)

    @Slot(str, bool)
    def download_component(self, component_name:str, process_need_reload:bool = False):
        self.process_need_reload = process_need_reload
        
        self.qthread = QThread()
        self.worker = DownloadComponent(component_name)
        self.worker.moveToThread(self.qthread)

        self.qthread.started.connect(self.worker.run)
        self.worker.downloadFinished.connect(self._component_installing_finished)
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
    
class UpdateCheckerWorker(QObject):
    finished = Signal(bool)
    progress = Signal(int)

    def __init__(self, parent=None):
        super().__init__()

    def check_updates(self):
        update_available = False
        settings.settings['GLOBAL']["check_complete"] = 'True'
        try:
            total_components = len(COMPONENTS_URLS)
            for i, component_name in enumerate(COMPONENTS_URLS):
                c = component_name.lower()
                if not settings.settings.getboolean('COMPONENTS', c):
                    continue
                if settings.get_value("COMPONENTS", c+"_version").replace("v", "") != \
                        settings.get_value("COMPONENTS", c+"_server_version").replace("v", ""):
                    update_available = True
                    continue
                try:
                    pre_url = get_component_download_url(component_name)
                    url = pre_url.split("|")[0]
                    if url == "ERR_LATEST_VERSION_ALREADY_INSTALLED":
                        continue
                    print(url)
                    version = pre_url.split("|")[1]

                    if settings.get_value("COMPONENTS", c+"_version").replace("v", "") != version:
                        settings.settings["COMPONENTS"][c+"_server_version"] = version
                except Exception as ex:
                    print(ex)
                    settings.settings['GLOBAL']["check_complete"] = "False"

                if settings.get_value("COMPONENTS", c+"_version").replace("v", "") != \
                        settings.get_value("COMPONENTS", c+"_server_version").replace("v", ""):
                    update_available = True

                self.progress.emit(int((i + 1) / total_components * 100))

            settings.save_settings()
            self.finished.emit(update_available)
        except Exception as ex:
            settings.settings['GLOBAL']["check_complete"] = 'False'
            settings.save_settings()
            self.finished.emit(False)

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

        version = get_latest_release(reason='manual')
        if "ERR" in version:
            return 'false'

        time.sleep(5)
        
        if DEBUG:
            return version
        
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

    def __init__(self, component_name:str, url:str = None) -> None:
        super().__init__()
        self.component_name = 'goodbyeDPI' if component_name == 'goodbyedpi' else component_name
        self.url = url
    
    def run(self):
        success = self._download_component()
        self.downloadFinished.emit(success)
        self.workFinished.emit()

    def _download_component(self):
        import requests
        try:
            if self.url is None: self.url = get_component_download_url(self.component_name)

            url = self.url.split("|")[0]
            if "ERR" in url:
                return url
            version = self.url.split("|")[1]
        except Exception as ex:
            return 'ERR_INVALID_SERVER_RESPONSE'
        
        filename = 'unknown_component.zip' if url.endswith(".zip") else\
                   EXECUTABLES[self.component_name]
        _dir = 'E:/_component/' if DEBUG else settings.settings['GLOBAL']['work_directory']+f'data/{self.component_name}'
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        directory = os.path.join(_dir, filename)

        
        
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

                result = register_component(self.component_name, version)
                if result: return result
            elif filename.endswith(".exe"):
                if not DEBUG: stop_servise()
                result = register_component(self.component_name, version)
                if result: return result
            print("END")

        except requests.ConnectionError:
            return 'ERR_CONNECTION_LOST'
        except IOError:
            return 'ERR_FILE_WRITE'
        except Exception as ex:
            return 'ERR_UNKNOWN'

        return 'True'  