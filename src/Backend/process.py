import os
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from utils import GoodbyedpiProcess, change_setting, get_locale, get_preset_parameters, error_sound, stop_servise
from _data import EXECUTABLES, configs, settings, text, CONFIG_PATH, PARAMETER_MAPPING, VALUE_PARAMETERS, S_PARAMETER_MAPPING, S_VALUE_PARAMETERS

def get_parameter_mappings(engine_name):
    parameter_mappings = {
        'goodbyedpi': (PARAMETER_MAPPING, VALUE_PARAMETERS),
        'zapret': (None, None),
        'byedpi': (None, None),
        'spoofdpi': (S_PARAMETER_MAPPING, S_VALUE_PARAMETERS),
    }
    return parameter_mappings.get(engine_name, ({}, {}))

def build_command_from_config(engine_name, parameter_mapping, value_parameters):
    command = []
    configs[engine_name].reload_config()
    params = configs[engine_name].data
    if parameter_mapping:
        for ini_param, cmd_param in parameter_mapping.items():
            if ini_param in params:
                value = configs[engine_name].get_value(ini_param)
                if value:
                    value_key = f"{ini_param}_value"
                    if ini_param in value_parameters and value_key in params:
                        param_value = params[value_key]
                        if isinstance(param_value, str):
                            param_value = param_value.strip()
                        if param_value:
                            command.append(cmd_param)
                            command.append(param_value)
                    else:
                        command.append(cmd_param)
    if value_parameters:
        for ini_param, cmd_param in value_parameters.items():
            if ini_param in params:
                value = configs[engine_name].get_value(ini_param)
                value_key = f"{ini_param}_value"
                if value and value_key in params:
                    param_value = params[value_key]
                    if isinstance(param_value, str):
                        param_value = param_value.strip()
                    if param_value or param_value == 0:
                        command.append(cmd_param)
                        command.append(str(param_value))

    if engine_name == 'goodbyedpi':
        if 'blacklist_value' in params:
            blacklist_value = params['blacklist_value']
            if isinstance(blacklist_value, str):
                blacklist_value = blacklist_value.strip()
            if blacklist_value:
                blacklist_files = blacklist_value.split(",")
                for filePath in blacklist_files:
                    command.append('--blacklist')
                    command.append(str(filePath).strip('"'))

    if 'custom_parameters' in params:
        custom_params = params['custom_parameters']
        if custom_params:
            custom_params_list = [param.strip() for param in custom_params.split(' ') if param.strip()]
            command.extend(custom_params_list)

    return command

def check_args(preset):
    engine = settings.settings['GLOBAL']['engine'].lower()
    cfg = settings.settings['CONFIG'].get(f'{engine}_config_path', '')
    if cfg != "" and os.path.exists(cfg) and configs[engine].configfile != cfg:
        configs[engine].configfile = cfg
    else:
        configs[engine].configfile = CONFIG_PATH + f"/{engine}/user.json"
    configs[engine].reload_config()

    
    if engine == 'goodbyedpi':
        advanced_mode_setting = settings.settings.getboolean('GLOBAL', 'use_advanced_mode')
        if advanced_mode_setting and preset != -1:
            advanced_mode_setting = False
    else:
        advanced_mode_setting = settings.settings.getboolean(engine.upper(), 'use_advanced_mode')
        
    if advanced_mode_setting or engine == 'spoofdpi':
        parameter_mapping, value_parameters = get_parameter_mappings(engine)
        command = build_command_from_config(engine, parameter_mapping, value_parameters)
        return command
    else:
        preset = int(settings.settings[engine.upper()].get('preset', -1)) if preset == -1 else preset
        command = get_preset_parameters(preset, engine)

        if engine == 'goodbyedpi':
            if settings.settings['GLOBAL'].get('change_dns') == 'True':
                dns_prompt = [
                    VALUE_PARAMETERS['dns'], settings.settings['GOODBYEDPI']['dns_value'],
                    VALUE_PARAMETERS['dns_port'], settings.settings['GOODBYEDPI']['dns_port_value'],
                    VALUE_PARAMETERS['dnsv6'], settings.settings['GOODBYEDPI']['dnsv6_value'],
                    VALUE_PARAMETERS['dnsv6_port'], settings.settings['GOODBYEDPI']['dnsv6_port_value']
                ]
                command.extend(dns_prompt)
            if settings.settings['GOODBYEDPI'].get('use_blacklist') == 'True':
                command.extend(['--blacklist', '..//russia-blacklist.txt'])
            if settings.settings['GOODBYEDPI'].get('use_blacklist_custom') == 'True':
                command.extend(['--blacklist', '..//custom_blacklist.txt'])
        return command
    
def get_preset_name(engine, presetId):
    _additional = None
    additional = ""
    if engine == 'goodbyeDPI':
        if presetId == 9:
            _additional = "default"
        elif presetId == 10:
            _additional = "recommended"
        elif presetId == 11:
            _additional = "alt"
        
        if _additional:
            additional = f" ({get_locale(_additional)})" 
            
        return f"{presetId}. "+ get_locale(f"preset_{presetId}") + additional
    elif engine == 'zapret':
        if presetId == 3:
            _additional = "recommended"
        elif presetId == 4:
            _additional = "alt"
        
        if _additional:
            additional = f" ({get_locale(_additional)})" 
        
        return f"{presetId}. "+ get_locale(f"qpreset_{presetId}") + additional
    
    elif engine == 'byedpi':
        return f"{presetId}. "+ "("+get_locale(f"default") + ")"
    
def get_engine_preset(engine:str):
    if engine == 'goodbyeDPI':
        advanced_mode_setting = settings.settings.getboolean('GLOBAL', 'use_advanced_mode')
    else:
        advanced_mode_setting = settings.settings.getboolean(engine.upper(), 'use_advanced_mode')
    
    cfg = settings.settings.get('CONFIG', f'{engine.lower()}_config_path')
    if cfg != "" and os.path.exists(cfg) and advanced_mode_setting:
        return f"User config - \"{cfg.split('/')[-1]}\""

    else:
        if advanced_mode_setting or engine == 'spoofdpi':
            return "Custom - \"user.json\""
        elif not advanced_mode_setting:
            return get_preset_name(engine, settings.settings.getint(f'{engine.upper()}', "preset"))
    print(engine)
    return "UNKNOWN"

class Process(QObject):
    output_added = Signal(str)
    error_happens = Signal(str)
    process_started = Signal(bool)
    process_stopped = Signal(str)
    engine_changed = Signal(str)
    preset_changed = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self.output = ""
        self.engine = settings.settings['GLOBAL']['engine']
        self.is_running = False
        self.process = GoodbyedpiProcess()
        self.process.output_signal.connect(self.output_added)
        self.process.output_signal.connect(self.handle_output)
        self.process.process_started.connect(self.handle_process_started)
        self.process.process_stopped.connect(self.handle_process_stopped)
        self.process.error_occurred.connect(self.handle_error)

    @Slot()
    def update_preset(self):
        self.preset_changed.emit()

    @Slot(result=str)
    def get_preset(self):
        return get_engine_preset(self.engine)
    
    @Slot(str, result=str)
    def get_config_name(self, component):
        return configs[component].configfile

    @Slot(result=str)
    def get_executable(self):
        return EXECUTABLES[self.engine]
    
    @Slot(str)
    def change_engine(self, engine):
        change_setting("GLOBAL", "engine", engine)
        if not self.is_running:
            self.engine = engine
            self.engine_changed.emit(self.engine)
            self.preset_changed.emit()

    @Slot(result=bool)
    def is_process_alive(self):
        return self.is_running

    @Slot(result=bool)
    def start_process(self):
        self.engine = settings.settings['GLOBAL']['engine']
        self.engine_changed.emit(self.engine)
        self.preset_changed.emit()

        self.output = ""
        try:
            args = check_args(-1)
        except Exception as ex:
            error_sound()
            self.handle_error(f"Internal error. Unable to start process. \nError information: \n{ex}")
            return False
        print(args)
        self.is_running = True
        return self.process.start_goodbyedpi(*args)

    @Slot(result=bool)
    def stop_process(self):
        self.is_running = False
        self.process.stop_goodbyedpi()
        return True
    
    @Slot()
    def stop_service(self):
        self.is_running = False
        self.process.stop_goodbyedpi()
        stop_servise()
    
    @Slot(result=str)
    def get_output(self):
        return self.output

    def handle_output(self, data):
        self.output += data

    def handle_process_started(self):
        self.engine = settings.settings['GLOBAL']['engine']

        self.engine_changed.emit(self.engine)
        self.preset_changed.emit()
        self.process_started.emit(True)

        self.is_running = True
        print("Process started.")

    def handle_process_stopped(self, reason):
        print(reason)
        self.is_running = False
        self.process_stopped.emit(reason)
        print("Process stopped.")

    def handle_error(self, error_message):
        self.is_running = False
        self.output += ("\n\n[ERROR] " + error_message + "\n\n")
        self.error_happens.emit(error_message)