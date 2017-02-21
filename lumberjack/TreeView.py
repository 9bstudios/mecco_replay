# python

import lxifc, lx

from TreeData import *
from TreeNode import *
from util import *
from var import *

class TreeView( lxifc.TreeView,
                lxifc.Tree,
                lxifc.ListenerPort,
                lxifc.Attributes ):

    # Gloabal list of all created tree views.
    # These are used for shape and attribute changes
    _listenerClients = {}

    # The root TreeNode() object
    _root = None

    def __init__(self, node, curIndex = 0):
        self.m_currentNode = node
        self.m_currentIndex = curIndex

        # The only node without a parent is the root
        if not self.m_currentNode.parent:
            self.__class__._root = self

    # --------------------------------------------------------------------------------------------------
    # Listener port
    # --------------------------------------------------------------------------------------------------

    @classmethod
    def addListenerClient(cls,listener):
        """Whenever a new tree view is created, we will add a copy of its
        listener so that it can be notified of attribute or shape changes"""
        treeListenerObj = lx.object.TreeListener(listener)
        cls._listenerClients[treeListenerObj.__peekobj__()] = treeListenerObj

    @classmethod
    def removeListenerClient(cls,listener):
        """When a view is destroyed, it will be removed from the list of clients
        that need notification."""
        treeListenerObject = lx.object.TreeListener(listener)
        if cls._listenerClients.has_key(treeListenerObject.__peekobj__()):
            del  cls._listenerClients[treeListenerObject.__peekobj__()]

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

    #---  --------------------------------------------------------------------

    def lport_AddListener(self,obj):
        """Called from core code with the object that wants to
        bind to the listener port"""
        self.addListenerClient(obj)

    def lport_RemoveListener(self,obj):
        """Called from core when a listener needs to be removed from
        the port."""
        self.removeListenerClient(obj)

    # --------------------------------------------------------------------------------------------------
    # Target layer in the tree
    # --------------------------------------------------------------------------------------------------

    def targetNode(self):
        """Returns the targeted layer node in the current tier"""
        return self.m_currentNode.children[ self.m_currentIndex ]

    # --------------------------------------------------------------------------------------------------
    # Each time the tree is spawned, we create a copy of ourselves at current
    # location in the tree and return it
    # --------------------------------------------------------------------------------------------------

    def tree_Spawn(self, mode):
        """Spawn a new instance of this tier in the tree."""

        # create an instance of our current location in the tree
        newTree = TreeView(self.m_currentNode,self.m_currentIndex)

        # Convert to a tree interface
        newTreeObj = lx.object.Tree(newTree)

        if mode == lx.symbol.iTREE_PARENT:
            # move the tree to the parent tier
            newTreeObj.ToParent()

        elif mode == lx.symbol.iTREE_CHILD:
            # move tree to child tier
            newTreeObj.ToChild()

        elif mode == lx.symbol.iTREE_ROOT:
            #move tree to root tier
            newTreeObj.ToRoot()

        return newTreeObj

    def tree_ToParent(self):
        """Step up to the parent tier and set the selection in this tier to the
        current items index"""
        m_parent = self.m_currentNode.parent

        if m_parent:
            self.m_currentIndex = m_parent.children.index(self.m_currentNode)
            self.m_currentNode = m_parent

    def tree_ToChild(self):
        """Move to the child tier and set the selected node"""
        self.m_currentNode = self.m_currentNode.children[self.m_currentIndex]

    def tree_ToRoot(self):
        """Move back to the root tier of the tree"""
        self.m_currentNode = self._root

    def tree_IsRoot(self):
        """Check if the current tier in the tree is the root tier"""
        if self.m_currentNode == self._root:
            return True
        else:
            return False

    def tree_ChildIsLeaf(self):
        """If the current tier has no children then it is
        considered a leaf"""
        if len( self.m_currentNode.children ) > 0:
            return False
        else:
            return True

    def tree_Count(self):
        """Returns the number of nodes in this tier of
        the tree"""
        return len( self.m_currentNode.children )

    def tree_Current(self):
        """Returns the index of the currently targeted item in
        this tier"""
        return self.m_currentIndex

    def tree_SetCurrent(self, index):
        """Sets the index of the item to target in this tier"""
        self.m_currentIndex = index

    def tree_ItemState(self, guid):
        """Returns the item flags that define the state."""
        return self.targetNode().state

    def tree_SetItemState(self, guid, state):
        """Set the item flags that define the state."""
        self.targetNode().state = state


    # --------------------------------------------------------------------------------------------------
    # Tree view
    # --------------------------------------------------------------------------------------------------

    def treeview_StoreState(self, uid):
        lx.notimpl()

    def treeview_RestoreState(self, uid):
        lx.notimpl()

    def treeview_ColumnCount(self):
        return len(self._root.columns)

    def treeview_ColumnByIndex(self, columnIndex):
        return self._root.columns[columnIndex]

    def treeview_ToPrimary(self):
        """Move the tree to the primary selection"""
        if self.m_currentNode.primary:
            self.m_currentNode = True
            self.tree_ToParent()
            return True
        return False

    def treeview_IsSelected(self):
        return self.targetNode().selected

    def treeview_Select(self, mode):

        if mode == lx.symbol.iTREEVIEW_SELECT_PRIMARY:
            self._root.deselect_descendants()
            self.targetNode().selected = True

        elif mode == lx.symbol.iTREEVIEW_SELECT_ADD:
            self.targetNode().selected = True

        elif mode == lx.symbol.iTREEVIEW_SELECT_REMOVE:
            self.targetNode().selected = False

        elif mode == lx.symbol.iTREEVIEW_SELECT_CLEAR:
            self._root.deselect_descendants()

    def treeview_CellCommand(self, columnIndex):
        # TODO
        # Support cell command queries (must be queries).
        # Must also implement BatcchCommand, cannot do one without the other.
        # Usually the cell and batch commands are the same, but the cell
        # command has an optional argument set that tells the command to target
        # a specific row instead of the entire selection.

        # Such as, "item.channel enable ? item:someItemID" for the cell command,
        # vs "item.channel enable ?" for the batch command -- the batch version
        # targets all selected rows by looking at the selection.

        # Colors aren't currently supported, BTW; it's just strings, ints,
        # floats and popups.  And async monitors.
        lx.notimpl()

    def treeview_BatchCommand(self, columnIndex):
        lx.notimpl()

    def treeview_ToolTip(self, columnIndex):
        columns = self._root.columns
        tooltip = self.targetNode().values[columns[n]].tooltip
        if tooltip:
            return tooltip
        lx.notimpl()

    def treeview_BadgeType(self, columnIndex, badgeIndex):
        lx.notimpl()

    def treeview_BadgeDetail(self, columnIndex, badgeIndex, badgeDetail):
        lx.notimpl()

    def treeview_IsInputRegion(self, columnIndex, regionID):
        lx.notimpl()

    def treeview_SupportedDragDropSourceTypes(self, columnIndex):
        lx.notimpl()

    def treeview_GetDragDropSourceObject(self, columnIndex, type):
        lx.notimpl()

    def treeview_GetDragDropDestinationObject(self, columnIndex, location):
        lx.notimpl()

    # --------------------------------------------------------------------------------------------------
    # Attributes
    # --------------------------------------------------------------------------------------------------

    def attr_Count(self):
        return len(self._root.columns)

    def attr_GetString(self, index):
        columns = self._root.columns
        node = self.targetNode()

        for n in range(len(columns)):
            if index == n:
                try:
                    # Print the `display_value` in the cell
                    return node.values[columns[n]].display_value
                except:
                    # Column is empty
                    pass
