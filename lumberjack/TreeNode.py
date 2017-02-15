# python

from util import *
from var import *
from os.path import basename

class TreeNode(object):

    _primary = None

    def __init__(self, key, value=None, parent=None, node_region=None, value_type=None, selectable=True, ui_only=False):
        self._key = key
        self._value = value
        self._parent = parent
        self._node_region = node_region
        self._value_type = value_type
        self._children = []
        self._state = 0
        self._selected = False
        self._selectable = selectable
        self._ui_only = ui_only
        self._tooltips = {}

        self._columns = ((COL_NAME, -1), (COL_VALUE, -3))

    @classmethod
    def set_primary(cls, primary=None):
        cls._primary = primary

    @classmethod
    def primary(cls):
        return cls._primary

    def add_child(self, key, value=None, node_region=None, value_type=None, selectable=True, ui_only=False):
        self._children.append(TreeNode(key, value, self, node_region, value_type, selectable, ui_only))
        return self._children[-1]

    def clear_children(self):
        if len(self._children) > 0:
            for child in self._children:
                self._children.remove(child)

    def clear_selection(self):
        if self.primary():
            self.set_primary(None)

        self.set_selected(False)

        for child in self._children:
            child.clear_selection()

    def ui_only(self):
        return self._ui_only

    def set_ui_only(self, ui_only=True):
        self._ui_only = ui_only

    def set_selected(self, val=True):
        if val:
            self.set_primary(self)
        self._selected = val

    def is_selected(self):
        return self._selected

    def state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    def add_state_flag(self, flag):
        self._state = self._state | flag

    def set_tooltip(self, idx, tip):
        self._tooltips[idx] = tip

    def tooltip(self, idx):
        if idx in self._tooltips:
            return self._tooltips[idx]

    def raw_value(self):
        return self._value

    def display_value(self):
        m = ''
        if self._value_type in (list.__name__, dict.__name__, tuple.__name__):
            m = GRAY
        elif self._node_region == REGIONS[1]:
            m = GRAY
        elif self._node_region == REGIONS[5]:
            m = GRAY

        if self._node_region == REGIONS[1]:
            v = self.child_by_key(SCENE_PATH).raw_value()
        elif self._value_type == IMAGE_FORMAT:
            # v = monkey.util.get_imagesaver(self._value)[1]
            pass
        else:
            v = str(self._value)

        return m + v

    def display_name(self):
        m = ''
        if self._node_region == REGIONS[1]:
            m = ''
        elif self._ui_only:
            m = GRAY
        elif self._node_region == REGIONS[7]:
            m = FONT_BOLD
        elif isinstance(self._key, int):
            m = GRAY

        if self._node_region == REGIONS[1]:
            k = basename(self.child_by_key(SCENE_PATH).raw_value())
        elif isinstance(self._key, int):
            k = str(self._key + 1)
        else:
            k = str(self._key)
            k = k.replace('_', ' ')
            k = k.title() if "." not in k else k

        return m + k

    def key(self):
        return str(self._key)

    def set_key(self, key):
        self._key = key

    def node_region(self):
        return str(self._node_region)

    def set_node_region(self, node_region):
        self._node_region = node_region
        return self._node_region

    def set_value(self,value):
        self._value = value

    def value_type(self):
        return self._value_type

    def set_value_type(self, value_type):
        self._value_type = value_type
        return self._value_type

    def selectable(self):
        return self._selectable

    def set_selectable(self, selectable=True):
        self._selectable = selectable

    def columns(self):
        return self._columns

    def child_by_key(self, key):
        for child in self._children:
            if key == child.key():
                return child
        return False

    def selected_children(self, recursive=True):
        sel = []
        for child in self._children:
            if child.is_selected():
                sel.append(child)
            if recursive:
                sel += child.selected_children()

        return sel

    def ancestors(self, path=None):
        if self._parent:
            return self._parent.ancestors() + [self]
        else:
            return path if path else []

    def ancestor_keys(self):
        return [ancestor.key() for ancestor in self.ancestors()[1:]]

    def parent(self):
        return self._parent

    def children(self):
        return self._children

    def insert_child(self, index, node):
        self._children.insert(index, node)

    def parent_child_index(self):
        return self.parent().children().index(self)

    def set_parent_child_index(self,index):
        self.destroy()
        self.parent().insert_child(index, self)

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

    def select_shift_up(self):
        if self.parent_child_index() > 0:
            self.set_selected(False)
            self.parent().children()[self.parent_child_index() - 1].set_selected()

    def select_shift_down(self):
        if self.parent_child_index() + 1 < len(
                [i for i in self.parent().children() if not i.ui_only()]
        ):
            self.set_selected(False)
            self.parent().children()[self.parent_child_index() + 1].set_selected()

    def update_child_keys(self):
        if self.value_type() in (list.__name__, tuple.__name__):
            legit_kids = [child for child in self.children() if not child.ui_only()]
            for key, child in enumerate(sorted(legit_kids, key=lambda x: x.key())):
                child.set_key(key if isinstance(key, int) else child.key())

    def destroy(self):
        self.clear_selection()
        self.parent().children().remove(self)

    def tier(self):
        return len(self.ancestors())
