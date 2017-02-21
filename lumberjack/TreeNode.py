# python

import re.search

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

    # Methods will be called when cell values update
    _callbacks_for_refresh = []

    # Methods will be called when tree structure updates
    _callbacks_for_rebuild = []

    # Whether selectable in GUI
    _selectable = bool()

    # Whether selected in GUI
    _selected = bool()

    # Whether "primary" in GUI, aka most recently selected
    _primary = bool()

    # Dict of TreeValue objects for each column; {column_name: TreeValue()}
    _values = dict()

    # TreeNode parent. All TreeNode() objects except root should have a parent.
    _parent = None

    # List of TreeNode objects (listed under carrot twirl in GUI; Attributes
    # are also TreeNode objects, but listed under the + sign in the GUI.)
    _children = list()

    # List of TreeNode objects (listed under the + in GUI; Children
    # are also TreeNode objects, but listed under the triangular twirl in the GUI.)
    _attributes = list()

    # List of TreeNode objects appended to the bottom of the node's list
    # of children, e.g. (new group), (new form), and (new command) in Form Editor
    _tail_commands = list()

    # Bitwise flags for GUI states like expand/collapse etc. Leave this alone.
    _state = None

    # String for use in input remapping. Must correspond with one of the region
    # strings provided in the Lumberjack blessing_parameters() method.
    _input_region = str()

    def __init__(self, **kwargs):
        self._column_names = getattr(kwargs, 'column_names', [])
        self._selectable = getattr(kwargs, 'selectable', True)
        self._selected = getattr(kwargs, 'selected', False)
        self._values = getattr(kwargs, 'values', {})
        self._parent = getattr(kwargs, 'parent', None)
        self._index = getattr(kwargs, 'index', 0)
        self._children = getattr(kwargs, 'children', [])
        self._attributes = getattr(kwargs, 'attributes', [])
        self._tail_commands = getattr(kwargs, 'tail_commands', [])
        self._state = getattr(kwargs, 'state', None)
        self._input_region = getattr(kwargs, 'input_region', None)

        # Primary is usually the most recently selected node. If we initialize
        # a new node, however, that one becomes primary.
        self.__class__._primary = self


    # PROPERTIES
    # ----------

    def callbacks_for_refresh(self):
        doc = "Method to call when cell values are updated."
        def fget(self):
            return self._callbacks_for_refresh
        def fset(self, value):
            self._callbacks_for_refresh = value
        return locals()

    callbacks_for_refresh = property(**callbacks_for_refresh())

    def callbacks_for_rebuild(self):
        doc = "Method to call when tree structure is updated."
        def fget(self):
            return self._callbacks_for_rebuild
        def fset(self, value):
            self._callbacks_for_rebuild = value
        return locals()

    callbacks_for_rebuild = property(**callbacks_for_rebuild())

    def selectable(self):
        doc = "Whether the node is selectable in the GUI. (boolean)"
        def fget(self):
            return self._selectable
        def fset(self, value):
            if value == False:
                self._selected = False
                self._primary = False
            self._selectable = value
        return locals()

    selectable = property(**selectable())

    def selected(self):
        doc = "Whether the node is selected in the GUI. (boolean)"
        def fget(self):
            return self._selected
        def fset(self, value):
            self._selected = value
        return locals()

    selected = property(**selected())

    def primary(self):
        doc = """Whether the node is primary in the GUI. (boolean)

        Typically the most recently selected or created node will be primary.
        It is possible to set the primary node to False, meaning there is no
        current primary."""
        def fget(self):
            return self._primary
        def fset(self, value):
            self.__class__._primary = False
            self._primary = value
        return locals()

    primary = property(**primary())

    def values(self):
        doc = """The values for each column in the node. (dictionary)

        The dictionary should have one key for each column name defined in the
        Lumberjack blessing_parameters `'column_names'` key. The values themselves
        are `TreeValue()` objects, each with a `value` property for the internal
        value, but also containing metadata like font, color, etc.

        Empty values and invalid keys (not matching a column name) will be
        ignored."""
        def fget(self):
            return self._values
        def fset(self, values = {}):
            self._values = values
            self.callback_refresh()
        return locals()

    values = property(**values())

    def parent(self):
        doc = """The parent node of the current `TreeNode()` object. The root
        node's parent is `None`."""
        def fget(self):
            return self._parent
        def fset(self, node):
            self._parent = node
            self.callback_rebuild()
        return locals()

    parent = property(**parent())

    def index(self):
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

    def children(self):
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

    def attributes(self):
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

    def tail_commands(self):
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

    def state(self):
        doc = """Bitwise flags used to define GUI states like expand/collapse etc.
        Leave these alone."""
        def fget(self):
            return self._state
        def fset(self, value):
            self._state = value
        return locals()

    state = property(**state())

    def input_region(self):
        doc = """String for use in input remapping. Must correspond with one of the region
        strings provided in the Lumberjack blessing_parameters() method."""
        def fget(self):
            return self._input_region
        def fset(self, value):
            self._input_region = value
        return locals()

    input_region = property(**input_region())


    # METHODS
    # ----------

    def add_child(self, **kwargs):
        """Adds a child `TreeNode()` to the current node and returns it."""
        self._children.append(TreeNode(**kwargs))
        self.callback_rebuild()
        return self._children[-1]

    def add_attribute(self, **kwargs):
        """Adds an attribute `TreeNode()` to the current node and returns it."""
        self._attributes.append(TreeNode(**kwargs))
        self.callback_rebuild()
        return self._attributes[-1]

    def get_siblings(self):
        """Returns a list of all of the current node's siblings, i.e. parent's children.
        (Including the current node.)"""
        return self._parent.children

    def get_descendants(self):
        """Returns a list of all children, grandchildren, etc for the current node."""
        descendants = []
        for child in self.children:
            descendants.extend(child.get_descendants())
        return descendants

    def select_descendants(self):
        """Selects all children, grandchildren, etc."""
        for child in self.children:
            child.selected = True
            child.select_descendants()

    def deselect_descendants(self):
        """Selects all children, grandchildren, etc."""
        for child in self.children:
            child.selected = False
            child.deselect_descendants()

    def get_anscestors(self):
        """Returns a list of all parents, grandparents, etc for the current node."""
        if self.parent:
            return self.parent.get_anscestors().extend(self.parent)
        elif not self.parent:
            return []

    def delete(self):
        """Deletes the current node and reparents all of its children to its parent."""
        self.selected = False
        self.primary = False
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

    def tier(self):
        """Returns the number of anscestors."""
        return len(self.get_ancestors())

    def find_in_descendants(self, column_name, search_term, regex=False):
        """Returns a list of descendant nodes with values matching search criteria.

        Unless regex is enabled, the search_term requires an exact match.

        :param column_name: (str) name of the column to search
        :param search_term: (str, bool, int, or float) value to search for
        :param regex: (bool) use regular expression"""

        found = []

        for child in self.children:

            if not getattr(child.values, column_name):
                continue

            if regex:
                result = re.search(search_term, child.values[column_name])

            elif not regex:
                result = child.values[column_name]

            if result:
                found.append(child)

            found.extend(child.find_in_descendants)

        return found

    def callback_refresh(self):
        """Calls each callback method in `callbacks_for_refresh`. Runs any time
        a cell value is updated anywhere in the node tree."""
        for callback in self.callbacks_for_refresh:
            callback()

    def callback_rebuild(self):
        """Calls each callback method in `callbacks_for_rebuild`. Runs any time
        the node tree structure is modified in any way (add/remove/reparent nodes,
        etc.)"""
        for callback in self.callbacks_for_rebuild:
            callback()
