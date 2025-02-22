import json
import os
import re
import shutil
import tempfile
import time
import traceback
from typing import Literal
import zipfile

from _data import DEBUG, DEBUG_PATH, DIRECTORY, settings, VERSION
from PySide6.QtCore import QObject, QThread, Signal, Slot
import requests
from utils import change_setting, download_update, get_download_url, get_latest_release

from logger import AppLogger

logger = AppLogger(VERSION, "patcher")


class Patcher(QObject):
    errorHappens = Signal(str)  # noqa: N815
    downloadProgress = Signal(float)  # noqa: N815
    downloadFinished = Signal(str)  # noqa: N815
    workFinished = Signal()  # noqa: N815
    patcherWorkFinished = Signal()  # noqa: N815
    preparationProgress = Signal()  # noqa: N815

    def __init__(self):
        super().__init__()
        self.state = "quit"

    @Slot()
    def download_update(self):
        self.qthread = QThread()
        self.worker = PatchDownloadWorker()
        self.worker.moveToThread(self.qthread)

        self.qthread.started.connect(self.worker.run)
        self.worker.progressChanged.connect(self.downloadProgress)
        self.worker.progressChanged.connect(self.progressChanged)
        self.worker.downloadFinished.connect(self.downloadFinished)
        self.worker.error.connect(self.downloadFinished)
        self.worker.preparationProgress.connect(self.preparationProgress)
        self.worker.preparationProgress.connect(self.preparation)
        self.worker.workFinished.connect(self._quit)
        self.worker.workFinished.connect(self.qthread.quit)
        self.worker.workFinished.connect(self.worker.deleteLater)
        self.qthread.finished.connect(self.qthread.deleteLater)

        self.qthread.start()

    @Slot(str)
    def add_local_patch(self, file_path):
        self.qthread = QThread()
        self.worker = PatchDownloadWorker(file_path)
        self.worker.moveToThread(self.qthread)

        self.qthread.started.connect(self.worker.run)
        self.worker.progressChanged.connect(self.downloadProgress)
        self.worker.error.connect(self.errorHappens)
        self.worker.workFinished.connect(self.qthread.quit)
        self.worker.workFinished.connect(self.worker.deleteLater)
        self.worker.workFinished.connect(self.patcherWorkFinished)
        self.qthread.finished.connect(self.qthread.deleteLater)

        self.qthread.start()

    @Slot()
    def open_requirements(self):
        if os.path.exists(f"{DIRECTORY}unpacked_patch/requirements.json"):
            os.startfile(f"{DIRECTORY}unpacked_patch/requirements.json")

    @Slot()
    def get_ready_for_install(self):
        if os.path.exists(f"{DIRECTORY}unpacked_patch"):
            shutil.rmtree(f"{DIRECTORY}unpacked_patch")

    @Slot(float)
    def progressChanged(self, progress: float):  # noqa: N802
        self.state = "progress"

    @Slot()
    def preparation(self):
        self.state = "preparation"

    @Slot()
    def _quit(self):
        self.state = "quit"

    @Slot(result=bool)
    def is_getting_ready(self):
        if self.state == "preparation":
            return True
        return False


class PatchDownloadWorker(QObject):
    error = Signal(str)
    progressChanged = Signal(float)  # noqa: N815
    downloadFinished = Signal(str)  # noqa: N815
    workFinished = Signal()  # noqa: N815
    preparationProgress = Signal()  # noqa: N815

    def __init__(self, local_file_path=None):
        super().__init__()
        self.local_file_path = local_file_path
        self.processed_patches = []

    def run(self):
        if self.local_file_path:
            # Only for development mode. Unstable.
            time.sleep(2)
            success = self._process_patch(self.local_file_path, mode="manual")
            self.workFinished.emit()
            return
        success = self._download_update()
        self.downloadFinished.emit(success)

    def _download_update(self):
        filename = "patch.cdpipatch"
        directory = os.path.join(
            (DEBUG_PATH if DEBUG else settings.settings["GLOBAL"]["work_directory"]),
            filename,
        )
        self.local_file_path = directory
        try:
            url = get_download_url(get_latest_release(), filetype=".cdpipatch")
        except KeyError:
            return "ERR_INVALID_SERVER_RESPONSE"

        print(url)

        if "ERR" in url:
            self.progressChanged.emit(0.0)
            return url

        try:
            download_update(url, directory, self.progressChanged)
            self.progressChanged.emit(0.0)
            change_setting("GLOBAL", "after_update", "True")

            if os.path.isdir(f"{DIRECTORY}unpacked_patch"):
                shutil.rmtree(f"{DIRECTORY}unpacked_patch")

            os.makedirs(f"{DIRECTORY}unpacked_patch")

            return self._process_patch(directory)
        except requests.ConnectionError:
            return "ERR_CONNECTION_LOST"
        except IOError:
            logger.create_error_log(traceback.format_exc())
            return "ERR_FILE_WRITE"
        except Exception:
            return "ERR_UNKNOWN"

    def _process_patch(self, patch_file, mode: Literal["manual", "auto"] = "auto"):
        self.preparationProgress.emit()

        if patch_file in self.processed_patches:
            print(f"Already processed - {patch_file}")
            return "True"

        temp_dir = self._create_temp_dir(DEBUG_PATH + DIRECTORY)
        self.preparationProgress.emit()
        try:
            self._extract_patch(patch_file, temp_dir)

            if not patch_file.endswith(".cdpipatch"):
                self.processed_patches.append(temp_dir)
                return "True"

            requirements_path = os.path.join(temp_dir, "requirements.json")
            goodbyeDPI_UI_path = os.path.join(temp_dir, "goodbyeDPI UI")  # noqa: N806

            self.preparationProgress.emit()

            if not os.path.exists(requirements_path) or not os.path.exists(
                goodbyeDPI_UI_path,
            ):
                shutil.rmtree(temp_dir)
                self.error.emit("ERR_INVALID_PATCH")
                return "ERR_INVALID_PATCH"

            with open(requirements_path, "r") as file:
                requirements = json.load(file)

            patch_urls = requirements.get("patch_urls", [])

            for url in patch_urls:
                self.preparationProgress.emit()
                match = re.search(r"/download/(\d+\.\d+\.\d+)/", url)
                if match and not DEBUG:
                    version = match.group(1)
                    if version < VERSION:
                        continue

                dependency_patch_path = os.path.join(temp_dir, os.path.basename(url))
                try:
                    self._download_and_process_dependency(url, dependency_patch_path)
                except Exception:
                    shutil.rmtree(temp_dir)
                    self.error.emit("ERR_PATCH_REQUROEMENTS_DOWNLOAD")
                    return "ERR_PATCH_REQUROEMENTS_DOWNLOAD"

            self.processed_patches.append(temp_dir)

        except Exception:
            shutil.rmtree(temp_dir)
            self.error.emit("ERR_INVALID_PATCH")
            return "ERR_INVALID_PATCH"

        try:
            if self.local_file_path == patch_file:
                self._apply_patch(temp_dir)
                if mode == "auto" and os.path.exists(self.local_file_path):
                    os.remove(self.local_file_path)

        except Exception as ex:
            print(ex)

            for i, patch_url in enumerate(self.processed_patches):
                shutil.rmtree(self.processed_patches[i])
            self.processed_patches.clear()

            shutil.rmtree(f"{DIRECTORY}unpacked_patch")

            self.error.emit("ERR_PATCH_APPLY")
            return "ERR_PATCH_APPLY"

        return "True"

    def _download_and_process_dependency(self, url, dependency_patch_path):
        download_update(
            url,
            dependency_patch_path,
            self.progressChanged,
            debug_check=False,
        )

        self._process_patch(dependency_patch_path)

    def _apply_patch(self, patch_dir):
        self.preparationProgress.emit()

        goodbyeDPI_UI_path = f"{DIRECTORY}unpacked_patch/goodbyeDPI UI"  # noqa: N806

        for i, patch_url in enumerate(self.processed_patches):
            if not os.path.exists(
                os.path.join(DEBUG_PATH + DIRECTORY, patch_url, "goodbyeDPI UI"),
            ):
                shutil.move(patch_url, goodbyeDPI_UI_path)
            else:
                _tmp = os.path.join(DEBUG_PATH + DIRECTORY, patch_url, "goodbyeDPI UI")
                for root, _, files in os.walk(_tmp):
                    relative_path = os.path.relpath(root, _tmp)
                    target_dir = os.path.join(goodbyeDPI_UI_path, relative_path)

                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    for file in files:
                        shutil.move(
                            os.path.join(root, file),
                            os.path.join(target_dir, file),
                        )

        old_directory = os.path.join(DIRECTORY, ".old")
        if os.path.exists(old_directory):
            shutil.rmtree(old_directory)

        os.makedirs(old_directory)

        for root, _, files in os.walk(goodbyeDPI_UI_path):
            for file in files:
                source_path = os.path.relpath(
                    os.path.join(root, file),
                    goodbyeDPI_UI_path,
                )
                target_path = os.path.join(
                    old_directory,
                    os.path.relpath(root, goodbyeDPI_UI_path),
                    file,
                )

                _file = os.path.join(DEBUG_PATH + DIRECTORY, source_path)
                if os.path.exists(_file) and source_path != ".":
                    if not os.path.isfile(_file) and not os.path.exists(target_path):
                        os.makedirs(target_path)
                        continue

                    if not os.path.exists(target_path):
                        target_dir = os.path.dirname(target_path)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)

                    shutil.copy(
                        os.path.join(DEBUG_PATH + DIRECTORY, source_path),
                        target_path,
                    )

        zip_file_path = os.path.join(patch_dir, "..", "_portable.zip")
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

        self.preparationProgress.emit()
        shutil.make_archive(
            zip_file_path.replace(".zip", ""),
            "zip",
            f"{DIRECTORY}unpacked_patch",
        )
        try:
            for i, patch_url in enumerate(self.processed_patches):
                shutil.rmtree(self.processed_patches[i])
        except Exception:
            logger.create_error_log(traceback.format_exc())
        self.processed_patches.clear()

        shutil.rmtree(f"{DIRECTORY}unpacked_patch")

    def _extract_patch(self, patch_file, destination):
        with zipfile.ZipFile(patch_file, "r") as zip_ref:
            total_files = len(zip_ref.infolist())
            for i, file in enumerate(zip_ref.infolist(), 1):
                zip_ref.extract(file, destination)
                self.progressChanged.emit(i / total_files * 100)

    def _create_temp_dir(self, base_dir):
        return tempfile.mkdtemp(dir=base_dir)
