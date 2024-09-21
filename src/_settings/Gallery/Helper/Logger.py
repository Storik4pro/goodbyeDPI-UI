import logging
import os
import sys
import threading

from PySide6.QtCore import QDir, qInstallMessageHandler, QtMsgType, QStandardPaths, QDateTime, QSysInfo

__logging: logging.Logger
__fileHandler: logging.FileHandler
__formatFileHandler: logging.FileHandler
__stdoutHandler: logging.StreamHandler
__formatStdoutHandler: logging.StreamHandler


class __CustomFormatter(logging.Formatter):
    def format(self, record):
        record.threadId = threading.get_ident()
        return super().format(record)


def __get_level_by_msg_type(msg_type):
    if msg_type == QtMsgType.QtFatalMsg:
        return logging.FATAL
    if msg_type == QtMsgType.QtCriticalMsg:
        return logging.CRITICAL
    if msg_type == QtMsgType.QtWarningMsg:
        return logging.WARNING
    if msg_type == QtMsgType.QtInfoMsg:
        return logging.INFO
    if msg_type == QtMsgType.QtDebugMsg:
        return logging.DEBUG
    return logging.DEBUG


def __open_format():
    __logging.removeHandler(__fileHandler)
    __logging.removeHandler(__stdoutHandler)
    __logging.addHandler(__formatFileHandler)
    __logging.addHandler(__formatStdoutHandler)


def __close_format():
    __logging.removeHandler(__formatFileHandler)
    __logging.removeHandler(__formatStdoutHandler)
    __logging.addHandler(__fileHandler)
    __logging.addHandler(__stdoutHandler)


def __message_handler(msg_type, context, message):
    if message == "Retrying to obtain clipboard.":
        return
    global __logging
    global __fileHandler
    global __formatFileHandler
    global __stdoutHandler
    global __formatStdoutHandler
    __close_format()
    file_and_line_log_str = ""
    if context.file:
        str_file_tmp = context.file
        ptr = str_file_tmp.rfind('/')
        if ptr != -1:
            str_file_tmp = str_file_tmp[ptr + 1:]
        ptr_tmp = str_file_tmp.rfind('\\')
        if ptr_tmp != -1:
            str_file_tmp = str_file_tmp[ptr_tmp + 1:]
        file_and_line_log_str = f"[{str_file_tmp}:{str(context.line)}]"
    level = __get_level_by_msg_type(msg_type)
    final_message = (f"{QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss.zzz')}[{logging.getLevelName(level)}]"
                     f"{file_and_line_log_str}[{threading.get_ident()}]:{message}")
    __logging.log(level, final_message)
    __open_format()


def setup(name, level=logging.DEBUG):
    global __logging
    global __fileHandler
    global __formatFileHandler
    global __stdoutHandler
    global __formatStdoutHandler

    __logging = logging.getLogger(name)
    __logging.setLevel(level)
    log_file_name = f"{name}_{QDateTime.currentDateTime().toString('yyyyMMdd')}.log"
    log_dir_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation) + "/log"
    log_dir = QDir(log_dir_path)
    if not log_dir.exists():
        log_dir.mkpath(log_dir_path)
    log_file_path = log_dir.filePath(log_file_name)
    __fileHandler = logging.FileHandler(log_file_path)
    __stdoutHandler = logging.StreamHandler(sys.stdout)
    __formatFileHandler = logging.FileHandler(log_file_path)
    __formatStdoutHandler = logging.StreamHandler(sys.stdout)
    fmt = __CustomFormatter("%(asctime)s[%(levelname)s][%(filename)s:%(lineno)s][%(threadId)d] %(message)s")
    __formatFileHandler.setFormatter(fmt)
    __formatStdoutHandler.setFormatter(fmt)
    __logging.addHandler(__formatStdoutHandler)
    __logging.addHandler(__formatFileHandler)
    qInstallMessageHandler(__message_handler)
    __logging.info(f"===================================================")
    __logging.info(f"[AppName] {name}")
    __logging.info(f"[AppPath] {sys.argv[0]}")
    __logging.info(f"[ProcessId] {os.getpid()}")
    __logging.info(f"[DeviceInfo]")
    __logging.info(f"  [DeviceId] {QSysInfo.machineUniqueId().toStdString()}")
    __logging.info(f"  [Manufacturer] {QSysInfo.productVersion()}")
    __logging.info(f"  [CPU_ABI] {QSysInfo.currentCpuArchitecture()}")
    __logging.info(f"[LOG_LEVEL] {logging.getLevelName(level)}")
    __logging.info(f"[LOG_PATH] {log_file_path}")
    __logging.info(f"===================================================")


def logger():
    return __logging
