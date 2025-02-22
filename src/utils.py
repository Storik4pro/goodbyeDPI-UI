# Standard Library imports (sorted alphabetically)
import asyncio
import configparser
import ctypes
from datetime import datetime
import hashlib
import json
import os
import platform
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Literal
import winsound
import zipfile

# Third Party imports (sorted alphabetically)
from _data import (
    COMPONENTS_URLS,
    CONFIG_PATH,
    CONFIGS_REPO_NAME,
    DEBUG,
    DEBUG_PATH,
    DIRECTORY,
    EXECUTABLES,
    GOODBYE_DPI_EXECUTABLE,
    GOODBYE_DPI_PATH,
    PARAMETER_MAPPING,
    REPO_NAME,
    REPO_OWNER,
    S_PARAMETER_MAPPING,
    S_VALUE_PARAMETERS,
    settings,
    SETTINGS_FILE_PATH,
    text,
    VALUE_PARAMETERS,
)
import psutil
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QThread, Signal
import requests
from toasted import (
    Button,
    Image,
    Progress,
    Text,
    Toast,
    ToastButtonStyle,
    ToastImagePlacement,
)
import winreg


def check_winpty():
    version = platform.version()
    major, minor, build = map(int, version.split("."))
    return build >= 17763


winpty_support = check_winpty()


if winpty_support:
    import winpty


def error_sound():
    winsound.MessageBeep(winsound.MB_ICONHAND)


def background_sound():
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)


# PC test
def is_weak_pc():  # ФУНКЦИЯ ПЕРЕПИСЫВАЛАСЬ
    cpu_freq = psutil.cpu_freq().max
    cpu_cores = psutil.cpu_count(logical=False)
    total_memory_gb = psutil.virtual_memory().total / (1024**3)

    low_cpu_freq = 2000
    low_cpu_cores = 2
    low_memory_gb = 4

    weak_cpu = cpu_freq < low_cpu_freq or cpu_cores <= low_cpu_cores
    weak_memory = total_memory_gb <= low_memory_gb

    return weak_cpu or weak_memory


def get_locale(element):
    try:
        return text.inAppText[element]
    except Exception:
        return f"locale:{element}"


# Toast


class ProgressToast:
    def __init__(
        self,
        app_id: str,
        title,
        description,
        filename="sample_file.txt",
    ) -> None:
        self.toast = Toast(
            app_id=app_id,
            arguments="click",
        )
        self.toast.elements = [
            Text(title),
            Text(description),
            Progress(
                value="-1",
                status="{status}",
                title=filename,
                display_value="0% @ 0 MB/s",
            ),
        ]
        self.notification_thread = None
        print(self.toast.elements[2].value)
        self.start_toast(-1, "downloading")

    async def update_toast_tread(self, value, status):
        self.result = await self.toast.show({"status": status, "value": value})
        return self.result

    def start_toast(self, value, status):
        if self.notification_thread is None or not self.notification_thread.is_alive():
            self.notification_thread = threading.Thread(
                target=lambda: asyncio.run(self.update_toast_tread(value, status)),
            )
            self.notification_thread.start()

    def update_toast(self, value, status, body=None, title=None):
        print(value)
        self.toast.elements[2].value = value
        self.toast.elements[2].status = status
        if body:
            self.toast.elements[1].content = body
        if title:
            self.toast.elements[0].content = title


async def show_message(app_id: str, title, description):  # ФУНКЦИЯ ПЕРЕПИСЫВАЛАСЬ
    toast = Toast(app_id=app_id)
    toast.elements = [
        Text(title),
        Text(description),
    ]
    return await toast.show()


async def show_error(
    app_id: str,
    title,
    description,
    btn_text,
    btn_text2,
):  # ФУНКЦИЯ ПЕРЕПИСЫВАЛАСЬ
    toast = Toast(app_id=app_id)
    elements = [
        Image(
            f"file:///{(DIRECTORY if not DEBUG else DEBUG_PATH)+'/data/warning.png'}\
                ?foreground=#FFFFFF&background=#F7630C&padding=40",
            placement=ToastImagePlacement.LOGO,
        ),
        Text(title),
        Text(description),
        Button(btn_text, arguments="accept", style=ToastButtonStyle.CRITICAL),
    ]
    if btn_text2:
        elements.append(
            Button(
                btn_text2,
                arguments="call2",
            ),
        )
    toast.elements = elements

    return await toast.show()


def register_app():
    if not Toast.is_registered_app_id("GoodbyeDPI_app"):
        Toast.register_app_id(
            "GoodbyeDPI_app",
            "GoodbyeDPI UI",
            icon_uri=DIRECTORY + "data\icon.png",  # noqa: W605
        )


# utils


def install_font(font_path):
    try:
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(os.environ["WINDIR"], "Fonts", font_name)
        shutil.copyfile(font_path, dest_path)

        reg_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            reg_path,
            0,
            winreg.KEY_SET_VALUE,
        ) as reg_key:
            winreg.SetValueEx(
                reg_key,
                "Nunito SemiBold (TrueType)",
                0,
                winreg.REG_SZ,
                font_name,
            )

        ctypes.windll.gdi32.AddFontResourceW(dest_path)
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)

        return True
    except Exception:
        return False


# engine load'n'read

spoofdpi_logo = """███████ ██████   ██████   ██████  ███████ ██████  ██████  ██
██      ██   ██ ██    ██ ██    ██ ██      ██   ██ ██   ██ ██
███████ ██████  ██    ██ ██    ██ █████   ██   ██ ██████  ██
     ██ ██      ██    ██ ██    ██ ██      ██   ██ ██      ██
███████ ██       ██████   ██████  ██      ██████  ██      ██"""


def remove_ansi_sequences(text: str):
    text = re.sub(r"\u001b\]0;.*?\[\?25h", "", text)

    stage1 = re.sub(r"\w:\\[^ ]+", "", text)
    print(
        "",
    )  # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE

    ansi_escape = re.compile(r"(?:\x1B[@-_][0-?]*[ -/]*[@-~])|\]0;")
    stage2 = ansi_escape.sub("", stage1)
    print(
        "",
    )  # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print(
        "",
    )  # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE
    print(
        "",
    )  # SYKA BLYAD EBANIY HYU!!! Without this print the code does not work DO NOT DELETE OGROMNI CHLEN
    if settings.settings["GLOBAL"]["engine"] == "goodbyeDPI":
        stage2.replace("GG", "G")
    stage2 = stage2.replace(
        "https://github.com/ValdikSS/GoodbyeDPI",
        "https://github.com/ValdikSS/GoodbyeDPI\n\n",
    )

    if settings.settings["GLOBAL"]["engine"] == "spoofdpi":
        stage2 = stage2.replace("•ADDR", "\n\n•ADDR")
        stage2 = stage2.replace("to quit", "to quit\n\n")
        stage2 = stage2.replace("Press", "\nPress")
        stage2 = re.sub(r"█.*█", "", stage2, flags=re.DOTALL)
        print(stage2)

    return stage2


class GoodbyedpiWorker(QThread):
    output_signal = Signal(str)
    process_started = Signal()
    process_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, args, engine, parent=None):
        super().__init__(parent)
        self.args = args
        self.engine = engine
        self.stop_event = threading.Event()
        self.queue = queue.Queue()
        self.output = []
        self.reason = "for unknown reason"
        self.error = False
        self.proc = None
        self.pty_process = None

    def run(self):
        engine = self.engine
        execut = EXECUTABLES[engine]

        if engine == "goodbyeDPI":
            self.path = os.path.join(GOODBYE_DPI_PATH, "x86_64", GOODBYE_DPI_EXECUTABLE)
            cwd = os.path.join(GOODBYE_DPI_PATH, "x86_64")
        else:
            self.path = os.path.join(DIRECTORY, f"data/{engine}", execut)
            cwd = os.path.join(DIRECTORY, f"data/{engine}")

        command = [str(self.path)]
        command.extend(self.args)
        print(command)

        self.output = []

        if winpty_support:
            try:
                self.pty_process = winpty.PtyProcess.spawn(command, cwd=cwd)
            except Exception as ex:
                data = f"Component not installed correctly. ({ex})"
                self.queue.put(data)
                self.output.append(data)
                self.output_signal.emit(data)
                self.error_occurred.emit(data)
                return

            while not self.stop_event.is_set():
                if self.pty_process.isalive():
                    try:
                        data = self.pty_process.read(10000)
                        if data:
                            data = remove_ansi_sequences(data)
                            print("data received")
                            self.queue.put(data)
                            self.output.append(data)
                            self.output_signal.emit(data)
                    except OSError as e:
                        print(e)
                        break
                    except Exception:
                        break
                else:
                    break

            self.cleanup()

        else:
            self.proc = start_process(*command, engine=self.engine)
            data = "Filter activated"
            self.queue.put(data)
            self.output_signal.emit(data)

    def cleanup(self):
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except Exception:
                pass
            self.pty_process = None
        execut = EXECUTABLES[self.engine]
        term = f"\n[DEBUG] The {execut} process has been terminated {self.reason}\n"
        self.output.append(term)
        self.queue.put(term)
        self.output_signal.emit(term)

        self.process_finished.emit(self.reason)

    def stop(self):
        self.reason = "by user"
        print("Stopping process...")
        self.stop_event.set()
        if self.pty_process:
            try:
                self.pty_process.close(True)
            except Exception:
                pass
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
        self.wait()


stop_flags = [
    "Error opening filter",
    "unknown option",
    "failed",
    "must specify port filter",
    "ERROR:",
    "Component not installed correctly",
    "--debug=0|1|syslog|@<filename>",
    "error",
    "could not read",
    "invalid value",
    "already running",
]


class GoodbyedpiProcess(QObject):
    output_signal = Signal(str)
    process_started = Signal()
    process_stopped = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.error = False
        self.stop = False
        self.engine = settings.settings["GLOBAL"]["engine"]
        self.reason = "by user"

    @Slot()
    def start_goodbyedpi(self, *args):
        self.engine = settings.settings["GLOBAL"]["engine"]
        if self.worker is None or not self.worker.isRunning():
            self.worker = GoodbyedpiWorker(args=args, engine=self.engine)
            self.worker.output_signal.connect(self.handle_output)
            self.worker.process_finished.connect(self.handle_process_finished)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.start()
            self.error = False
            self.stop = False
            return True
        return False

    @Slot()
    def stop_goodbyedpi(self):
        if not winpty_support:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == EXECUTABLES[self.engine]:
                    try:
                        proc.terminate()
                        if self.worker and self.worker.isRunning():
                            self.worker.stop()
                    except psutil.NoSuchProcess:
                        return False
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.process_stopped.emit(self.reason)
            self.error = False
            self.stop = True
        return True

    def handle_output(self, data):
        if not self.error and not self.stop:
            self.output_signal.emit(data)
        if (
            "Filter activated" in data
            or "capture is started." in data
            or "created a listener" in data
        ):
            self.error = False
            self.process_started.emit()
        elif any(error_msg in data for error_msg in stop_flags):
            self.reason = "for unknown reason"
            self.error = True
            print("Trying to connect terminal")
            error_sound()
            self.error_occurred.emit("Unknown error occurred while process running")

    def handle_process_finished(self, reason):
        self.reason = reason
        self.process_stopped.emit(self.reason)

    def handle_error(self, error_message):
        self.error_occurred.emit(error_message)


def start_process(*args, **kwargs):
    """
    :param *args: startup args: turple
    :param engine: Setting custom engine. Default -> `settings.settings["GLOBAL"]["engine"]`
    :param execut: Executable file. Default -> `EXECUTABLES[engine]`
    :param path: Path to execut. Default -> `DIRECTORY+f'data/{engine}/{execut}'`
    :param cwd: Process work directory. Default -> `DIRECTORY+f'data/{engine}'`
    """
    engine = kwargs.get("engine", settings.settings["GLOBAL"]["engine"])
    execut = kwargs.get("execut", EXECUTABLES[engine])
    path = kwargs.get(
        "path",
        (
            os.path.join(GOODBYE_DPI_PATH, "x86_64", GOODBYE_DPI_EXECUTABLE)
            if engine == "goodbyeDPI"
            else os.path.join(DIRECTORY + f"data/{engine}", execut)
        ),
    )
    cwd = kwargs.get(
        "cwd",
        (
            os.path.join(GOODBYE_DPI_PATH, "x86_64")
            if settings.settings["GLOBAL"]["engine"] == "goodbyeDPI"
            else os.path.join(DIRECTORY + f"data/{engine}")
        ),
    )

    _args = [
        path,
        *args,
    ]

    return subprocess.Popen(
        _args,
        cwd=cwd,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def stop_servise():
    try:
        subprocess.run(["sc", "stop", "WinDivert"], check=True)
        subprocess.run(["sc", "delete", "WinDivert"], check=True)
    except Exception:
        pass


def download_blacklist(
    url,
    progress_toast: ProgressToast,
    local_filename=GOODBYE_DPI_PATH + "russia-blacklist.txt",
):
    temp_filename = local_filename + ".tmp"
    progress_toast.update_toast(0, "downloading")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get("content-length")
            if total_length is None:
                total_length = 1
            else:
                total_length = int(total_length)
            with open(temp_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
        if os.path.exists(local_filename):
            os.remove(local_filename)
        os.rename(temp_filename, local_filename)

    except Exception as ex:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        progress_toast.update_toast(0, "error", str(ex), "Something went wrong")
        return False
    progress_toast.update_toast(100, "complete!")
    return True


def move_settings_file(settings_file_path, backup_settings_file_path):
    shutil.copy(settings_file_path, backup_settings_file_path)


# settings change


def change_setting(setting_group, setting, value):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_PATH, encoding="utf-8")
    config[setting_group][setting] = value

    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as configfile:
        config.write(configfile)

    settings.reload_settings()


def change_settings(setting_group, settings_list):
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE_PATH, encoding="utf-8")
    for i, setting in enumerate(settings_list):
        config[setting_group][setting[0]] = setting[1]

    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as configfile:
        config.write(configfile)

    settings.reload_settings()


def open_custom_blacklist():
    os.startfile(f"{GOODBYE_DPI_PATH}/custom_blacklist.txt")


def check_mica():
    version = platform.version()
    major, minor, build = map(int, version.split("."))
    return build >= 22000


# update
def save_version_data_to_cache(owner, name, obj="prg", url="releases/latest"):
    url = f"https://api.github.com/repos/{owner}/{name}/{url}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"ERR_SERVER_STATUS_CODE_{response.status_code}"

    data = response.json()

    if not os.path.exists(f"{DIRECTORY}tempfiles"):
        os.makedirs(f"{DIRECTORY}tempfiles")

    with open(
        f"{DIRECTORY}tempfiles/versiondata_{owner}_{name}.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    settings.change_setting(
        "CACHE",
        f"{obj}_update_check_time",
        datetime.now().strftime("%d.%m.%Y"),
    )
    settings.save_settings()

    return True


def get_latest_release(reason: Literal["auto", "manual"] = "auto"):

    if (
        settings.get_value("CACHE", "prg_update_check_time")
        != datetime.now().strftime("%d.%m.%Y")
        or not os.path.exists(
            f"{DIRECTORY}tempfiles/versiondata_{REPO_OWNER}_{REPO_NAME}.json",
        )
        or reason == "manual"
    ):
        code = save_version_data_to_cache(REPO_OWNER, REPO_NAME, obj="prg")
        if not code:
            return code

    with open(
        f"{DIRECTORY}tempfiles/versiondata_{REPO_OWNER}_{REPO_NAME}.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return data["tag_name"]


def get_release_info(version):  # ФУНКЦИЯ ПЕРЕПИСЫВАЛАСЬ
    if settings.get_value("CACHE", "prg_update_check_time") != datetime.now().strftime(
        "%d.%m.%Y",
    ) or not os.path.exists(
        f"{DIRECTORY}tempfiles/versiondata_{REPO_OWNER}_{REPO_NAME}.json",
    ):
        code = save_version_data_to_cache(REPO_OWNER, REPO_NAME, obj="prg")
        if not code:
            return code

    with open(
        f"{DIRECTORY}tempfiles/versiondata_{REPO_OWNER}_{REPO_NAME}.json",
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_download_url(version, filetype=".zip"):
    if DEBUG:
        return "patch.cdpipatch"
    try:
        data = get_release_info(version)

        if isinstance(data, str) and ("ERR" in data):
            return data

        download_url = None

        for asset in data["assets"]:
            if asset["name"].endswith(filetype):
                download_url = asset["browser_download_url"]
                break

        if download_url is None:
            return "ERR_INVALID_URL"

        return download_url
    except requests.ConnectionError:
        return "ERR_CONNECTION_LOST"
    except Exception:
        return "ERR_UNKNOWN"


def download_update(url, directory, signal=None, debug_check=True):
    if not debug_check or not DEBUG or signal is None:
        with requests.get(url, stream=True) as r:
            total_length = r.headers.get("content-length")
            if total_length is None:
                with open(directory, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                dl = 0
                total_length = int(total_length)
                with open(directory, "wb") as f:
                    for data in r.iter_content(chunk_size=4096):
                        if signal:
                            signal.emit(float((dl / total_length) * 100))
                        dl += len(data)
                        f.write(data)
    else:
        i = 0
        while i < 100:
            i += 1
            if signal:
                signal.emit(i)
            time.sleep(0.05)
        shutil.copyfile(url, directory)


def get_component_download_url(component_name: str):  # ФУНЦИЯ ПЕРЕПИСЫВАЛАСЬ
    component_addres = COMPONENTS_URLS[component_name]
    repo = component_addres.split("/")[1]
    owner = component_addres.split("/")[0]
    try:
        if settings.get_value(
            "CACHE",
            f"component_{component_name.lower()}_update_check_time",
        ) != datetime.now().strftime("%d.%m.%Y") or not os.path.exists(
            f"{DIRECTORY}tempfiles/versiondata_{owner}_{repo}.json",
        ):
            code = save_version_data_to_cache(
                owner,
                repo,
                obj=f"component_{component_name.lower()}",
                url="releases",
            )
            if not code:
                return code

        with open(
            f"{DIRECTORY}tempfiles/versiondata_{owner}_{repo}.json",
            "r",
            encoding="utf-8",
        ) as file:
            response = json.load(file)

        latest_release = response[0]

        version = latest_release.get("tag_name")
        if component_name == "zapret":
            return f"https://github.com/bol-van/zapret-win-bundle/archive/refs/heads/master.zip|{version}"

        if component_name == "goodbyeDPI" and version == "0.2.3rc3":
            return f"ERR_LATEST_VERSION_ALREADY_INSTALLED|{version}"

        download_url = None

        for asset in latest_release["assets"]:
            if asset["name"].endswith(".zip"):
                # For "byedpi", only select if "x86_64-w64" is in the asset name.
                if component_name == "byedpi" and "x86_64-w64" not in asset["name"]:
                    continue
                download_url = asset["browser_download_url"]
                break
            if asset["name"].endswith(".exe"):
                download_url = asset["browser_download_url"]
                break

        if download_url is None:
            return "ERR_INVALID_URL"

        return download_url + "|" + version

    except Exception:
        return "ERR_UNKNOWN"


def extract_zip(zip_file, zip_folder_to_unpack, extract_to, files_to_skip=[]):
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            members = zip_ref.infolist()
            extracted_files = 0

            index = 0
            while index < len(members):
                member = members[index]
                member_path = member.filename
                if (
                    member_path.count("/") == 1
                    and member_path.split("/")[1] == ""
                    and zip_folder_to_unpack == "/"
                ):
                    zip_folder_to_unpack = member_path

                if member_path.startswith(zip_folder_to_unpack):
                    relative_path = member_path[len(zip_folder_to_unpack) :]
                    if relative_path == "":
                        index += 1
                        continue

                    if any(skip_item in relative_path for skip_item in files_to_skip):
                        index += 1
                        continue

                    destination_path = os.path.join(extract_to, relative_path)
                    destination_dir = os.path.dirname(destination_path)
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)

                    if relative_path.endswith(".txt") and os.path.exists(
                        destination_path,
                    ):
                        index += 1
                        continue

                    if member.is_dir():
                        if not os.path.exists(destination_path):
                            os.makedirs(destination_path)
                    else:
                        try:
                            with zip_ref.open(member) as source, open(
                                destination_path,
                                "wb",
                            ) as target:
                                shutil.copyfileobj(source, target)
                        except OSError as pe:
                            print(pe.errno)
                            if "13" in str(pe.errno):
                                return "ERR_PERMISSION_DENIED"
                            return "ERR_FILE_UNPACKING"
                        except Exception:
                            return "ERR_FILE_UNPACKING"

                    extracted_files += 1
                index += 1

    except Exception as ex:
        print(ex)
        return "ERR_FILE_UNPACKING"


def download_files_from_github(remote_dir, local_dir):
    base_url = f"https://api.github.com/repos/{REPO_OWNER}/{CONFIGS_REPO_NAME}/contents/{remote_dir}?ref=main"
    headers = {"Accept": "application/vnd.github.v3.raw"}

    skip_files = [
        "custom_blacklist.txt",
        "list-discord.txt",
        "list-youtube.txt",
        "youtube.txt",
        "myhostlist.txt",
        "russia-blacklist.txt",
    ]

    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            return f"ERR_SERVER_STATUS_CODE_{response.status_code}"

        files = response.json()

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        for file_info in files:
            if file_info["type"] == "file":
                filename = file_info["name"]
                if filename in (".", ".."):
                    continue

                local_filepath = os.path.join(local_dir, filename)
                if filename == "user.json" and os.path.exists(local_filepath):
                    print(local_filepath)
                    continue

                if filename in skip_files and os.path.exists(local_filepath):
                    continue

                download_url = file_info["download_url"]
                file_response = requests.get(download_url, headers=headers)
                if file_response.status_code == 200:
                    with open(local_filepath, "wb") as f:
                        f.write(file_response.content)
                else:
                    continue

        return None
    except Exception:
        return "ERR_CONFIG_DOWNLOAD_UNKNOWN"


def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            return "ERR_FILE_NOT_FOUND"
        return None
    except FileNotFoundError:
        return "ERR_FILE_NOT_FOUND"
    except PermissionError:
        return "ERR_PERMISSION_DENIED"
    except Exception:
        return "ERR_CLEANUP_FILES"


def open_folder(folder_path):
    os.startfile(folder_path)


def register_component(component_name: str, version):
    component_directory = (
        DIRECTORY + f"data/{component_name}"
        if not DEBUG
        else f"E:/_component/{component_name}"
    )
    result = download_files_from_github(
        remote_dir=f"{component_name.lower()}/",
        local_dir=component_directory,
    )
    if result:
        return result

    config_component_path = (
        CONFIG_PATH + f"/{component_name.lower()}"
        if not DEBUG
        else f"E:/_component/{component_name}/config"
    )
    result = download_files_from_github(
        remote_dir=f"{component_name.lower()}/configs",
        local_dir=config_component_path,
    )
    if result:
        return result

    change_settings(
        "COMPONENTS",
        [
            [f"{component_name.lower()}", "True"],
            [f"{component_name.lower()}_version", version],
            [f"{component_name.lower()}_server_version", version],
        ],
    )
    return None


def unregister_component(component_name: str):
    if component_name == "goodbyeDPI":
        return "ERR_CANNOT_REMOVE_COMPONENT"
    if settings.settings["GLOBAL"]["engine"] == component_name:
        change_setting("GLOBAL", "engine", "goodbyeDPI")
    change_setting("COMPONENTS", f"{component_name.lower()}", "False")
    return "True"


def is_process_running(process_name):
    for proc in psutil.process_iter(["pid", "name"]):

        if proc.info["name"] == process_name:
            if proc.info["pid"] != os.getpid():
                return proc
    return None


# autorun


def create_xml(author, executable, arguments):  # ФУНКЦИЯ ПЕРЕПИСЫВАЛАСЬ
    user_domain = os.environ.get("USERDOMAIN", "")
    user_name = os.environ.get("USERNAME", "")
    current_user = f"{user_domain}\\{user_name}" if user_domain else user_name

    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
  <Task xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
    <RegistrationInfo>
      <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
      <Author>{author}</Author>
    </RegistrationInfo>
    <Triggers>
      <LogonTrigger>
        <Enabled>true</Enabled>
        <UserId>{current_user}</UserId>
      </LogonTrigger>
    </Triggers>
    <Principals>
      <Principal id="Author">
        <UserId>{current_user}</UserId>
        <LogonType>InteractiveToken</LogonType>
        <RunLevel>HighestAvailable</RunLevel>
      </Principal>
    </Principals>
    <Settings>
      <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
      <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
      <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
      <AllowHardTerminate>true</AllowHardTerminate>
      <StartWhenAvailable>true</StartWhenAvailable>
      <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
      <IdleSettings>
        <StopOnIdleEnd>false</StopOnIdleEnd>
        <RestartOnIdle>false</RestartOnIdle>
      </IdleSettings>
      <AllowStartOnDemand>true</AllowStartOnDemand>
      <Enabled>true</Enabled>
      <Hidden>false</Hidden>
      <RunOnlyIfIdle>false</RunOnlyIfIdle>
      <WakeToRun>false</WakeToRun>
      <ExecutionTimeLimit>P3D</ExecutionTimeLimit>
      <Priority>7</Priority>
    </Settings>
    <Actions Context="Author">
      <Exec>
        <Command>{executable}</Command>
        <Arguments>{arguments}</Arguments>
      </Exec>
    </Actions>
  </Task>
  """
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-16",
        suffix=".xml",
        delete=False,
    ) as temp_xml:
        temp_xml.write(xml_content)
        return temp_xml.name


def remove_xml(path):
    os.remove(path)


# goodbyeDPI

hash_gdpi_64_023rc32 = "afa7f66231b9cec7237e738b622c0181"
hash_gdpi_64_023testbuild = "4d060be292eb50783c0d8022d4bf246c"
hash_gdpi_64_testbuild_by_Decavoid = "c25b01de6d5471f3b7337122049827f6"  # noqa: N816


def calculate_hash(file_path, algorithm="md5"):
    hash_function = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_function.update(chunk)

    return hash_function.hexdigest()


def check_version(gdpi_exe_fullpath=GOODBYE_DPI_PATH + "\\x86_64\\goodbyedpi.exe"):
    hash_value = calculate_hash(gdpi_exe_fullpath)

    if hash_value == hash_gdpi_64_023testbuild:
        return "test version - FWSNI support"
    if hash_value == hash_gdpi_64_testbuild_by_Decavoid:
        return "test version (Decavoid) - FWSNI support"
    if hash_value == hash_gdpi_64_023rc32:
        return "0.2.3-rc3-2"

    return "UNKNOWN VERSION (FWSNI support enabled)"


def sni_support():
    if "FWSNI support" in check_version():
        return True
    return False


def check_urls():
    with open(
        f"{(DEBUG_PATH if DEBUG else '') + GOODBYE_DPI_PATH}/custom_blacklist.txt",
        "r",
    ) as file:
        urls = file.read().splitlines()

    sites = []
    print(urls)

    for url in urls:
        try:
            print(url)
            response = requests.head("https://" + url, timeout=5)
            print(response)
            if response.status_code != 404:
                sites.append("https://" + url)
        except requests.RequestException as ex:
            if "Read timed out." in str(ex):
                sites.append("https://" + url)
            print(str(ex), ex)
            continue
        except Exception:
            continue

    return sites


def get_parameter_mappings(engine_name):
    parameter_mappings = {
        "goodbyedpi": (PARAMETER_MAPPING, VALUE_PARAMETERS),
        "zapret": (None, None),
        "byedpi": (None, None),
        "spoofdpi": (S_PARAMETER_MAPPING, S_VALUE_PARAMETERS),
    }
    return parameter_mappings.get(engine_name, ({}, {}))


def convert_custom_params(command, parameter_mapping, value_parameters):
    command = command.split(" ")
    params = {}
    custom_params = []
    params["blacklist_value"] = ""
    i = 0
    while i < len(command):
        cmd_param = command[i]
        if cmd_param in parameter_mapping.values():
            ini_param = list(parameter_mapping.keys())[
                list(parameter_mapping.values()).index(cmd_param)
            ]
            print(cmd_param, ini_param)
            if ini_param == "blacklist":
                i += 1
                params[f"{ini_param}_value"] += f',"{command[i]}"'
            params[ini_param] = True
            if ini_param in value_parameters:
                i += 1
                params[f"{ini_param}_value"] = command[i]
        elif cmd_param in value_parameters.values():
            ini_param = list(value_parameters.keys())[
                list(value_parameters.values()).index(cmd_param)
            ]
            i += 1
            params[ini_param] = True
            params[f"{ini_param}_value"] = command[i]
        else:
            custom_params.append(cmd_param)
        i += 1
    params["custom_parameters"] = " ".join(custom_params)
    return params


# JSON
def convert_bat_file(bat_file, output_folder, engine):
    with open(bat_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    variables = {}
    command_lines = []
    in_command = False

    for line in lines:
        line = line.strip()

        if not line or line.startswith("::") or line.lower().startswith("rem"):
            continue

        var_match = re.match(r"set\s+(\w+)=([\s\S]+)", line, re.IGNORECASE)
        if var_match:
            var_name = var_match.group(1)
            var_value = var_match.group(2)
            var_value = var_value.replace("%~dp0", "")
            var_value = var_value.strip('"')
            variables[var_name.upper()] = var_value
            continue

        if line.lower().startswith("start"):
            in_command = True
            line = re.sub(
                r'start\s+".*?"\s+((/min+\s+".*?")|(\S*))\s*\^?',
                "",
                line,
                flags=re.IGNORECASE,
            )
            line = line.strip()
            if line:
                command_lines.append(line)
            continue

        if in_command:
            if line.endswith("^"):
                line = line[:-1].strip()
                command_lines.append(line)
            else:
                command_lines.append(line)
                in_command = False
                continue

    command = " ".join(command_lines)

    command = command.replace("^", "").replace("\n", "").strip()

    command = command.replace("%~dp0", "").replace("POPD", "")

    def replace_vars(match):
        var_name = match.group(1)
        return variables.get(var_name.upper(), "")

    command = re.sub(r"%(\w+)%", replace_vars, command)

    command = command.replace(r'\\"', "").replace('"', "")
    command = command.replace("%~dp0..\\bin\\", "")

    command = command.replace("=", " ")

    command = re.sub(r"\s+", " ", command).strip()

    if command == "":
        raise KeyError(
            "Empty startup parameters. The file is damaged or not compatible",
        )

    parameter_mapping, value_parameters = get_parameter_mappings(engine.lower())

    if parameter_mapping and value_parameters:
        json_data = convert_custom_params(command, parameter_mapping, value_parameters)
    else:
        json_data = {"custom_parameters": command}

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    bat_name = os.path.splitext(os.path.basename(bat_file))[0]
    json_file = os.path.join(output_folder, f"{bat_name}.json")

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    return json_file


def check_json_file(file: str, component: str):
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            custom_parameters = data.get("custom_parameters")
            if custom_parameters is not None and custom_parameters != "":
                return True
            raise KeyError(f"Unable to load {file}. JSON file not setup right")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Unable to found config file {file}. File is not exist in current location",
        )
    except json.JSONDecodeError:
        raise json.JSONDecodeError(
            f"Unable to found config file {file}. File encoding is incorrect",
        )


def get_preset_parameters(index: int | str, engine: str):
    filename = f"{index}.json"
    path = os.path.join(
        (DEBUG_PATH if DEBUG else "") + CONFIG_PATH + "/" + engine.lower(),
        filename,
    )
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            custom_parameters = data.get("custom_parameters")
            if custom_parameters is not None:
                return str(custom_parameters).split()
            raise KeyError(f"Unable to load {filename}. JSON file not setup right")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Unable to found config file {filename}. File is not exist in current location {path}",
        )
    except json.JSONDecodeError:
        raise json.JSONDecodeError(
            f"Unable to found config file {filename}. File encoding is incorrect",
        )


def replace_system_folders_with_short_names(path):
    system_folders = {
        "Program Files": "Progra~1",
        "Program Files (x86)": "Progra~2",
        "ProgramData": "Progra~3",
        "Users": "Users",
        "Documents and Settings": "Docume~1",
        "Application Data": "Applic~1",
        "Local Settings": "LocalS~1",
    }

    path_parts = path.split(os.sep)

    new_path_parts = []
    for part in path_parts:
        if part in system_folders:
            new_path_parts.append(system_folders[part])
        else:
            new_path_parts.append(part)

    return os.sep.join(new_path_parts)


def pretty_path(text):
    def random_string(length):
        return ""

    def transliterate(char):
        translit_table = {
            "А": "A",
            "Б": "B",
            "В": "V",
            "Г": "G",
            "Д": "D",
            "Е": "E",
            "Ё": "E",
            "Ж": "Zh",
            "З": "Z",
            "И": "I",
            "Й": "Y",
            "К": "K",
            "Л": "L",
            "М": "M",
            "Н": "N",
            "О": "O",
            "П": "P",
            "Р": "R",
            "С": "S",
            "Т": "T",
            "У": "U",
            "Ф": "F",
            "Х": "Kh",
            "Ц": "Ts",
            "Ч": "Ch",
            "Ш": "Sh",
            "Щ": "Shch",
            "Ъ": "",
            "Ы": "Y",
            "Ь": "",
            "Э": "E",
            "Ю": "Yu",
            "Я": "Ya",
            "а": "a",
            "б": "b",
            "в": "v",
            "г": "g",
            "д": "d",
            "е": "e",
            "ё": "e",
            "ж": "zh",
            "з": "z",
            "и": "i",
            "й": "y",
            "к": "k",
            "л": "l",
            "м": "m",
            "н": "n",
            "о": "o",
            "п": "p",
            "р": "r",
            "с": "s",
            "т": "t",
            "у": "u",
            "ф": "f",
            "х": "kh",
            "ц": "ts",
            "ч": "ch",
            "ш": "sh",
            "щ": "shch",
            "ъ": "",
            "ы": "y",
            "ь": "",
            "э": "e",
            "ю": "yu",
            "я": "ya",
        }
        return translit_table.get(char, None)

    result = re.sub(
        r'[^0-9a-zA-Z:"><\/\\.\-_\s,=+]',
        lambda x: transliterate(x.group()) or random_string(len(x.group())),
        text,
    )
    return result if result != "" else "_template"
