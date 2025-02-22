import logging
import os
import shutil
import time
import traceback

from _data import (
    BACKUP_SETTINGS_FILE_PATH,
    COMPONENTS_URLS,
    DEBUG,
    DEBUG_PATH,
    DIRECTORY,
    GOODBYE_DPI_PATH,
    LOG_LEVEL,
    settings,
    SETTINGS_FILE_PATH,
    text,
    VERSION,
)
from PySide6.QtCore import QObject, QThread, Signal, Slot
from quick_start import merge_blacklist, merge_settings
from utils import get_component_download_url

from Backend.backend import DownloadComponent
from logger import AppLogger


logger = AppLogger(VERSION, "after_update", LOG_LEVEL if not DEBUG else logging.DEBUG)


class AfterUpdateHelper(QObject):
    progressIndeterminateVisibleChanged = Signal(bool)  # noqa: N815
    progressVisibleChanged = Signal(bool)  # noqa: N815
    progressValueChanged = Signal(int)  # noqa: N815
    remainingTimeChanged = Signal("QVariantList")  # noqa: N815
    updateMovingSettingsCompleted = Signal()  # noqa: N815
    updateCleanupStarted = Signal()  # noqa: N815
    updateCleanupCompleted = Signal()  # noqa: N815
    updateComponentsStarted = Signal()  # noqa: N815
    updateComponentsCompleted = Signal()  # noqa: N815

    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.skip_components_update = False

    @Slot()
    def open_logs(self):
        os.startfile(DEBUG_PATH + DIRECTORY + "update.log")

    @Slot(bool)
    def startUpdateProcess(  # noqa: N802
        self,
        skip_components_update,
    ):  # Add flag for skip components update
        self.startMovingSettings()
        self.skip_components_update = skip_components_update

    def startMovingSettings(self):  # noqa: N802
        self.worker_thread = QThread()
        self.worker = MovingSettingsWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.progressVisibleChanged.connect(self.progressVisibleChanged)
        self.worker.progressValueChanged.connect(self.progressValueChanged)
        self.worker.finished.connect(self.movingSettingsFinished)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    @Slot()
    def movingSettingsFinished(self):  # noqa: N802
        self.updateMovingSettingsCompleted.emit()
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.startCleanup()

    def startCleanup(self):  # noqa: N802
        self.progressIndeterminateVisibleChanged.emit(True)
        self.updateCleanupStarted.emit()
        self.worker_thread = QThread()
        self.worker = CleanupWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.progressVisibleChanged.connect(self.progressVisibleChanged)
        self.worker.progressValueChanged.connect(self.progressValueChanged)
        self.worker.remainingTimeChanged.connect(self.remainingTimeChanged)
        self.worker.finished.connect(self.cleanupFinished)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    @Slot()
    def cleanupFinished(self):  # noqa: N802
        self.progressIndeterminateVisibleChanged.emit(False)
        self.updateCleanupCompleted.emit()
        self.worker_thread.quit()
        self.worker_thread.wait()

        self.startUpdatingComponents()

    def startUpdatingComponents(self):  # noqa: N802
        self.updateComponentsStarted.emit()

        if self.skip_components_update:
            self.updateComponentsCompleted.emit()
            return

        self.worker_thread = QThread()
        self.worker = UpdateComponentsWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.progressIndeterminateVisibleChanged.connect(
            self.progressIndeterminateVisibleChanged,
        )
        self.worker.progressValueChanged.connect(self.progressValueChanged)
        self.worker.finished.connect(self.updateComponentsFinished)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    @Slot()
    def exitApp(self):  # noqa: N802
        os._exit(0)

    @Slot()
    def gotoMainWindow(self):  # noqa: N802
        self.updateComponentsCompleted.emit()

    @Slot()
    def updateComponentsFinished(self):  # noqa: N802
        self.updateComponentsCompleted.emit()
        try:
            self.worker_thread.quit()
            self.worker_thread.wait()
        except Exception:
            pass


class MovingSettingsWorker(QObject):
    progressVisibleChanged = Signal(bool)  # noqa: N815
    progressValueChanged = Signal(int)  # noqa: N815
    finished = Signal()

    def run(self):
        source_dir = (
            DIRECTORY + "_internal/data" if not DEBUG else "E:/_component/data1"
        )
        dest_dir = DIRECTORY + "data" if not DEBUG else "E:/_component/data"
        if os.path.exists(source_dir):
            try:
                files_to_move = []
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(".txt"):
                            source_file = os.path.join(root, file)
                            relative_path = os.path.relpath(source_file, source_dir)
                            dest_file = os.path.join(dest_dir, relative_path)
                            files_to_move.append((source_file, dest_file))

                total_files = len(files_to_move)

                if not merge_settings(
                    source_dir + "/settings/_settings.ini",
                    dest_dir + "/settings/settings.ini",
                ):
                    logger.create_error_log(
                        "The update could not be completed correctly. Your data may be lost.\n\n"
                        + f"Backup settings file {source_dir + '/settings/_settings.ini'} does not exist.",
                    )
                settings.reload_settings()

                if total_files == 0:
                    self.finished.emit()
                    return

                self.progressVisibleChanged.emit(True)
                for index, (source_file, dest_file) in enumerate(files_to_move):
                    try:
                        dest_file_dir = os.path.dirname(dest_file)
                        if not os.path.exists(dest_file_dir):
                            os.makedirs(dest_file_dir)

                        shutil.copyfile(source_file, dest_file)

                        progress = int((index + 1) / total_files * 100)
                        self.progressValueChanged.emit(progress)
                    except Exception as e:
                        logger.create_error_log(
                            f"Error moving file {source_file} to {dest_file}: {e}",
                        )

                self.progressVisibleChanged.emit(False)
            except Exception:
                logger.raise_warning(
                    "The update could not be completed. Your data may be lost.\n\n"
                    + traceback.format_exc(),
                )
        else:
            try:
                merge_settings(BACKUP_SETTINGS_FILE_PATH, SETTINGS_FILE_PATH)
                merge_blacklist(GOODBYE_DPI_PATH)
                settings.reload_settings()

                settings.change_setting("GLOBAL", "after_update", "False")
            except Exception:
                logger.raise_warning(
                    "The update could not be completed. Your data may be lost.\n\n"
                    + traceback.format_exc(),
                )

        if settings.settings["COMPONENTS"]["goodbyedpi_server_version"] == "0.2.3rc3":
            settings.settings["COMPONENTS"][
                "goodbyedpi_server_version"
            ] = "test version - FWSNI support"
            settings.save_settings()

        text.reload_text()
        self.finished.emit()


class CleanupWorker(QObject):
    progressVisibleChanged = Signal(bool)  # noqa: N815
    progressValueChanged = Signal(int)  # noqa: N815
    remainingTimeChanged = Signal(list)  # noqa: N815
    finished = Signal()

    def run(self):
        items_to_delete = []

        inte_dir = DIRECTORY + "_internal" if not DEBUG else "E:/_component/_internal"
        port_dir = (
            DIRECTORY + "_portable.zip" if not DEBUG else "E:/_component/_portable.zip"
        )

        if os.path.exists(inte_dir):
            items_to_delete.append(inte_dir)
        if os.path.exists(port_dir):
            items_to_delete.append(port_dir)

        total_items = 0
        time_per_item = 0.01
        items_file_counts = {}

        for item in items_to_delete:
            if os.path.isdir(item):
                total_files = self.count_files_in_directory(item)
                items_file_counts[item] = total_files
                total_items += total_files
            elif os.path.isfile(item):
                items_file_counts[item] = 1
                total_items += 1

        if total_items == 0:
            self.finished.emit()
            return

        total_estimated_time = total_items * time_per_item

        self.progressVisibleChanged.emit(True)
        files_deleted = 0

        for item in items_to_delete:
            try:
                if os.path.isdir(item):
                    for root, dirs, files in os.walk(item, topdown=False):
                        for name in files:
                            file_path = os.path.join(root, name)
                            try:
                                os.remove(file_path)
                                files_deleted += 1
                                self.update_progress(
                                    files_deleted,
                                    total_items,
                                    total_estimated_time,
                                )
                            except Exception as e:
                                logger.create_error_log(
                                    f"Error deleting file {file_path}: {e}",
                                )
                        for name in dirs:
                            dir_path = os.path.join(root, name)
                            try:
                                os.rmdir(dir_path)
                                files_deleted += 1
                                self.update_progress(
                                    files_deleted,
                                    total_items,
                                    total_estimated_time,
                                )
                            except Exception as e:
                                logger.create_error_log(
                                    f"Error deleting directory {dir_path}: {e}",
                                )
                    try:
                        os.rmdir(item)
                        files_deleted += 1
                        self.update_progress(
                            files_deleted,
                            total_items,
                            total_estimated_time,
                        )
                    except Exception as e:
                        logger.create_error_log(f"Error deleting directory {item}: {e}")
                elif os.path.isfile(item):
                    os.remove(item)
                    files_deleted += 1
                    self.update_progress(
                        files_deleted,
                        total_items,
                        total_estimated_time,
                    )
            except Exception as e:
                logger.create_error_log(f"Error deleting {item}: {e}")

        self.progressVisibleChanged.emit(False)
        self.remainingTimeChanged.emit(["", 0])
        self.finished.emit()

    def update_progress(self, files_deleted, total_files, total_estimated_time):
        progress = int((files_deleted / total_files) * 100)
        self.progressValueChanged.emit(progress)
        elapsed_time = files_deleted * 0.01
        remaining_time = total_estimated_time - elapsed_time
        self.emitRemainingTime(remaining_time)
        time.sleep(0.01)

    def emitRemainingTime(self, remaining_time):  # noqa: N802
        if remaining_time > 60:
            minutes_left = int(remaining_time / 60)
            remaining_time_str = ["cleanup_c", minutes_left]
        elif remaining_time > 0:
            remaining_time_str = ["cleanup_m", 0]
        else:
            remaining_time_str = ["cleanup_e", 0]
        self.remainingTimeChanged.emit(remaining_time_str)

    def count_files_in_directory(self, directory):
        total_files = 0
        for root, dirs, files in os.walk(directory):
            total_files += len(files) + len(dirs)

        total_files += 1
        return total_files


class UpdateComponentsWorker(QObject):
    progressIndeterminateVisibleChanged = Signal(bool)  # noqa: N815
    progressValueChanged = Signal(int)  # noqa: N815
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.components_to_update = []
        self.update_urls = {}
        self.current_component_index = 0
        self.qthreads = []
        self.workers = []

    def check_updates(self):
        update_available = False
        settings.settings["GLOBAL"]["check_complete"] = "True"
        urls = {}
        try:
            for i, component_name in enumerate(COMPONENTS_URLS):
                c = component_name.lower()
                if not settings.settings.getboolean("COMPONENTS", c):
                    continue
                try:
                    pre_url = get_component_download_url(component_name)
                    url = pre_url.split("|")[0]
                    if url == "ERR_LATEST_VERSION_ALREADY_INSTALLED":
                        continue
                    print(url)
                    version = pre_url.split("|")[1]

                    if (
                        settings.get_value("COMPONENTS", c + "_version").replace(
                            "v",
                            "",
                        )
                        != version
                    ):
                        settings.settings["COMPONENTS"][c + "_server_version"] = version
                        urls[component_name] = pre_url
                except Exception as ex:
                    print(ex)
                    settings.settings["GLOBAL"]["check_complete"] = "False"

                if settings.get_value("COMPONENTS", c + "_version").replace(
                    "v",
                    "",
                ) != settings.get_value("COMPONENTS", c + "_server_version").replace(
                    "v",
                    "",
                ):
                    update_available = True

            settings.save_settings()
            return update_available, urls
        except Exception as ex:
            print(ex)
            settings.settings["GLOBAL"]["check_complete"] = "False"
            settings.save_settings()
            return False, urls

    @Slot()
    def run(self):
        self.progressIndeterminateVisibleChanged.emit(True)
        update_available, urls = self.check_updates()
        if not update_available and not urls:
            self.progressIndeterminateVisibleChanged.emit(False)
            self.finished.emit()
            return

        self.update_urls = urls
        for component_name in COMPONENTS_URLS:
            c = component_name.lower()
            if not settings.settings.getboolean("COMPONENTS", c):
                continue
            if settings.get_value("COMPONENTS", c + "_version").replace(
                "v",
                "",
            ) != settings.get_value("COMPONENTS", c + "_server_version").replace(
                "v",
                "",
            ):
                self.components_to_update.append(component_name)

        self.current_component_index = 0
        self.start_next_download()

    def start_next_download(self):
        if self.current_component_index >= len(self.components_to_update):
            self.progressIndeterminateVisibleChanged.emit(False)
            self.finished.emit()
            return

        component_name = self.components_to_update[self.current_component_index]
        url = self.update_urls.get(component_name)

        qthread = QThread()
        worker = DownloadComponent(component_name, url)
        worker.moveToThread(qthread)
        worker.downloadFinished.connect(self.on_download_finished)
        qthread.started.connect(worker.run)
        worker.workFinished.connect(qthread.quit)
        worker.workFinished.connect(worker.deleteLater)
        qthread.finished.connect(qthread.deleteLater)

        self.qthreads.append(qthread)
        self.workers.append(worker)

        qthread.finished.connect(lambda: self.cleanup_thread(qthread, worker))

        qthread.start()

    def cleanup_thread(self, qthread, worker):
        try:
            self.qthreads.remove(qthread)
        except ValueError:
            pass
        try:
            self.workers.remove(worker)
        except ValueError:
            pass

    @Slot(str)
    def on_download_finished(self, result):
        logger.create_debug_log(
            f"Download finished for component {self.components_to_update[self.current_component_index]} \
                with result {result}",
        )
        self.current_component_index += 1
        self.start_next_download()
