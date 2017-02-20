# python

from util import *
from var import *
from os.path import basename

class TreeNode(object):

    # Only one TreeNode can be "primary". This is typically the most recently
    # selected node in the tree, displayed with a slightly darker background
    # color than the others. (It is not necessarily still selected.)
    _primary = None

    # Must correspond to one of the regions predefined in the Lumberjack
    # blessing_parameters.
    _input_region = None

    # Whether or not the node is selectable in the treeview GUI.
    _selectable = True

    # The only node without a parent is the root node.
    _parent = None

    def __init__(self, values = {}, parent = None, meta = {}):
        self._values = values
        self._parent = parent

        # state, selected, selectable, ui-only, tooltips, input-region
        self._meta = {}

        if not self._primary:
            self._primary = self

        self._children = []

    # PROPERTIES
    # ----------

    def selected():
        doc = "The selected property."
        def fget(self):
            return self._selected
        def fset(self, value):
            self._selected = value
        def fdel(self):
            del self._selected
        return locals()

    selected = property(**selected())

    def primary():
        doc = "The primary property."
        def fget(self):
            return self._primary
        def fset(self, value):
            self.__class__._primary = False
            self._primary = value
        def fdel(self):
            del self._primary
        return locals()

    primary = property(**primary())

    def state():
        doc = "The state property."
        def fget(self):
            return self._state
        def fset(self, value):
            self._state = value
        def fdel(self):
            del self._state
        return locals()

    state = property(**state())

    def values(self):
        # TODO
        pass

    def input_region():
        doc = "The input_region property."
        def fget(self):
            return self._input_region
        def fset(self, value):
            self._input_region = value
        def fdel(self):
            del self._input_region
        return locals()

    input_region = property(**input_region())

    def selectable():
        doc = "The selectable property."
        def fget(self):
            return self._selectable
        def fset(self, value):
            # TODO - when disabling, deselect.
            self._selectable = value
        def fdel(self):
            del self._selectable
        return locals()

    selectable = property(**selectable())

    def descendants(self):
        """Returns all of the descendants of the node.
        (i.e. children, grandchildren, etc)"""

        # TODO
        pass

    def ancestors(self):
        """Returns all of the ancestors of the node.
        (i.g. parent, grandparent, etc)"""

        # TODO

        pass

    def parent():
        doc = "The parent property."
        def fget(self):
            return self._parent
        def fset(self, value):
            self._parent = value
        def fdel(self):
            del self._parent
        return locals()

    parent = property(**parent())

    def children():
        doc = "The children property."
        def fget(self):
            return self._children
        def fset(self, value):
            self._children = value
        def fdel(self):
            del self._children
        return locals()

    children = property(**children())

    def index():
        # TODO
        # Should get or set the index of the current node
        # within its parent
        # self.parent().children().index(self)
        doc = "The index property."
        def fget(self):
            return self._index
        def fset(self, value):
            self._index = value
        def fdel(self):
            del self._index
        return locals()

    index = property(**index())

    # METHODS
    # ----------

    def add_child(self, values, parent, meta):
        self._children.append(TreeNode(values, parent, meta))
        return self._children[-1]

    def delete_descendants(self):
        if len(self._children) > 0:
            for child in self._children:
                self._children.remove(child)

    def reorder_up(self):
        if self.parent_child_index() > 0:
            self.set_parent_child_index(self.parent_child_index()-1)

    def reorder_down(self):
        if self.parent_child_index() + 1 < len(
                [i for i in self.parent().children() if not i.ui_only()]
        ):
            self.set_parent_child_index(self.parent_child_index()+1)

    def reorder_top(self):
        self.set_parent_child_index(0)

    def reorder_bottom(self):
        self.set_parent_child_index(
            len([i for i in self.parent().children() if not i.ui_only()]) - 1
        )

    def delete(self):
        self.clear_selection()
        self.parent().children().remove(self)

    def tier(self):
        return len(self.ancestors())
