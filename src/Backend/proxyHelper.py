import ctypes
import glob
import os
from pathlib import Path
import shutil
import subprocess
import time
import traceback
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap, QImage
from PySide6.QtQml import QQmlApplicationEngine
import xml.etree.ElementTree as ET
import win32com.client
import win32ui
import win32gui
import winreg
import re
from _data import DIRECTORY, DEBUG_PATH, DEBUG, PROXIFYRE_CONFIG_PATH, PROXIFYRE_URLS, \
                  PROXIFYRE_VERSIONS, logger, text, settings, UserConfig
from utils import check_proxifyre_install, delete_file, download_update, extract_zip, get_download_url, save_proxy_settings

registry_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"



def get_proxy_settings(signal:Signal=None):
    settings = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)

        proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
        settings["ProxyEnable"] = proxy_enable

        try:
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
            settings["ProxyServer"] = proxy_server
        except FileNotFoundError:
            settings["ProxyServer"] = None

        try:
            proxy_override, _ = winreg.QueryValueEx(key, "ProxyOverride")
            settings["ProxyOverride"] = proxy_override
        except FileNotFoundError:
            settings["ProxyOverride"] = None  
        
        winreg.CloseKey(key)
    except Exception as e:
        signal.emit(
            text.safe_get('reg_read_error').format(f"HKEY_CURRENT_USER/{registry_path}"), 
            "ERR_REGISTRY_READ"
        )
        return None

    return settings

def get_icon_from_exe(exe_path):
    if exe_path.lower().endswith(".exe"):
        try:
            large, small = win32gui.ExtractIconEx(exe_path, 0)
        except Exception as e:
            return None
        if large:
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, 32, 32)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)
            hdc.DrawIcon((0, 0), large[0])
            win32gui.DestroyIcon(large[0])

            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)
            image = QImage(bmpstr, bmpinfo['bmWidth'], bmpinfo['bmHeight'], QImage.Format_ARGB32)
            
            icon = QPixmap.fromImage(image)
            return icon
    else:
        try:
            package_path = Path(exe_path)
            manifest_path = package_path / "AppxManifest.xml"
            if not manifest_path.exists():
                return None

            tree = ET.parse(manifest_path)
            root = tree.getroot()
            namespace = {
                '': 'http://schemas.microsoft.com/appx/manifest/foundation/windows10',
                'uap': 'http://schemas.microsoft.com/appx/manifest/uap/windows10'
            }
            visual_elements = root.find('.//uap:VisualElements', namespace)
            if visual_elements is not None:
                icon_path = visual_elements.get('Square44x44Logo')
                if icon_path:
                    icon_path = package_path / icon_path.replace('\\', '/')
                    if icon_path.exists():
                        image = QImage(str(icon_path))
                        icon = QPixmap.fromImage(image)
                        return icon
                    else:
                        icon_path = str(icon_path).replace('.png', '.*.png')
                        icons = glob.glob(icon_path)
                        if icons:
                            image = QImage(str(icons[0]))
                            icon = QPixmap.fromImage(image)
                            return icon
                        
        except Exception as e:
            return None
    return None

def get_apps_from_shell_apps_folder(imageProvider):
    shell = win32com.client.Dispatch("Shell.Application")
    apps_folder = shell.Namespace("shell:AppsFolder")
    
    apps = []
    for item in apps_folder.Items():
        display_name = apps_folder.GetDetailsOf(item, 0)
        short_name = apps_folder.GetDetailsOf(item, 1)
        
        exe_path = None
        try:
            exe_path = item.ExtendedProperty("System.Link.TargetParsingPath")
        except Exception:
            exe_path = None
            
        exe_name = None
        if exe_path:
            parts = exe_path.split("\\")
            if len(parts) > 1:
                exe_name = parts[-1].split(".")[0]
        
        if not exe_path:
            app_id = None
            try:
                app_id = item.ExtendedProperty("System.AppUserModel.ID")
            except Exception:
                pass
            if app_id:
                parts = app_id.split("!")
                if len(parts) > 1:
                    base_path = Path("C:\\", "Program Files", "WindowsApps")
                    app_foder = parts[0].split("_")
                    if len(app_foder) > 1:
                        app_foder = app_foder[0] + "_*_x64__" + app_foder[1]
                        exe_path = os.path.join(base_path, app_foder)
                        folders = glob.glob(exe_path)
                        if folders:
                            exe_path = folders[0]
                        else:
                            app_foder = parts[0].split("_")
                            if len(app_foder) > 1:
                                app_foder = app_foder[0] + "_*_" + app_foder[1]
                                exe_path = os.path.join(base_path, app_foder)
                                _folders = glob.glob(exe_path)
                                if _folders:
                                    exe_path = _folders[0]
                if exe_path:    
                    if os.path.exists(exe_path):
                        exe_name = exe_path
            
        if display_name.startswith("http"):
            continue
        
        icon = None
        
        apps.append({
            "display_name": short_name,
            "exe": exe_path,
            "exe_name": exe_name,
            "icon": icon,
            "checked": False
        })
        
        try:
            imageProvider.preloadPixmap(exe_path)
        except:
            pass
        
    return apps

def after_install_proxifyre_action() -> UserConfig:
    if not os.path.exists(PROXIFYRE_CONFIG_PATH):
        os.makedirs(DEBUG_PATH+DIRECTORY+'data/proxifyre', exist_ok=True)
        with open(DEBUG_PATH+PROXIFYRE_CONFIG_PATH, "w") as f:
            f.write("{}")
            
        config = UserConfig(PROXIFYRE_CONFIG_PATH)
        config.set_value("logLevel", "INFO")
        config.set_value("proxies", [CONFIG_EXAMPLE,])
        
    else:
        config = UserConfig(PROXIFYRE_CONFIG_PATH)
    return config

CONFIG_EXAMPLE = {
    "appNames": [],
    "socks5ProxyEndpoint": "127.0.0.1:1080",
    "supportedProtocols": ["TCP", "UDP"],
}

MODE_MAPPING = {
    ('UDP', 'TCP'): 0,
    ('UDP',): 1,
    ('TCP',): 2
}





class AppsLoader(QObject):
    finished = Signal(list)
    errorHappens = Signal(str, str)
    
    def __init__(self, imageProvider):
        super().__init__()
        self.imageProvider = imageProvider
    
    @Slot()
    def run(self):
        try:
            apps = get_apps_from_shell_apps_folder(self.imageProvider)
        except Exception as e:
            self.errorHappens.emit(str(e), "ERR_GET_APPS")
            apps = []
        self.finished.emit(apps)


class ProxyHelper(QObject):
    appsLoaded = Signal(list)
    progressChanged = Signal(float)
    stateChanged = Signal(str)
    downloadFinished = Signal(str)
    errorHappens = Signal(str, str)
    openProxySettings = Signal()
    proxyTypeChanged = Signal()
    
    def __init__(self, imageProvider):
        super().__init__()
        self.apps_list = []
        self.config = after_install_proxifyre_action()
        
        self.settings = None
        self.settingsLoadedError = False

        self.imageProvider = imageProvider
        
    @Slot()
    def proxyTypeChange(self):
        self.proxyTypeChanged.emit()
        
    @Slot()
    def open_setup(self):
        self.openProxySettings.emit()
    
    @Slot()
    def get_apps(self):
        if not self.apps_list:
            self.thread = QThread()
            self.worker = AppsLoader(self.imageProvider)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.errorHappens.connect(self.errorHappens)
            self.worker.finished.connect(self.on_apps_loaded)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
        else:
            self.on_apps_loaded(self.apps_list)
            

    @Slot()
    def on_apps_loaded(self, apps):
        self.apps_list = apps
        app_names = self.config.get_value("proxies")[0]['appNames']
        existing_app_names = {app['exe_name'] for app in self.apps_list}
        for app in self.apps_list:
            if app['exe_name'] in app_names or app['exe'] in app_names:
                app['checked'] = True
                
            else:
                app['checked'] = False
                
        for app_name in app_names:
            if app_name.lower() not in (name.lower() for name in existing_app_names if name) and \
                app_name.lower() != 'discord':

                self.apps_list.append({
                    "display_name": app_name,
                    "exe": app_name,
                    "exe_name": app_name,
                    "icon": None,
                    "checked": True
                })    
                
        self.appsLoaded.emit(self.apps_list)    
    
    @Slot(str, str)
    def add_app(self, path, name):
        if name in self.config.get_value("proxies")[0]['appNames']:
            return
        
        proxies = self.config.get_value("proxies")
        
        if "discord\\update.exe" in path.lower():
            proxies[0]['appNames'].append('discord')
            name = path
        
        proxies[0]['appNames'].append(name)
        self.config.set_value("proxies", proxies)
        
        for app in self.apps_list:
            if app['exe_name'] in proxies[0]['appNames']:
                app['checked'] = True
                return
        
        self.apps_list.append({
            "display_name": name,
            "exe": path,
            "exe_name": path,
            "icon": None,
            "checked": True
        })
        
    @Slot(str, str)
    def remove_app(self, path, name):
        proxies = self.config.get_value("proxies")
        if name in proxies[0]['appNames'] or path in proxies[0]['appNames']:
            
            if "discord\\update.exe" in path.lower() and 'discord' in proxies[0]['appNames']:
                proxies[0]['appNames'].remove('discord')
                name = path
                
            proxies[0]['appNames'].remove(name)
            self.config.set_value("proxies", proxies)

        for app in self.apps_list:
            if app['exe_name'] in proxies[0]['appNames']:
                app['checked'] = False
    
    @Slot(result=int)
    def get_current_mode(self):
        try:
            proxies = self.config.get_value('proxies')
            proto = proxies[0]['supportedProtocols']
            
            for key, value in MODE_MAPPING.items():
                if all(protocol in proto for protocol in key):
                    return value
        except:
            pass
        return 0
    
    @Slot(int)
    def set_mode(self, mode):
        proxies = self.config.get_value('proxies')
        
        for key, value in MODE_MAPPING.items():
            if mode == value:
                proxies[0]['supportedProtocols'] = key
                
        self.config.set_value("proxies", proxies)
        
    @Slot(str, result=str)
    def get_ip(self, name):
        proxies = self.config.get_value('proxies')
        socks5ProxyEndpoint = proxies[0]['socks5ProxyEndpoint'].split(":")
        if len(socks5ProxyEndpoint) > 2:
            socks5ProxyEndpoint = proxies[0]['socks5ProxyEndpoint'].split("]:")
        if len(socks5ProxyEndpoint) == 1:
            socks5ProxyEndpoint.append("1080")
        
        if name == 'ip':
            return socks5ProxyEndpoint[0].replace("[", '')
        else:
            return socks5ProxyEndpoint[1]
        
    @Slot(str, str)
    def set_ip(self, name, value):
        sep = ':'
        
        proxies = self.config.get_value('proxies')
        socks5ProxyEndpoint = proxies[0]['socks5ProxyEndpoint'].split(":")
        if len(socks5ProxyEndpoint) > 2:
            socks5ProxyEndpoint = proxies[0]['socks5ProxyEndpoint'].split("]:")
            if name == 'port': sep = "]:"
        if len(socks5ProxyEndpoint) == 1:
            socks5ProxyEndpoint.append("1080")
        
        if ":" in value:
            value = f'[{value}]'
        
        if name == 'ip':
            socks5ProxyEndpoint[0] = value
        else:
            socks5ProxyEndpoint[1] = value
            
        proxies[0]['socks5ProxyEndpoint'] = sep.join(socks5ProxyEndpoint)
        
        self.config.set_value("proxies", proxies)
        
    @Slot(str, result=bool)
    def check_ip_addr(self, addr):
        ipv4_result = re.findall(
            r'^\b(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\b$',
            addr
            )
        if ipv4_result != []: 
            return True
        
        if addr == "::":
            return True
        
        ipv6_result = re.findall(
            r'^((?:[A-Fa-f0-9]{1,4}:){1,7}[A-Fa-f0-9]{1,4}|'
            r'(?:[A-Fa-f0-9]{1,4}:){1,7}:|:(:[A-Fa-f0-9]{1,4}){1,7}|'
            r'(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}|'
            r'(?:[A-Fa-f0-9]{1,4}:){1,5}(:[A-Fa-f0-9]{1,4}){1,2}|'
            r'(?:[A-Fa-f0-9]{1,4}:){1,4}(:[A-Fa-f0-9]{1,4}){1,3}|'
            r'(?:[A-Fa-f0-9]{1,4}:){1,3}(:[A-Fa-f0-9]{1,4}){1,4}|'
            r'(?:[A-Fa-f0-9]{1,4}:){1,2}(:[A-Fa-f0-9]{1,4}){1,5}|'
            r'[A-Fa-f0-9]{1,4}:(:[A-Fa-f0-9]{1,4}){1,6}|'
            r'::(?:[A-Fa-f0-9]{1,4}:){0,6}[A-Fa-f0-9]{1,4}|(?:[A-Fa-f0-9]{1,4}:){1,7}:)$',
            addr
            )
        
        if ipv6_result != []:
            return True
    
        return False
    
    @Slot(str, result=bool)
    def check_port(self, port:str):
        if not port.isdigit():
            return False
        
        if 1024 <= int(port) <= 49151:
            return True
        else:
            return False
        
    @Slot()
    def load_proxy_settings(self):
        self.settings = get_proxy_settings(self.errorHappens)
        if self.settings is None:
            self.settingsLoadedError = True
            
        print(self.settings['ProxyEnable'])
        
    @Slot(str, result=str)
    def get_proxy_setting_string(self, key, default=""):
        if self.settings:
            return self.settings.get(key, default)
        else:
            return default
        
    @Slot(str, result=int)
    def get_proxy_setting_int(self, key, default=0):
        if self.settings:
            return self.settings.get(key, default)
        else:
            return default
        
    @Slot(str, str)
    def set_proxy_setting(self, key, value):
        if value.isdigit():
            value = int(value)
        if self.settings:
            self.settings[key] = value
        else:
            self.settings = {key: value}
            
    @Slot()
    def save_proxy_settings(self):
        save_proxy_settings(0, settings=self.settings, signal=self.errorHappens)
            
        
    @Slot(str, result=str)
    def get_version(self, name):
        return PROXIFYRE_VERSIONS[name]
    
    @Slot(result=bool)
    def check_install(self):
        return check_proxifyre_install()
    
    @Slot()
    def uninstall_proxifyre(self):
        directory = os.path.join(DEBUG_PATH+DIRECTORY, 'data', 'proxifyre')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        if settings.settings['PROXY']['proxy_now_used'] == 'proxifyre':
            settings.change_setting('PROXY', 'proxy_now_used', '')
    
    @Slot()
    def download_proxifyre(self):
        self.qthread = QThread()
        self._worker = UpdateDownloadWorker()
        self._worker.moveToThread(self.qthread)

        self.qthread.started.connect(self._worker.run)
        self._worker.downloadFinished.connect(self._downloadFinished)
        self._worker.progressChanged.connect(self.progressChanged)
        self._worker.stateChanged.connect(self.stateChanged)
        self._worker.workFinished.connect(self.qthread.quit)
        self._worker.workFinished.connect(self._worker.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)

        self.qthread.start()
        
    def _downloadFinished(self, out):
        self.config = after_install_proxifyre_action()
        if 'ERR' in out:
            self.uninstall_proxifyre()
            pass
        self.downloadFinished.emit(out)
        
class UpdateDownloadWorker(QObject):
    progressChanged = Signal(float)
    downloadFinished = Signal(str)
    stateChanged = Signal(str)
    workFinished = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        success = self._download_update()
        self.downloadFinished.emit(success)
        self.workFinished.emit()

    def _download_update(self):
        import requests
        self.stateChanged.emit("GETR")
        
        basic_filename = '_proxifyre.zip'
        ndisapi_filename = '_ndisapi.zip'
        ndisapi_msi_filename = '_ndisapi.msi'
        
        directory = os.path.join(DEBUG_PATH+DIRECTORY, 'data', 'proxifyre')
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        basic_url = "https://github.com/" + PROXIFYRE_URLS['basic']
        ndisapi_url = "https://github.com/" + PROXIFYRE_URLS['ndisapi']
        ndisapi_msi_url = "https://github.com/" + PROXIFYRE_URLS['ndisapi_msi']
        
        basic_directory = os.path.join(directory, basic_filename)
        ndisapi_directory = os.path.join(directory, ndisapi_filename)
        ndisapi_msi_directory = os.path.join(directory, ndisapi_msi_filename)
        try:
            # download proxifyre
            self.stateChanged.emit("PRXF_d")
            download_update(basic_url, basic_directory, self.progressChanged, debug_check=False)
            
            # download ndisapi
            self.stateChanged.emit("NDSA_d")
            download_update(ndisapi_url, ndisapi_directory, self.progressChanged, debug_check=False)
            
            # download ndisapi msi
            self.stateChanged.emit("NDSA_MSI_d")
            download_update(ndisapi_msi_url, ndisapi_msi_directory, self.progressChanged, 
                            debug_check=False)
            
            folder_to_unpack = ""
            
            # unpack proxifyre
            self.stateChanged.emit("PRXF_i")
            result = extract_zip(zip_file=basic_directory, zip_folder_to_unpack=folder_to_unpack, 
                                 extract_to=directory)
            if result: return result
            delete_file(file_path=basic_directory)
            
            # unpack ndisapi
            self.stateChanged.emit("NDSA_i")
            result = extract_zip(zip_file=ndisapi_directory, zip_folder_to_unpack=folder_to_unpack, 
                                 extract_to=directory)
            if result: return result
            delete_file(file_path=ndisapi_directory)
            
            # install ndisapi msi
            self.stateChanged.emit("NDSA_MSI_i")

            install_process = subprocess.Popen(
                ['msiexec', '/i', Path(ndisapi_msi_directory), '/passive', '/norestart'], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path(directory)
                )
            
            start_time = time.time()
            while install_process.poll() is None:
                time.sleep(1)
                if time.time() - start_time > 600:
                    install_process.kill()
                    return 'ERR_DRIVER_INSTALL_TIMEOUT'
            
            if install_process.returncode != 0 and install_process.returncode != 1603:
                return f'ERR_DRIVER_INSTALL_FAILED_{install_process.returncode}'
            
            delete_file(file_path=ndisapi_msi_directory)
            
            
        except requests.ConnectionError:
            return 'ERR_CONNECTION_LOST'
        except IOError:
            return 'ERR_FILE_WRITE'
        except requests.exceptions:
            return 'ERR_REQUESTS_UNKNOWN'
        except Exception as ex:
            logger.create_critical_log(traceback.format_exc())
            return 'ERR_UNKNOWN'

        return 'True'     