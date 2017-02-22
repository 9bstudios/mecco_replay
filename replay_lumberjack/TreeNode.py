# python

from re import search
from TreeValue import TreeValue

class TreeNode(object):
    """Generalized container object for TreeView node data. Everything needed
    to draw the node in the TreeView UI is contained in the TreeNode, as well
    as properties and methods for getting, setting, and modifying that data
    from outside.

    The Lumberjack() object class is a self-contained Model-View-Controller system.
    The Lumberjack() object itself acts as controller, it creates a TreeView() subclass
    to act as the view, and a TreeNode() object acts as the model.

    End-users of the Lumberjack class will probably never interact with TreeView
    objects. They will, however, interact frequently with TreeNode objects."""

    # Column names are common to all nodes, defined during Lumberjack subclass `bless()`
    # Each column is a dictionary with at least two keys: 'name', and 'width'. Width
    # values can be positive integers for literal pixel widths, or negative integers
    # for ratios of the sum-total of all other negative integers. (If one column is
    # width -1 and another is -3, the first is 25%, the second is 75%.)
    _columns = []

    # Methods will be called when cell values update
    _callbacks_for_refresh = []

    # Methods will be called when tree structure updates
    _callbacks_for_rebuild = []

    # Node that is "primary" in the GUI, aka most recently selected
    _primary = None

    def __init__(self, **kwargs):

        # Whether selectable in GUI
        self._selectable = kwargs.get('selectable', True)

        # Whether selected in GUI
        self._selected = kwargs.get('selected', False)

        # Dict of TreeValue objects for each column; {column_name: TreeValue()}
        self._values = kwargs.get('values', {})

        # TreeNode parent. All TreeNode() objects except root should have a parent.
        self._parent = kwargs.get('parent', None)

        # List of TreeNode objects (listed under carrot twirl in GUI; Attributes
        # are also TreeNode objects, but listed under the + sign in the GUI.)
        self._children = kwargs.get('children', [])

        # List of TreeNode objects (listed under the + in GUI; Children
        # are also TreeNode objects, but listed under the triangular twirl in the GUI.)
        self._attributes = kwargs.get('attributes', [])

        # List of TreeNode objects appended to the bottom of the node's list
        # of children, e.g. (new group), (new form), and (new command) in Form Editor
        self._tail_commands = kwargs.get('tail_commands', [])

        # Bitwise flags for GUI states like expand/collapse etc. Leave this alone.
        self._state = kwargs.get('state', None)

        # String for use in input remapping. Must correspond with one of the region
        # strings provided in the Lumberjack blessing_parameters() method.
        self._input_region = kwargs.get('input_region', None)

        # Primary is usually the most recently selected node. If we initialize
        # a new node, however, that one becomes primary.
        self.__class__._primary = self

        # Add empty TreeValue objects for each column, ready to accept values.
        for column in self._columns:
            self._values[column['name']] = TreeValue()

    ########################################################################

    # WHISKYTREE BOILERPLATE
    # ----------

    # TODO
    # It is not at all clear, but it seems as if MODO may be trying to use
    # specific method names for some calls to TreeNode. For safety I have
    # included modified versions of each of the ones from Whiskytree here.

    # These should be deleted if they turn out to be unnecessary.

    def AddNode(self, **kwargs):
        self.add_child(**kwargs)

    def ClearSelection(self):
        self.clear_tree_selection

    def SetSelected(self, val=True):
        if val:
            self.setPrimary(self)
        self.selected = val

    def isSelected(self):
        return self.selected

    @classmethod
    def setPrimary(cls, primary=None):
        cls.primary = primary

    @classmethod
    def getPrimary(cls):
        return cls.primary

    def setState(self, flag):
        self.state = self.state | flag

    def setToolTip(self, index, tip):
        self.values[index].tooltip = tip

    def getToolTip(self, index):
        if index < len(self.values):
            return self.values[index].tooltip

    ########################################################################


    # PROPERTIES
    # ----------

    def columns():
        doc = """List of column names for the node tree. Common to all nodes.
        Set during `Lumberjack().bless()`

        Each column is a dictionary with at least two keys: 'name', and 'width'. Width
        values can be positive integers for literal pixel widths, or negative integers
        for ratios of the sum-total of all other negative integers. (If one column is
        width -1 and another is -3, the first is 25%, the second is 75%.)"""
        def fget(self):
            return self._columns
        def fset(self, value):
            self.__class__._columns = value
        return locals()

    columns = property(**columns())

    def callbacks_for_refresh():
        doc = "Method to call when cell values are updated."
        def fget(self):
            return self._callbacks_for_refresh
        def fset(self, value):
            self._callbacks_for_refresh = value
        return locals()

    callbacks_for_refresh = property(**callbacks_for_refresh())

    def callbacks_for_rebuild():
        doc = "Method to call when tree structure is updated."
        def fget(self):
            return self._callbacks_for_rebuild
        def fset(self, value):
            self._callbacks_for_rebuild = value
        return locals()

    callbacks_for_rebuild = property(**callbacks_for_rebuild())

    def selectable():
        doc = "Whether the node is selectable in the GUI. (boolean)"
        def fget(self):
            return self._selectable
        def fset(self, value):
            if value == False:
                self._selected = False
                self._primary = None
            self._selectable = value
        return locals()

    selectable = property(**selectable())

    def selected():
        doc = "Whether the node is selected in the GUI. (boolean)"
        def fget(self):
            return self._selected
        def fset(self, value):
            self._selected = value
        return locals()

    selected = property(**selected())

    def primary():
        doc = """Class property teturns the primary TreeNode in the tree.

        Typically the most recently selected or created node will be primary.
        It is possible to set the primary node to False, meaning there is no
        current primary."""
        def fget(self):
            return self._primary
        def fset(self, value):
            self.__class__._primary = value
        return locals()

    primary = property(**primary())

    def values():
        doc = """The values for each column in the node. (dictionary)

        The dictionary should have one key for each column name defined in the
        Lumberjack blessing_parameters `'columns'` key. The values themselves
        are `TreeValue()` objects, each with a `value` property for the internal
        value, but also containing metadata like font, color, etc.

        Empty values and invalid keys (not matching a column name) will be
        ignored."""
        def fget(self):
            return self._values
        def fset(self, values):
            self._values = values
            self.callback_refresh()
        return locals()

    values = property(**values())

    def parent():
        doc = """The parent node of the current `TreeNode()` object. The root
        node's parent is `None`."""
        def fget(self):
            return self._parent
        def fset(self, node):
            self._parent = node
            self.callback_rebuild()
        return locals()

    parent = property(**parent())

    def root():
        doc = """The root node of the current `TreeNode()` hierarchy."""
        def fget(self):
            if not self.parent:
                return self
            return self.parent.root
        return locals()

    root = property(**root())

    def index():
        doc = "The index of the node amongst its siblings (parent's children)."
        def fget(self):
            return self._parent.children.index(self)
        def fset(self, index):
            child_list = self._parent.children
            old_index = child_list.index(self)
            child_list.insert(index, child_list.pop(old_index))
            self.callback_rebuild()
        return locals()

    index = property(**index())

    def children():
        doc = """A list of `TreeNode()` objects that are children of the current
        node. Note that children appear under the triangular twirl in the listview
        GUI, while attributes appear under the + sign."""
        def fget(self):
            return self._children
        def fset(self, value):
            self._children = value
            self.callback_rebuild()
        return locals()

    children = property(**children())

    def attributes():
        doc = """A list of `TreeNode()` objects that are attributes of the current
        node. Note that attributes appear under the + sign in the listview
        GUI, while children appear under the triangular twirl."""
        def fget(self):
            return self._attributes
        def fset(self, value):
            self._attributes = value
            self.callback_rebuild()
        return locals()

    attributes = property(**attributes())

    def tail_commands():
        doc = """List of TreeNode objects appended to the bottom of the node's list
        of children, e.g. (new group), (new form), and (new command) in Form Editor.
        Command must be mapped using normal input remapping to the node's input region."""
        def fget(self):
            return self._tail_commands
        def fset(self, value):
            self._tail_commands = value
            self.callback_rebuild()
        return locals()

    tail_commands = property(**tail_commands())

    def state():
        doc = """Bitwise flags used to define GUI states like expand/collapse etc.
        Leave these alone."""
        def fget(self):
            return self._state
        def fset(self, value):
            self._state = value
        return locals()

    state = property(**state())

    def input_region():
        doc = """String for use in input remapping. Must correspond with one of the region
        strings provided in the Lumberjack blessing_parameters() method."""
        def fget(self):
            return self._input_region
        def fset(self, value):
            self._input_region = value
        return locals()

    input_region = property(**input_region())

    def siblings():
        doc = """Returns a list of all of the current node's siblings, i.e. parent's children.
        (Including the current node.)"""
        def fget(self):
            return self._parent.children
        return locals()

    siblings = property(**siblings())

    def descendants():
        doc = """Returns a list of all children, grandchildren, etc for the current node."""
        def fget(self):
            descendants = []
            for child in self.children:
                descendants.append(child)
                descendants.extend(child.descendants())
            return descendants
        return locals()

    descendants = property(**descendants())

    def ancestors():
        doc = """Returns a list of all parents, grandparents, etc for the current node."""
        def fget(self):
            if self.parent:
                return self.parent.ancestors.extend(self.parent)
            elif not self.parent:
                return []
        return locals()

    ancestors = property(**ancestors())

    def tier():
        doc = """Returns the number of anscestors."""
        def fget(self):
            return len(self.get_ancestors())
        return locals()

    tier = property(**tier())


    # METHODS
    # ----------

    def add_child(self, **kwargs):
        """Adds a child `TreeNode()` to the current node and returns it."""
        if not 'parent' in kwargs:
            kwargs['parent'] = self
        self.children.append(TreeNode(**kwargs))
        self.callback_rebuild()
        return self._children[-1]

    def add_attribute(self, **kwargs):
        """Adds an attribute `TreeNode()` to the current node and returns it."""
        self._attributes.append(TreeNode(**kwargs))
        self.callback_rebuild()
        return self._attributes[-1]

    def clear_tree_selection(self):
        """Deselects all TreeNodes in the current tree."""
        for node in self.root.descendants:
            node.selected = False

    def select_descendants(self):
        """Selects all children, grandchildren, etc."""
        for child in self.children:
            child.selected = True
            child.select_descendants()

    def deselect_descendants(self):
        """Deselects all children, grandchildren, etc."""
        for child in self.children:
            child.selected = False
            child.deselect_descendants()

    def delete(self):
        """Deletes the current node and reparents all of its children to its parent."""
        self.selected = False
        self.primary = None
        # Reparent children to parent. (Does not delete hierarchy.)
        for sibling in self.parent.children:
            sibling.parent = self.parent
        self.callback_rebuild()

    def delete_descendants(self):
        """Deletes all children, grandchildren etc from the current node. To delete
        the node itself, use `delete()`"""
        if len(self._children) > 0:
            for child in self._children:
                self._children.remove(child)
            self.callback_rebuild()

    def reorder_up(self):
        """Reorder the current node up one index in the tree.
        Returns the new index."""
        if self.index > 0:
            self.index -= 1
        self.callback_rebuild()
        return self.index

    def reorder_down(self):
        """Reorder the current node down one index in the tree.
        Returns the new index."""
        if self.index + 1 < len(self.get_siblings()):
            self.index += 1
        self.callback_rebuild()
        return self.index

    def reorder_top(self):
        """Reorder the current node to the top of its branch in the tree."""
        self.index = 0
        self.callback_rebuild()

    def reorder_bottom(self):
        """Reorder the current node to the bottom of its branch in the tree.
        Returns the new index."""
        self.index = len(self.get_siblings()) - 1
        self.callback_rebuild()
        return self.index

    def find_in_descendants(self, column_name, search_term, regex=False):
        """Returns a list of descendant nodes with values matching search criteria.

        Unless regex is enabled, the search_term requires an exact match.

        :param column_name: (str) name of the column to search
        :param search_term: (str, bool, int, or float) value to search for
        :param regex: (bool) use regular expression"""

        found = []

        for child in self.children:

            if not child.values.get(column_name, None):
                continue

            if regex:
                result = search(search_term, child.values[column_name])

            elif not regex:
                result = child.values[column_name]

            if result:
                found.append(child)

            found.extend(child.find_in_descendants)

        return found

    def callback_refresh(self):
        """Calls each callback method in `callbacks_for_refresh`. Runs any time
        a cell value is updated anywhere in the node tree. Expects each callback
        to be a tuple with an object and the method name in the form
        (object, method_name)."""
        for obj, attr in self.callbacks_for_refresh:
            getattr(obj, attr)(obj())

    def callback_rebuild(self):
        """Calls each callback method in `callbacks_for_rebuild`. Runs any time
        the node tree structure is modified in any way (add/remove/reparent nodes,
        etc.) Expects each callback to be a tuple with an object and the method
        name in the form (object, method_name)."""
        for obj, attr in self.callbacks_for_refresh:
            getattr(obj, attr)(obj())
