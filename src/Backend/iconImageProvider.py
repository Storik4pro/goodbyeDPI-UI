from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtQuick import QQuickImageProvider
import urllib.parse
from Backend.proxyHelper import get_icon_from_exe


class IconImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)
        self.icons_cache = {}
        self.default_icon = None
        
    def preloadPixmap(self, exe_path):
        try:
            pixmap = get_icon_from_exe(exe_path)
            if pixmap:
                self.icons_cache[exe_path] = pixmap
                return pixmap
        except Exception as e:
            print(f"Error loading icon: {e}")
            
        if self.default_icon is None: 
            self.default_icon = QPixmap.fromImage(QImage(":/qt/qml/GoodbyeDPI_UI/res/image/app.png"))
        
        self.icons_cache[exe_path] = self.default_icon
        
        return self.default_icon
    
    def requestPixmap(self, id, size, requestedSize):
        exe_path = urllib.parse.unquote(id).replace('C:Program', 'C:\\Program')
        
        if exe_path in self.icons_cache:
            return self.icons_cache[exe_path]
        
        return self.preloadPixmap(exe_path)
    