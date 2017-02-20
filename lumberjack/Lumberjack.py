# python

from var import *
from TreeData import TreeData
from TreeNode import TreeNode
from TreeView import TreeView

class Lumberjack(object):
    """Metaclass containing everything necessary to create
    and manage a working treeview in MODO.

    COMMON OPERATIONS
    -----------------

    TreeView object must be blessed in order to be available in MODO.
    Several parameters are required as a prerequisite of blessing, see
    blessing_parameters() method for more. TreeView can only be blessed
    once per session.

    `Lumberjack().bless()`

    The Lumberjack() root node is available with the `.root` property, but
    all of its methods are also available on the Lumberjack() object itself
    for convenience and readability.

    Lumberjack()`.root # gets root node`
    `Lumberjack().add_child(kwargs**) # equiv of .root.add_child()`
    `Lumberjack().tail_commands = [TreeNode()] # add UI commands to bottom of children

    Nodes have methods for various manipulations and properties for meta
    properties like row color. Note that input mapping regions can be added
    to rows or individual values (i.e. cells) as needed.

    `Lumberjack().children[n].selectable = False`
    `Lumberjack().children[n].selected = True`
    `Lumberjack().children[n].primary = True`
    `Lumberjack().children[n].setParent(node)`
    `Lumberjack().children[n].clear_children(node)`
    `Lumberjack().children[n].reorder(index)`
    `Lumberjack().children[n].reorder_up()`
    `Lumberjack().children[n].reorder_down()`
    `Lumberjack().children[n].reorder_top()`
    `Lumberjack().children[n].reorder_bottom()`
    `Lumberjack().children[n].delete()`
    `Lumberjack().children[n].delete_descendants()`
    `Lumberjack().children[n].row_color = row_color_string`
    `Lumberjack().children[n].input_region = region_name`
    `Lumberjack().children[n].children`
    `Lumberjack().children[n].get_descendants()`
    `Lumberjack().children[n].get_ancestors()`
    `Lumberjack().children[n].tier() # returns number of ancestors`

    Nodes have a `values` property containing keys for each column in the
    TreeView. The value property has set/get built-in, but also contains
    properties for metadata like color, font_weight, font_style, etc.
    An optional display_value overrides the value parameter for display
    in the TreeView UI, but the `value` is always used internally.

    `Lumberjack().children[n].values[col_name] = value`
    `Lumberjack().children[n].values[col_name].value = value # equiv of above`
    `Lumberjack().children[n].values[col_name].display_value = display_value`
    `Lumberjack().children[n].values[col_name].input_region = region_name`
    `Lumberjack().children[n].values[col_name].color = color_string`
    `Lumberjack().children[n].values[col_name].font_weight = 'bold'`
    `Lumberjack().children[n].values[col_name].font_style = 'italic'`

    Attributes are TreeNodes that appear under the `+` sign in the MODO UI.
    They have the same columns as other nodes, but are separate from the
    node's children.

    `Lumberjack().children[n].addAttribute(kwargs**)`
    `Lumberjack().children[n].attribute[attribute_name] = attribute_value`

    Various tree-wide properties and methods are available for the TreeView
    from the Lumberjack object itself.

    `Lumberjack().selected # list of selected nodes`
    `Lumberjack().primary # most recently selected node (usually)`
    `Lumberjack().nodes # all nodes in tree`
    `Lumberjack().find(column_name, search_term) # list of matches`
    'Lumberjack().clear_selection()'

    Rebuild and Refresh methods are built into the various manipulation
    methods in Lumberjack, so there is no need to manually Refresh or Rebuild
    the treeview."""

    # In case there are multiple Lumberjack subclasses floating around,
    # we create our own subclass of TreeView for the blessing. That way
    # the blessed class is sure not to interfere with any other Lumberjack
    # subclasses.

    _TreeViewSubclass = type('_TreeViewSubclass', (TreeView,), {})

    _root = None
    _tree_view = None
    _blessed = False

    def __init__(self):
        """A lumberjack class is a self-contained model-view-controller system.

        It maintains:
        - a TreeData() object
        - a TreeView() object

        The TreeData object is the data moel, the TreeView is the view model,
        and the lumberjack object acts as controller."""

        # The TreeNode() object is the root of the tree, and all other nodes
        # will be children of this node. The root node is NOT visible in the GUI.
        self._root = TreeNode()

        # Our internal handle for the view itself.
        self._tree_view = _TreeViewSubclass()

    def rebuild(self, data):
        """Rebuilds the lumberjack TreeNode object from a dictionary
        and notifies the TreeView of the change.

        :param data: Valid lumberjack TreeNode object or compatible dictionary."""

        # We can accept either a dictionary, or a TreeNode object.
        # If it's a dict, just pump it straight into our data object:
        if isinstance(data, dict):
            # TODO Build the tree

        # If it's a TreeData object, grab its internal data:
        elif isinstance (data, TreeNode):
            self._root = data

        # Rebuild the tree
        self._tree_view.notify_NewShape()

    def refresh(self):
        """Called by TreeNodes when a value is updated. Refreshes the treeview
        cell values without rebuilding the entire tree."""

        # Refresh the tree
        self._tree_view.notify_NewAttributes()

    def bless(self, viewport_type, nice_name, internal_name, ident, column_names, input_regions, notifiers):
        """Blesses the TreeView into existence in the MODO GUI.

        Requires seven arguments.

        :param viewport_type:   category in the MODO UI popup
                                vpapplication, vp3DEdit, vptoolbars, vpproperties, vpdataLists,
                                vpinfo, vpeditors, vputility, or vpembedded

        :param nice_name:       display name for the treeview in window title bars, etc
                                should ideally be a message table lookup '@table@message@'

        :param internal_name:   name of the treeview server (also used in config files)

        :param ident:           arbitrary unique four-letter all-caps identifier (ID4)

        :param column_names:    a list of column names for node values. Values in each
                                node's values dictionary must correspond with these strings

        :param input_regions:   list of regions for input remapping. These can be implemented from
                                within the data object itself as described in TreeData(), and used
                                in InputRemapping config files, like this:

                                <atom type="InputRemapping">
                                    <hash type="Region" key="treeViewConfigName+(contextless)/(stateless)+regionName@rmb">render</hash>
                                </atom>

                                NOTE: slot zero [0] in the list is reserved for the .anywhere region.
                                Don't use it.

                                [
                                    '(anywhere)',       # 0 reserved for .anywhere
                                    'regionNameOne',    # 1
                                    'regionNameTwo'     # 2
                                ]

        :param notifiers:       Returns a list of notifier tuples for auto-updating the tree. Optional.

                                [
                                    ("select.event", "polygon +ldt"),
                                    ("select.event", "item +ldt")
                                ]
        """

        # Can only be blessed once per session.
        if self._blessed:
            raise Exception('%s class has already been blessed.' % self.__class__.__name__)

        # NOTE: MODO has three different strings for SERVERNAME, sSRV_USERNAME,
        # and name to be used in config files. In practice, these should really
        # be the same thing. So lumberjack expects only a single "INTERNAL_NAME"
        # string for use in each of these fields.

        config_name = internal_name
        server_username = internal_name
        server_name = internal_name

        sTREEVIEW_TYPE = " ".join((
            viewport_type,
            ident,
            config_name,
            nice_name
        ))

        sINMAP = "name[{}] regions[{}]".format(
            server_username, " ".join(
                ['{}@{}'.format(n, i) for n, i in enumerate(input_regions) if n != 0]
            )
        )

        tags = {
            lx.symbol.sSRV_USERNAME: server_username,
            lx.symbol.sTREEVIEW_TYPE: sTREEVIEW_TYPE,
            lx.symbol.sINMAP_DEFINE: sINMAP
        }

        try:
            # We create a Lumberjack-specific subclass of our TreeView class for
            # the blessing, just in case more than one Lumberjack subclass exists.
            lx.bless(self._TreeViewSubclass, server_name, tags)

            # Make sure it doesn't happen again.
            self._blessed = True

        except:
            raise Exception('Unable to bless %s.' % self.__class__.__name__)

    @property
    def root(self):
        """Returns the class TreeData object."""
        return self.__class__._root

    @property
    def view(self):
        """Returns the class TreeView object."""
        return self.__class__._tree_view

    @property
    def primary(self):
        """Returns the primary TreeNode() object in the tree.
        Usually this is the most recently selected or created."""
        return self._root.primary

    @property
    def selected(self):
        """Returns the selected TreeNode() objects in the tree."""
        return self._root.selected

    @property
    def clear_selection(self):
        """Returns the selected TreeNode() objects in the tree."""
        return self._root.deselect_descendants()

    def children(self):
        doc = """A list of `TreeNode()` objects that are children of the current
        node. Note that children appear under the triangular twirl in the listview
        GUI, while attributes appear under the + sign."""
        def fget(self):
            return self._root.children
        def fset(self, value):
            self._root.children = value
        return locals()

    children = property(**children())

    def tail_commands(self):
        doc = """List of TreeNode objects appended to the bottom of the node's list
        of children, e.g. (new group), (new form), and (new command) in Form Editor.
        Command must be mapped using normal input remapping to the node's input region."""
        def fget(self):
            return self._root.tail_commands
        def fset(self, value):
            self._root.tail_commands = value
        return locals()

    tail_commands = property(**tail_commands())

    def add_child(self, **kwargs):
        """Adds a child `TreeNode()` to the current node and returns it."""
        self._root.children.append(TreeNode(**kwargs))
        return self._root.children[-1]

    def nodes(self):
        """Returns a list of all nodes in the tree."""
        nodes = []
        for child in self._root.children:
            nodes.extend(child.get_descendants())
        return nodes

    def find(self, column_name, search_term, regex=False):
        """Returns a list of nodes with values matching search criteria.

        If the search term is a string, it is treated as a regular expression.
        If it is any other value, search will require an exact match.

        :param column_name: name of the column to search
        :param search_term: regular expression or value to search for"""

        return self._root.find_in_descendants(column_name, search_term, regex)
