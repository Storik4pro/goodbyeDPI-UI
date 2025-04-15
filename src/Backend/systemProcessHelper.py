import os
from pathlib import Path
import shutil
import threading
import time
from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread, SignalInstance
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap, QImage
import psutil

from _data import DEBUG_PATH, DIRECTORY, UserConfig, logger, settings
from . import Process

CONFIG_META = "CDPIUI|ICF|sys_process_checker|1.0"
TASK_META = "CDPIUI|ECF|task|1.0"
TASK_FOLDER = Path(DEBUG_PATH+DIRECTORY, "tasks")

ENGINES = [
    "none",
    "goodbyeDPI",
    "zapret",
    "byedpi",
    "spoofdpi"
]

# Task format:
# ===========
# action : 0 = kill, 1 = run
# action_engine : 0 = None, 1 = GoodbyeDPI, 2 = Zapret, 3 = ByeDPI, 4 = SpoofDPI
# apps: same apps list formatted as [[APPNAME, APPPATH], ...]
# priority: 0 = high, 1 = medium, 2 = low
# state: 0 = running, 1 = stopped
# type: 0 = single action, 1 = track

class SystemProcessHelper(QObject):
    tasksLoaded = Signal('QVariantList')
    processCheckedStarted = Signal()
    processCheckedStopped = Signal()
    toastRequest = Signal(str, str)
    
    def __init__(self, process:Process):
        super().__init__()
        self.process = process
        self._worker = None
        self.qthread = None
        self.is_worker_alive = False
        configpath = Path(DEBUG_PATH+DIRECTORY, "data", 
                          "settings", "sys_process_checker.json")
        
        if not configpath.exists():
            configpath.parent.mkdir(parents=True, exist_ok=True)
            with open(configpath, 'w') as f:
                f.write('{}')
            self.config = UserConfig(configpath)
            self.config.set_value("metadata", CONFIG_META)
            self.config.set_value("tasks", {"sample_task": True})
        else:
            self.config = UserConfig(configpath)

        self.tasks = []
        self.tasks = self.load_tasks()
        
    @Slot(result=bool)
    def is_alive(self):
        return self.is_worker_alive
        
    @Slot(str, 'QVariantList')
    def save_task(self, filename, data:list):
        if not os.path.exists(TASK_FOLDER):
            TASK_FOLDER.mkdir(parents=True, exist_ok=True)
            
        if filename == "":
        
            _time = int(time.time())
            new_task_filename = f"basic_task_{_time}.cdpiuitask"
            new_task_path = TASK_FOLDER / new_task_filename
            with open(new_task_path, 'w') as f:
                f.write('{}')
        else:
            new_task_filename = f"{filename}.cdpiuitask"
            new_task_path = TASK_FOLDER / new_task_filename
        
        config = UserConfig(new_task_path)
        config.set_value("metadata", TASK_META)
        config.set_value("action", data[0]["action"])
        config.set_value("action_engine", data[0]["action_engine"])
        config.set_value("apps", data[0]["apps"])
        config.set_value("priority", data[0]["priority"])
        config.set_value("state", data[0]["state"])
        config.set_value("type", data[0]["type"])

        config.reload_config()
        del config
        logger.create_info_log(f"Task saved: {new_task_path}")
        self.tasks = self.load_tasks()
        self.tasksLoaded.emit(self.tasks)
        
    @Slot(str)
    def delete_task(self, filename):
        filepath = TASK_FOLDER / f"{filename}.cdpiuitask"
        self.tasks.clear()
        
        if filepath.exists():
            os.remove(filepath)
        known_tasks = self.config.get_value("tasks")
        if filename in known_tasks: del known_tasks[filename]
        self.config.set_value("tasks", known_tasks)
        self.update_task_list()
        
    def load_tasks(self):
        tasks = []
        if not os.path.exists(TASK_FOLDER):
            TASK_FOLDER.mkdir(parents=True, exist_ok=True)
            return tasks
        
        for file in TASK_FOLDER.iterdir():
            if file.suffix == ".cdpiuitask":
                config = UserConfig(file)
                config.reload_config()
                if config.get_value("metadata") != TASK_META:
                    logger.create_warning_log(f"Invalid task metadata: {file}")
                    continue
                task = {
                    "file": file.stem,
                    "action": config.get_value("action"),
                    "action_engine": config.get_value("action_engine"),
                    "apps": config.get_value("apps"),
                    "priority": config.get_value("priority"),
                    "state": config.get_value("state"),
                    "type": config.get_value("type")
                }
                known_tasks = self.config.get_value("tasks")
                if known_tasks and known_tasks.get(task["file"]) is None:
                    known_tasks.update({task["file"]: True})
                    self.config.set_value(f"tasks", known_tasks)
                    
                tasks.append(task)
        
        return tasks
    
    @Slot()
    def update_task_list(self):
        tasks = self.load_tasks()
        if self.tasks != tasks:
            self.tasks = tasks
            # !
        qt_tasks = []
        for task in tasks:
            qt_tasks.append({
                "file": task["file"],
                "action": task["action"],
                "action_engine": task["action_engine"],
                "apps": task["apps"],
                "priority": task["priority"],
                "state": task["state"],
                "type": task["type"]
            })
        self.tasksLoaded.emit(qt_tasks)
        
    @Slot(str, result='QVariantList')
    def get_task(self, task_name:str):
        task = None
        for t in self.tasks:
            if t["file"] == task_name:
                task = t
                break
        
        if task is None:
            return None
        
        qt_task = {
            "file": task["file"],
            "action": task["action"],
            "action_engine": task["action_engine"],
            "apps": task["apps"],
            "priority": task["priority"],
            "state": task["state"],
            "type": task["type"]
        }
        
        return [qt_task]
        
    @Slot(str, result=bool)
    def is_task_enabled(self, task_name:str):
        known_tasks = self.config.get_value("tasks")
        if known_tasks.get(task_name):
            return True
        return False
    
    @Slot(str, bool)
    def set_task_enabled(self, task_name:str, enabled:bool):
        known_tasks = self.config.get_value("tasks")
        if known_tasks.get(task_name):
            if enabled:
                return 
            else:
                known_tasks.update({task_name: False})
                self.config.set_value(f"tasks", known_tasks)
                return 
        else:
            if enabled:
                known_tasks.update({task_name: True})
                self.config.set_value(f"tasks", known_tasks)
                return 
            else:
                return 
            
    @Slot(result=bool)
    def is_start_process_checker_availible(self):
        if self.tasks == []:
            return False
        
        for task in self.tasks:
            known_tasks = self.config.get_value("tasks")
            if known_tasks.get(task["file"]):
                return True

        return False
    
    @Slot()
    def start_process_checker(self):
        if not self.is_start_process_checker_availible():
            return
        killMediumPriority = []
        killHighPriority = []
        killLowPriority = []
        
        runMediumPriority = []
        runHighPriority = []
        runLowPriority = []
        
        for task in self.tasks:
            known_tasks = self.config.get_value("tasks")
            if not known_tasks.get(task["file"]):
                continue
            process = {
                "name": task["apps"][0][0],
                "path": task["apps"][0][1],
                "mode": 'track' if task["type"] == 1 else 'single',
                "state": task["state"],
                "engine": task["action_engine"],
            }
            if task["action"] == 0:
                if task["priority"] == 0:
                    killHighPriority.append(process)
                elif task["priority"] == 1:
                    killMediumPriority.append(process)
                else: # task["priority"] == 2
                    killLowPriority.append(process)
            else:
                if task["priority"] == 0:
                    runHighPriority.append(process)
                elif task["priority"] == 1:
                    runMediumPriority.append(process)
                else:
                    runLowPriority.append(process)
                    
        self.processCheckedStarted.emit()
        self.toastRequest.emit('#COND:START_SUCCESS', "")
        self.process.stop_process()
        
        self.is_worker_alive = True
        self.qthread = QThread()
        self._worker = SystemProcessFindWorker()
        self._worker.setup(
            {
                "killMediumPriority": killMediumPriority,
                "killHighPriority": killHighPriority,
                "killLowPriority": killLowPriority,
                "runMediumPriority": runMediumPriority,
                "runHighPriority": runHighPriority,
                "runLowPriority": runLowPriority
            },
            self.toastRequest
        )
        self._worker.moveToThread(self.qthread)

        self.qthread.started.connect(self._worker.run)
        self._worker.stateChanged.connect(self.state_changed)
        self._worker.processAskToStop.connect(self.stop_process)
        self._worker.processAskToRun.connect(self.run_process)
        self._worker.workFinished.connect(self.work_finished)
        self._worker.workFinished.connect(self.qthread.quit)
        self._worker.workFinished.connect(self._worker.deleteLater)
        self._worker.workFinished.connect(self.processCheckedStopped)
        self.qthread.finished.connect(self.qthread.deleteLater)

        self.qthread.start()
        
    
    @Slot()
    def stop_process_checker(self):
        if self._worker:
            self._worker.stop()
            self.toastRequest.emit('#COND:STOP_SUCCESS', "")
        
    def state_changed(self, state):
        state_text = f"[SYSPROCHELPER] {state}"
        print(state_text)
        logger.create_info_log(state_text)
        
    def work_finished(self):
        self.is_worker_alive = False
        
    def stop_process(self, engine):
        if not self.process.is_process_alive():
            self.process.stop_process()
        
    def run_process(self, engine):
        if self.process.is_process_alive():
            if self.process.engine == ENGINES[engine]:
                return
            self.process.stop_process()
            
        result = self.process.start_process_manually(ENGINES[engine], None)
        print(result)
        if not result and self._worker:
            self.toastRequest.emit('#COND:FAILURE', "")
            self._worker.stop()
            self.state_changed("Unexpected error: process not started. See pseudoconsole.")
    
class SystemProcessFindWorker(QObject):
    stateChanged = Signal(str)
    processAskToStop = Signal(int)
    processAskToRun = Signal(int)
    workFinished = Signal()
    
    def __init__(self):
        super().__init__()
        self.processDict = None
        self.is_run = False
        self.signal = None
        self.stop_flag = threading.Event()
        self.lst_msg_proc_found = ""
        
    @Slot(dict)
    def setup(self, processDict, signal:SignalInstance):
        self.processDict = processDict
        self.signal = signal
        self.lst_msg_proc_found = ""
        
    @Slot()
    def run(self):
        self.is_run = True
        self.start_work()
        self.workFinished.emit()
    
    def start_work(self):    
        self.stateChanged.emit("Starting process checker...")
        while self.is_run:
            timer = 0
            while timer < settings.settings['GLOBAL'].getint('conditiontimeout') and self.is_run:
                time.sleep(1)
                timer +=1
                
            if not self.is_run:
                return
            
            self.stateChanged.emit("Updating process list...")
            dump = self.dump_processes()
            self.stateChanged.emit("Process list updated.")
            
            if self.check_process_dict(
                    self.processDict["runHighPriority"], 
                    dump, 
                    firstAction=self.processAskToRun,
                    secondAction=self.processAskToStop
                ):
                self.stateChanged.emit("High run priority process found. Starting requested send.")
                continue
            if self.check_process_dict(
                    self.processDict["killHighPriority"], 
                    dump, 
                    firstAction=self.processAskToStop,
                ):
                self.stateChanged.emit("High kill priority process found. Stopping requested send.")
                continue
            if self.check_process_dict(
                    self.processDict["runMediumPriority"], 
                    dump, 
                    firstAction=self.processAskToRun,
                    secondAction=self.processAskToStop
                ):
                self.stateChanged.emit("Medium run priority process found. Starting requested send.")
                continue
            if self.check_process_dict(
                    self.processDict["killMediumPriority"], 
                    dump, 
                    firstAction=self.processAskToStop,
                ):
                self.stateChanged.emit("Medium kill priority process found. Stopping requested send.")
                continue
            if self.check_process_dict(
                    self.processDict["runLowPriority"], 
                    dump, 
                    firstAction=self.processAskToRun,
                    secondAction=self.processAskToStop
                ):
                self.stateChanged.emit("Low run priority process found. Starting requested send.")
                continue
            if self.check_process_dict(
                    self.processDict["killLowPriority"], 
                    dump, 
                    firstAction=self.processAskToStop,
                ):
                self.stateChanged.emit("Low kill priority process found. Stopping requested send.")
                continue
            
            self.stateChanged.emit("No process found. No action needed.")
            
    
    def check_process_dict(self, processDict, dump, 
                           firstAction:SignalInstance=None, secondAction:SignalInstance=None):
        for process in processDict:
            processName = process["name"]
            processPath = process["path"]
            processMode = process["mode"]
            processEngine = process["engine"]
            processState = process["state"]
            pid = self.search_process(
                dump, processName, processPath if processPath!="" else None
            )
            if (processState == 1 and not pid and self.signal and 
                self.lst_msg_proc_found != processName):
                self.lst_msg_proc_found = processName
                self.signal.emit('#COND:PROC_NOT_FOUND', processName) 

            if processState != 1 and pid and self.signal and self.lst_msg_proc_found != processName:
                self.lst_msg_proc_found = processName
                self.signal.emit('#COND:PROC_FOUND', processName) 
            
            if processState == 1 and not pid:
                self.stateChanged.emit(
                    f"Process {processName} not found."
                )
                if firstAction:
                    firstAction.emit(processEngine)
                return True
            elif processState == 1 and processMode == "track" and pid:
                self.stateChanged.emit(
                    f"Found {processName} process [PID:{pid}]."
                )
                if secondAction:
                    secondAction.emit(processEngine)
                continue
            elif processState == 1 and pid:
                self.stateChanged.emit(
                    f"Found {processName} process [PID:{pid}]."
                )
                if secondAction:
                    secondAction.emit(processEngine)
                continue
              
            if processMode == "track" and pid:
                self.stateChanged.emit(
                    f"Found {processName} process [PID:{pid}]."
                )
                if firstAction:
                    firstAction.emit(processEngine)
                return pid
            elif processMode == "track" and not pid:
                self.stateChanged.emit(
                    f"Process {processName} not found."
                )
                if secondAction:
                    secondAction.emit(processEngine)
                continue
            elif pid:
                self.stateChanged.emit(
                    f"Found {processName} process [PID:{pid}]."
                )
                if firstAction:
                    firstAction.emit(processEngine)
                return pid
        return None
    
    def is_uwp_folder(self, path:str):
        appx_manifest = Path(path, 'AppxManifest.xml')
        return os.path.isdir(path) and os.path.exists(path) and os.path.exists(appx_manifest)
                
    def search_process(self, dump, processName, processPath=None):
        processPath = os.path.normpath(processPath) if processPath else None
        for process in dump:
            if process["exe"] is None:
                continue
            if processPath and self.is_uwp_folder(processPath):
                exe_path_abs = os.path.abspath(process["exe"])
                uwp_app_path = os.path.abspath(processPath)
                try:
                    if os.path.commonpath([exe_path_abs, uwp_app_path]) == uwp_app_path:
                        return process["pid"]
                except ValueError:
                    pass
            if processPath and process["exe"] == processPath:
                return process["pid"]
            elif processName and process["name"].lower() == processName.lower():
                return process["pid"]
        return None
                
    def dump_processes(self):
        dump = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                info = proc.info
                dump.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'exe': info['exe']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return dump
    
    def stop(self):
        self.is_run = False
