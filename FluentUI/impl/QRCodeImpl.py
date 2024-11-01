import qrcode
from PIL import ImageQt
from PySide6.QtCore import Signal, Property, QRect
from PySide6.QtGui import QColor
from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.impl"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class QRCodeImpl(QQuickPaintedItem):
    textChanged = Signal()
    colorChanged = Signal()
    backgroundColorChanged = Signal()
    sizeChanged = Signal()

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        self.__text: str = ""
        self.__color: QColor = QColor(0, 0, 0, 255)
        self.__backgroundColor: QColor = QColor(255, 255, 255, 255)
        self.__size: int = 100
        self.setWidth(self.__size)
        self.setHeight(self.__size)
        self.textChanged.connect(lambda: self.update())
        self.colorChanged.connect(lambda: self.update())
        self.backgroundColorChanged.connect(lambda: self.update())
        self.sizeChanged.connect(lambda: self.updateSize())

    def updateSize(self):
        self.setWidth(self.__size)
        self.setHeight(self.__size)
        self.update()

    def paint(self, painter):
        if self.__text == "":
            return
        if len(self.__text) > 1024:
            return
        painter.save()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=0
        )
        qr.add_data(self.__text)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color=self.__color.name(QColor.NameFormat.HexRgb),
                                 back_color=self.__backgroundColor.name(QColor.NameFormat.HexRgb))
        image = ImageQt.toqimage(qr_image)
        painter.drawImage(QRect(0, 0, int(self.width()), int(self.height())), image)
        painter.restore()

    @Property(int, notify=sizeChanged)
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        if self.__size == value:
            return
        self.__size = value
        self.sizeChanged.emit()

    @Property(QColor, notify=backgroundColorChanged)
    def backgroundColor(self):
        return self.__backgroundColor

    @backgroundColor.setter
    def backgroundColor(self, value):
        if self.__backgroundColor == value:
            return
        self.__backgroundColor = value
        self.backgroundColorChanged.emit()

    @Property(QColor, notify=colorChanged)
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if self.__color == value:
            return
        self.__color = value
        self.colorChanged.emit()

    @Property(str, notify=textChanged)
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        if self.__text == value:
            return
        self.__text = value
        self.textChanged.emit()
