from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal, Property, Slot, QItemSelectionModel, \
    QItemSelection
from PySide6.QtQml import QmlElement, QJSValue

QML_IMPORT_NAME = "FluentUI.Controls"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class DataGridModel(QAbstractListModel):
    countChanged = Signal()
    sourceDataChanged = Signal()

    @Property(list, notify=sourceDataChanged)
    def sourceData(self):
        return self.__sourceData

    @sourceData.setter
    def sourceData(self, value):
        if self.__sourceData == value:
            return
        self.__sourceData = value
        self.sourceDataChanged.emit()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__sourceData = []
        self.__roles = []

        def handleRowData():
            self.beginResetModel()
            if self.__sourceData:
                self.__updateRoles(self.__sourceData[0])
            self.endResetModel()
            self.countChanged.emit()

        self.sourceDataChanged.connect(lambda: handleRowData())

    def getCount(self):
        return self.rowCount()

    count = Property(int, getCount, notify=countChanged)

    def rowCount(self, parent=QModelIndex()):
        return len(self.__sourceData)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.__sourceData) or index.row() < 0:
            return None
        return self.__sourceData[index.row()].get(self.__roles[role])

    def roleNames(self):
        return {i: role.encode() for i, role in enumerate(self.__roles)}

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        row = index.row()
        if not index.isValid() or row >= self.rowCount() or row < 0:
            return False
        self.__sourceData[row][self.__roles[role]] = value
        self.__emitItemsChanged(index.row(), 1, [role])
        return True

    @Slot()
    def clear(self):
        self.beginResetModel()
        self.__sourceData.clear()
        self.endResetModel()

    @Slot(QJSValue)
    def append(self, data):
        if isinstance(data, list):
            if data:
                self.__updateRoles(data[0])
                self.beginInsertRows(QModelIndex(), len(self.__sourceData), len(self.__sourceData) + len(data) - 1)
                self.__sourceData.extend(data)
                self.endInsertRows()
                self.countChanged.emit()
        else:
            self.insert(len(self.__sourceData), data)

    @Slot(int, result=dict)
    def get(self, index):
        if 0 <= index < len(self.__sourceData):
            return self.__sourceData[index]
        return None

    @Slot(int, int, int, result=bool)
    def move(self, from_, to_, n):
        if from_ < 0 or from_ >= self.rowCount() or to_ < 0 or to_ >= self.rowCount() or n < 0 or (
                from_ + n) > self.rowCount():
            return False
        self.beginMoveRows(QModelIndex(), from_, from_ + n - 1, QModelIndex(), to_ + n if to_ > from_ else to_)
        if from_ > to_:
            tfrom = from_
            tto = to_
            from_ = tto
            to_ = tto + n
            n = tfrom - tto

        store = []
        for i in range(to_ - from_):
            store.append(self.__sourceData[from_ + n + i])
        for i in range(n):
            store.append(self.__sourceData[from_ + i])
        for i in range(len(store)):
            self.__sourceData[from_ + i] = store[i]
        self.endMoveRows()
        return True

    @Slot(int, result=bool)
    @Slot(int, int, result=bool)
    def remove(self, index, count=1):
        if index < 0 or index + count > self.rowCount() or count <= 0:
            return False
        self.beginRemoveRows(QModelIndex(), index, index + count - 1)
        del self.__sourceData[index:index + count]
        self.endRemoveRows()
        return True

    @Slot(int, QJSValue, result=bool)
    def insert(self, index, data):
        if index < 0 or index > self.rowCount():
            return False
        obj = data.toVariant()
        self.__updateRoles(obj)
        self.beginInsertRows(QModelIndex(), index, index)
        self.__sourceData.insert(index, obj)
        self.endInsertRows()
        self.countChanged.emit()
        return True

    @Slot(int, QJSValue, result=bool)
    def set(self, index, data):
        if index < 0 or index > self.rowCount() or self.rowCount() == 0:
            return False
        obj = data.toVariant()
        self.__sourceData[index] = obj
        self.dataChanged.emit(self.createIndex(index, 0), self.createIndex(index, 0))
        return True

    @Slot(list)
    def removeItems(self, indexes):
        sorted_indexes = sorted(indexes, key=lambda x: x.row(), reverse=True)
        if len(sorted_indexes) > 50:
            self.beginResetModel()
            for index in sorted_indexes:
                row = index.row()
                del self.__sourceData[row]
            self.endResetModel()
        else:
            for index in sorted_indexes:
                row = index.row()
                self.beginRemoveRows(QModelIndex(), row, row)
                del self.__sourceData[row]
                self.endRemoveRows()

    @Slot(QItemSelectionModel, int, int)
    def selectRange(self, selectionModel, startRow, endRow):
        if not selectionModel:
            return
        top_left = self.index(startRow, 0)
        bottom_right = self.index(endRow, 0)
        selection = QItemSelection(top_left, bottom_right)
        selectionModel.select(selection,
                              QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)

    def __emitItemsChanged(self, index, count, roles):
        if count > 0:
            self.dataChanged.emit(self.index(index), self.index(index + count - 1), roles)

    def __insertRole(self, name):
        if name not in self.__roles:
            self.__roles.append(name)

    def __updateRoles(self, data):
        self.__roles.clear()
        self.__insertRole("height")
        self.__insertRole("minimumHeight")
        self.__insertRole("maximumHeight")
        for key in data.keys():
            if key not in self.__roles:
                self.__insertRole(key)
