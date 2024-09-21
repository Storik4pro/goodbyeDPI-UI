
import subprocess
import sys
from _settings.Gallery.main import run_qt_app
from multiprocessing import Pipe, Process


def start_qt_settings():
    parent_conn, child_conn = Pipe()
    p = Process(target=run_qt_app, args=(child_conn,))
    p.start()
    return parent_conn, p
