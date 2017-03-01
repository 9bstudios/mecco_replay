# python

import lxifc, lx

class TreeView( lxifc.TreeView,
                lxifc.Tree,
                lxifc.ListenerPort,
                lxifc.Attributes ):

    """TreeView interface for the MODO API. Boilerplate pulled from:
    http://modo.sdk.thefoundry.co.uk/wiki/Python_Treeview_Example

    There is a lot of dark magic involved in the MODO API. Don't mess
    with this unless you know what you're doing."""

    # Gloabal list of all created tree views.
    # These are used for shape and attribute changes
    _listenerClients = {}

    def __init__(self, node = None, curIndex = 0, root = None):
        # `self.root` returns the root TreeNode() object for the treeview.
        # Fun fact about MODO API inheritance: if our TreeView class were to
        # inherit `object` as is the norm, everything breaks. This causes various
        # problems with inheritance. For one, class variables are only reliable
        # if they are defined during `__init__()`, NOT up above it as normal.

        # Note: TreeView classes require a root TreeNode object. Without this,
        # Bad Things happen. Be sure to include this parameter when instantiating
        # the class for the first time.
        if root:
            self.__class__._root = root

        # Because TreeView() does not inherit `object`, you cannot put the _root
        # classvariable declaration outside of __init__() without affecting all
        # subclasses.
        try:
            self._root
        except AttributeError:
            lx.out ('%s requires a root TreeNode on init.' % self.__name__)
            raise Exception('%s requires a root TreeNode on init.' % self.__name__)

        if node is None:
            node = self._root

        # Because TreeView() does not inherit `object`, you cannot put the
        # classvariable declaration outside of __init__() without affecting all
        # subclasses.
        try:
            self._primary_column_position
        except AttributeError:
            self.__class__._primary_column_position = 0

        self.m_currentNode = node
        self.m_currentIndex = curIndex

    # --------------------------------------------------------------------------------------------------
    # Listener port
    # --------------------------------------------------------------------------------------------------

    # Wanted to use a property for this instead of a setter method, but wasn't able
    # to make it work for some reason.
    def set_primary_column_position(self, value):
        """Moves the primary column to the specified column index.

        The "primary" column (i.e. the one with the twirly carrot icon for hide/show
        node children) is always the first column in the columns list, but is not
        necessarily left-most in the TreeView (witness the items list).

        To move it over to the selcond-from-left slot, for example, provide this
        function a value of 1."""
        self.__class__._primary_column_position = value

    def root():
        doc = """Root TreeNode object for the TreeView. This is typically set only
        once during the Lumberjack blessing."""
        def fget(self):
            return self._root
        def fset(self, value):
            self.__class__._root = value
        return locals()

    root = property(**root())

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
            del cls._listenerClients[treeListenerObject.__peekobj__()]

    @classmethod
    def notify_NewShape(cls):
        """Called whenever nodal hierarchy changes in any way. Slower than
        `notify_NewAttributes`, but necessary when nodes are added/removed/reparented."""
        for client in cls._listenerClients.values():
            if client.test():
                client.NewShape()

    @classmethod
    def notify_NewAttributes(cls):
        """Called when cell values are updated, but nodal hierarchy is unchanged.
        Faster than `notify_NewShape`, but does not update added/removed/reparented
        nodes."""
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
        newTree = self.__class__(self.m_currentNode, self.m_currentIndex)

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
            self.m_currentIndex = self.m_currentNode.index
            self.m_currentNode = m_parent
            return True
        return False

    def tree_ToChild(self):
        """Move to the child tier and set the selected node"""
        self.m_currentNode = self.m_currentNode.children[self.m_currentIndex]

    def tree_ToRoot(self):
        """Move back to the root tier of the tree"""
        self.m_currentNode = self.root

    def tree_IsRoot(self):
        """Check if the current tier in the tree is the root tier"""
        return (self.m_currentNode == self.root)

    def tree_ChildIsLeaf(self):
        """If the current tier has no children then it is
        considered a leaf"""
        return (len( self.m_currentNode.children ) == 0)

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
        """Returns the number of columns in the treeview."""
        return len(self.root.columns)

    def treeview_ColumnInternalName(self, columnIndex):
        """Returns the internal name of a given column for use in configs, etc.
        Important that these never change."""
        if columnIndex < len(self.root.columns):
            return self.root.columns[columnIndex].get('name')

    def treeview_ColumnIconResource(self, columnIndex):
        """Returns the name of a 13px icon resource for the column header."""
        if columnIndex < len(self.root.columns):
            icon_resource = self.root.columns[columnIndex].get('icon_resource')
            if icon_resource:
                return icon_resource
        # Without returning something, MODO will crash.
        return ""

    def treeview_ColumnJustification(self, columnIndex):
        """Returns the desired justification setting for a given column.
        #define LXiTREEJUST_LEFT                0
        #define LXiTREEJUST_CENTER              1
        #define LXiTREEJUST_RIGHT               2"""
        lookup = {
            'left': 0,
            'center': 1,
            'right': 2
        }
        if columnIndex < len(self.root.columns):
            string_value = self.root.columns[columnIndex].get('justify', 'left')
            return lookup[string_value]

    def treeview_PrimaryColumnPosition(self):
        """Returns True for the column that should be 'primary', i.e. should have the carrot
        display for children, etc."""
        lx.out("treeview_PrimaryColumnPosition: ", self._primary_column_position)
        return self._primary_column_position

    def treeview_ColumnByIndex(self, columnIndex):
        """Returns a tuple with the name and width of a given column."""
        try:
            name = self.root.columns[columnIndex]['name']
            width = self.root.columns[columnIndex]['width']
            return (name, width)
        except:
            raise Exception('treeview_ColumnByIndex failed. Possibly malformed column dictionary.')

    def treeview_ToPrimary(self):
        """Move the tree to the primary selection"""
        if self.m_currentNode.primary:
            self.m_currentNode = self.m_currentNode.primary
            self.tree_ToParent()
            return True
        return False


    def treeview_IsSelected(self):
        return self.targetNode().selected

    def treeview_IsDescendantSelected (self):
        # Backwards for some reason...
        # for child in self.targetNode().children:
        #     if child.selected:
        #         return False
        return True

    def treeview_Select(self, mode):
        if mode == lx.symbol.iTREEVIEW_SELECT_PRIMARY:
            self.root.clear_tree_selection()
            self.targetNode().selected = True

        elif mode == lx.symbol.iTREEVIEW_SELECT_ADD:
            self.targetNode().selected = True

        elif mode == lx.symbol.iTREEVIEW_SELECT_REMOVE:
            self.targetNode().selected = False

        elif mode == lx.symbol.iTREEVIEW_SELECT_CLEAR:
            self.root.clear_tree_selection()

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
        # columns = self.root.columns
        # try:
        #     tooltip = self.targetNode().values[columns[columnIndex]['name']].tooltip
        #     if tooltip:
        #         return tooltip
        # except:
        #     pass
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
        return len(self.root.columns)

    def attr_GetString(self, index):
        columns = self.root.columns
        node = self.targetNode()

        for n in range(len(columns)):
            if index == n:
                try:
                    # Print the `display_value` in the cell
                    return node.values[columns[n]['name']].display_value
                except:
                    # Column is empty
                    return ""

        return ""
