from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal, Property, Slot, QObject
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "FluentUI.Controls"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class TreeNode(QObject):
    rowDataChanged = Signal()
    depthChanged = Signal()
    expandedChanged = Signal()
    nodeParentChanged = Signal()
    nodeChildrenChanged = Signal()

    @Property(QObject, notify=nodeChildrenChanged)
    def nodeChildren(self):
        return self.__nodeChildren

    @nodeChildren.setter
    def nodeChildren(self, value):
        if self.__nodeChildren == value:
            return
        self.__nodeChildren = value
        self.nodeChildrenChanged.emit()

    @Property(QObject, notify=nodeParentChanged)
    def nodeParent(self):
        return self.__nodeParent

    @nodeParent.setter
    def nodeParent(self, value):
        if self.__nodeParent == value:
            return
        self.__nodeParent = value
        self.nodeParentChanged.emit()

    @Property(bool, notify=expandedChanged)
    def expanded(self):
        return self.__expanded

    @expanded.setter
    def expanded(self, value):
        if self.__expanded == value:
            return
        self.__expanded = value
        self.expandedChanged.emit()

    @Property(int, notify=depthChanged)
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, value):
        if self.__depth == value:
            return
        self.__depth = value
        self.depthChanged.emit()

    @Property(dict, notify=rowDataChanged)
    def rowData(self):
        return self.__rowData

    @rowData.setter
    def rowData(self, value):
        if self.__rowData == value:
            return
        self.__rowData = value
        self.rowDataChanged.emit()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__rowData = {}
        self.__depth = 0
        self.__expanded = True
        self.__nodeParent = None
        self.__nodeChildren = []

    def hasChildren(self):
        return bool(self.__nodeChildren)

    def appendChildren(self, node):
        self.__nodeChildren.append(node)

    def removeChildren(self, node):
        self.__nodeChildren.remove(node)

    def visible(self):
        p = self.__nodeParent
        while p:
            if not p.expanded:
                return False
            p = p.__nodeParent
        return True


@QmlElement
class TreeDataGridModel(QAbstractListModel):
    countChanged = Signal()
    sourceDataChanged = Signal()
    displayDataChanged = Signal()

    @Property(list, notify=sourceDataChanged)
    def sourceData(self):
        return self.__sourceData

    @sourceData.setter
    def sourceData(self, value):
        if self.__sourceData == value:
            return
        self.__sourceData = value
        self.sourceDataChanged.emit()

    @Property(list, notify=displayDataChanged)
    def displayData(self):
        return self.__displayData

    @displayData.setter
    def displayData(self, value):
        if self.__displayData == value:
            return
        self.__displayData = value
        self.displayDataChanged.emit()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__sourceData = []
        self.__roles = []
        self.__displayData = []
        self.__treeRoot = None

        def handleRowData():
            self.beginResetModel()
            if self.__displayData:
                self.__updateRoles(self.__displayData[0].rowData)
            self.endResetModel()
            self.countChanged.emit()

        self.displayDataChanged.connect(lambda: handleRowData())
        self.sourceDataChanged.connect(lambda: self.handleSourceData())

    def getCount(self):
        return self.rowCount()

    count = Property(int, getCount, notify=countChanged)

    def rowCount(self, parent=QModelIndex()):
        return len(self.__displayData)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.__displayData) or index.row() < 0:
            return None
        roleName = self.__roles[role]
        node = self.__displayData[index.row()]
        if roleName == 'depth':
            return node.depth
        elif roleName == 'expanded':
            return node.expanded
        elif roleName == 'hasChildren':
            return node.hasChildren()
        else:
            return node.rowData[roleName]

    def roleNames(self):
        return {i: role.encode() for i, role in enumerate(self.__roles)}

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        row = index.row()
        if not index.isValid() or row >= self.rowCount() or row < 0:
            return False
        roleName = self.__roles[role]
        node = self.__displayData[row]
        node.rowData[roleName] = value
        return True

    def handleSourceData(self):
        if not self.__sourceData:
            self.clear()
            return

        self.__treeRoot = TreeNode()
        treeData = []
        reverseData = self.__sourceData[::-1]

        while reverseData:
            data = reverseData.pop()
            node = TreeNode(self)
            node.rowData = data
            node.expanded = data.get("expanded", False)
            node.nodeParent = data.get("__parent", None)
            node.depth = data.get("__depth", 0)
            if node.nodeParent:
                node.nodeParent.appendChildren(node)
            else:
                node.nodeParent = self.__treeRoot
                self.__treeRoot.appendChildren(node)

            if "children" in data:
                children = data["children"]
                if children:
                    reverseChildren = children[::-1]
                    for child in reverseChildren:
                        child_map = child
                        child_map["__depth"] = data.get("__depth", 0) + 1
                        child_map["__parent"] = node
                        reverseData.append(child_map)
            if node.nodeParent.expanded:
                treeData.append(node)
        self.clear()
        self.displayData = treeData

    @Slot()
    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.__displayData) - 1)
        self.__displayData.clear()
        self.endRemoveRows()
        self.countChanged.emit()

    @Slot(int, result=dict)
    def get(self, index):
        if 0 <= index < len(self.__displayData):
            return self.__displayData[index].rowData
        return None

    @Slot(int)
    def collapse(self, row: int):
        data = self.__displayData[row]
        if not data.expanded:
            return
        data.expanded = False
        self.dataChanged.emit(self.index(row, 0), self.index(row, 0))
        removeCount = 0
        for i in range(row + 1, len(self.__displayData)):
            obj = self.__displayData[i]
            if obj.depth <= data.depth:
                break
            removeCount += 1
        self.__removeRows(row + 1, removeCount)

    @Slot(int)
    def expand(self, row: int):
        data = self.__displayData[row]
        if data.expanded:
            return
        data.expanded = True
        self.dataChanged.emit(self.index(row, 0), self.index(row, 0))
        insertData = []
        stack = data.nodeChildren[::-1]
        while len(stack) > 0:
            item = stack.pop()
            if item.visible():
                insertData.append(item)
            children = item.nodeChildren[::-1]
            if len(children) != 0:
                for c in children:
                    stack.append(c)
        self.__insertRows(row + 1, insertData)

    def __removeRows(self, row: int, count: int):
        if (row < 0) or (row + count) > len(self.__displayData) or (count == 0):
            return
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        firstPart = self.__displayData[:row]
        secondPart = self.__displayData[row + count:]
        self.__displayData.clear()
        self.__displayData.extend(firstPart)
        self.__displayData.extend(secondPart)
        self.endRemoveRows()

    def __insertRows(self, row: int, data: list):
        if row < 0 or row > len(self.__displayData) or len(data) == 0:
            return
        self.beginInsertRows(QModelIndex(), row, row + len(data) - 1)
        firstPart = self.__displayData[:row]
        secondPart = self.__displayData[row:]
        self.__displayData.clear()
        self.__displayData.extend(firstPart)
        self.__displayData.extend(data)
        self.__displayData.extend(secondPart)
        self.endInsertRows()

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
        self.__insertRole("hasChildren")
        self.__insertRole("depth")
        self.__insertRole("expanded")
        for key in data.keys():
            if key not in self.__roles:
                self.__insertRole(key)
