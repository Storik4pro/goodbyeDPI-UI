import logging
from . import AppLogger
from _data import VERSION, DIRECTORY
HOT_DEBUG_VERSION = VERSION + '_hotdebug'

class HotDebugger:
    def __init__(self):
        self.logger = None
        
    def setup(self):
        self.logger = AppLogger(HOT_DEBUG_VERSION, 'hot_debug', DIRECTORY, logging.DEBUG)
        
        self.logger.create_info_log('Hot debugger is setup correctly.')
        
    def log(self, info):
        if self.logger is None:
            return
            
        self.logger.create_info_log(info)

hot_debugger = HotDebugger()