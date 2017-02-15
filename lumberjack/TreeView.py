# python

import lxifc, lx

class TreeView(lxifc.TreeView,
                    lxifc.Tree,
                    lxifc.ListenerPort,
                    lxifc.Attributes
                    ):

    _listenerClients = {}

    def __init__(self, node=None, current_index=0):

        if node is None:
            node = _BATCH.tree()

        self.m_currentNode = node
        self.m_currentIndex = current_index

    @classmethod
    def addListenerClient(cls, listener):
        tree_listener_obj = lx.object.TreeListener(listener)
        cls._listenerClients[tree_listener_obj.__peekobj__()] = tree_listener_obj

    @classmethod
    def removeListenerClient(cls, listener):
        tree_listener_object = lx.object.TreeListener(listener)
        if tree_listener_object.__peekobj__() in cls._listenerClients:
            del cls._listenerClients[tree_listener_object.__peekobj__()]

    @classmethod
    def notify_NewShape(cls):
        for client in cls._listenerClients.values():
            if client.test():
                client.NewShape()

    @classmethod
    def notify_NewAttributes(cls):
        for client in cls._listenerClients.values():
            if client.test():
                client.NewAttributes()

    def lport_AddListener(self, obj):
        self.addListenerClient(obj)

    def lport_RemoveListener(self, obj):
        self.removeListenerClient(obj)

    def targetNode(self):
        return self.m_currentNode.children()[self.m_currentIndex]

    def tree_Spawn(self, mode):
        new_tree = TreeView(self.m_currentNode, self.m_currentIndex)
        new_tree_obj = lx.object.Tree(new_tree)

        if mode == lx.symbol.iTREE_PARENT:
            new_tree_obj.ToParent()

        elif mode == lx.symbol.iTREE_CHILD:
            new_tree_obj.ToChild()

        elif mode == lx.symbol.iTREE_ROOT:
            new_tree_obj.ToRoot()

        return new_tree_obj

    def tree_ToParent(self):
        m_parent = self.m_currentNode.parent()

        if m_parent:
            self.m_currentIndex = m_parent.children().index(self.m_currentNode)
            self.m_currentNode = m_parent

    def tree_ToChild(self):
        self.m_currentNode = self.m_currentNode.children()[self.m_currentIndex]

    def tree_ToRoot(self):
        self.m_currentNode = _BATCH.tree()

    def tree_IsRoot(self):
        if self.m_currentNode == _BATCH.tree():
            return True
        else:
            return False

    def tree_ChildIsLeaf(self):
        if len(self.m_currentNode.children()) > 0:
            return False
        else:
            return True

    def tree_Count(self):
        return len(self.m_currentNode.children())

    def tree_Current(self):
        return self.m_currentIndex

    def tree_SetCurrent(self, index):
        self.m_currentIndex = index

    def tree_ItemState(self, guid):
        return self.targetNode().state()

    def tree_SetItemState(self, guid, state):
        self.targetNode().set_state(state)

    def treeview_ColumnCount(self):
        return len(_BATCH.tree().columns())

    def treeview_ColumnByIndex(self, columnIndex):
        return _BATCH.tree().columns()[columnIndex]

    def treeview_ToPrimary(self):
        if self.m_currentNode.primary():
            self.m_currentNode = self.m_currentNode.primary()
            self.tree_ToParent()
            return True
        return False

    def treeview_IsSelected(self):
        return self.targetNode().is_selected()

    def treeview_Select(self, mode):

        if mode == lx.symbol.iTREEVIEW_SELECT_PRIMARY:
            _BATCH.tree().clear_selection()

            if self.targetNode().selectable():
                self.targetNode().set_selected()
            else:
                self.targetNode().parent().set_selected()

        elif mode == lx.symbol.iTREEVIEW_SELECT_ADD and self.targetNode().selectable():
            self.targetNode().set_selected()

        elif mode == lx.symbol.iTREEVIEW_SELECT_REMOVE:
            self.targetNode().set_selected(False)

        elif mode == lx.symbol.iTREEVIEW_SELECT_CLEAR:
            _BATCH.tree().clear_selection()

    def treeview_ToolTip(self, column_index):
        tooltip = self.targetNode().tooltip(column_index)
        if tooltip:
            return tooltip
        lx.notimpl()

    def treeview_IsInputRegion(self, column_index, regionID):
        if regionID == 0:
            return True
        if self.targetNode().node_region() == REGIONS[regionID]:
            return True

        return False

    def attr_Count(self):
        return len(_BATCH.tree().columns())

    def attr_GetString(self, index):
        if index == 0:
            return self.targetNode().display_name()

        elif self.targetNode().display_value():
            return self.targetNode().display_value()

        else:
            return EMPTY
