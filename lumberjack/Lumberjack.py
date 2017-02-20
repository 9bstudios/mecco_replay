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
    `Lumberjack().addCommandNode(kwargs**)`

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
    `Lumberjack().node(ident) # node by ident`
    `Lumberjack().find(column_name, search_term) # list of matches`
    'Lumberjack().clear_selection()'

    Rebuild and Refresh methods are built into the various manipulation
    methods in Lumberjack, so there is no need to manually Refresh or Rebuild
    the treeview."""

    def __init__(self):
        """A lumberjack class is a self-contained model-view-controller system.

        It maintains:
        - a TreeData() object
        - a TreeView() object

        The TreeData object is the data moel, the TreeView is the view model,
        and the lumberjack object acts as controller."""

        # On init we need to create class variables. It's important that we do
        # this inside the __init__() method and NOT at the top of the class,
        # because we want for these class variables to be specific to any
        # lumberjack subclass, not global to all lumberjack subclasses.

        try:
            self._tree_nodes
        except AttributeError:
            self.__class__._tree_nodes = TreeNode()

        try:
            self._tree_view
        except AttributeError:
            self.__class__._tree_view = TreeView()

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
            self._tree_nodes = data

        # Rebuild the tree
        self._tree_view.notify_NewShape()

    def refresh(self):
        """Called by TreeNodes when a value is updated. Refreshes the treeview
        cell values without rebuilding the entire tree."""

        # Refresh the tree
        self._tree_view.notify_NewAttributes()

    def bless(self):
        """Blesses a treeview using parameters defined in the lumberjack
        subclass's `blessing_parameters` method."""

        # NOTE: MODO has three different strings for SERVERNAME, sSRV_USERNAME,
        # and name to be used in config files. In practice, these should really
        # be the same thing. So lumberjack expects only a single "INTERNAL_NAME"
        # string for use in each of these fields.

        for parameter in [INTERNAL_NAME, VPTYPE, ID4, NICE_NAME]:
            if not getattr(blessing_parameters(), parameter):
                lx.out("Treeview could not be blessed. Missing parameter '%s'." % parameter)
                return

        config_name = blessing_parameters()[INTERNAL_NAME]
        server_username = blessing_parameters()[INTERNAL_NAME]
        server_name = blessing_parameters()[INTERNAL_NAME]

        sTREEVIEW_TYPE = " ".join((
            blessing_parameters()[VPTYPE],
            blessing_parameters()[ID4],
            config_name,
            blessing_parameters()[NICE_NAME]
        ))

        if getattr(blessing_parameters(), REGIONS):
            sINMAP = "name[{}] regions[{}]".format(
                server_username, " ".join(
                    ['{}@{}'.format(n, i) for n, i in enumerate(blessing_parameters()[REGIONS]) if n != 0]
                )
            )

        tags = {
            lx.symbol.sSRV_USERNAME: server_username,
            lx.symbol.sTREEVIEW_TYPE: blessing_parameters()[VPTYPE],
            lx.symbol.sINMAP_DEFINE: sINMAP
        }

        # Can only be blessed once per session. Just in case, try/except.
        try:
            lx.bless(blessing_parameters()[CLASS], server_name, tags)
        except:
            lx.out("Multiple Blessings: The treeview '%s' has already been blessed." % server_name)

    def blessing_parameters(self):
        """Returns all of the necessary information to bless the treeview into
        the MODO UI. Required.

        `return {

            # category in MODO UI popup
            # vpapplication, vp3DEdit, vptoolbars, vpproperties, vpdataLists,
            # vpinfo, vpeditors, vputility, or vpembedded
            'viewport_type':    'vpapplication',

            # display name for the treeview in window title bars, etc
            # should ideally be a message table lookup '@table@message@'
            'nice_name':        'My Tree View',

            # name of the treeview server (also used in config files)
            'internal_name':    'myTreeView',

            # arbitrary, unique, four-letter, all-caps identifier
            'ident':            'MTV1'

            # a list of column names for node values. Values in each node's
            # values dictionary must correspond with these strings
            'column_names': [
                'enabled',
                'name',
                'value'
            ]

            # list of regions for input remapping. These can be implemented from
            # within the data object itself as described in TreeData(), and used
            # in InputRemapping config files, like this:
            #
            # <atom type="InputRemapping">
            #     <hash type="Region" key="treeViewConfigName+(contextless)/(stateless)+regionName@rmb">render</hash>
            # </atom>
            #
            # NOTE: slot zero [0] in the list is reserved for the .anywhere region.
            # Don't use it.
            'input-regions': [
                '(anywhere)',       # 0 reserved for .anywhere
                'regionNameOne',    # 1
                'regionNameTwo'     # 2
            ]

            # Returns a list of notifier tuples for auto-updating the tree. Optional.
            'notifiers': [
                ("select.event", "polygon +ldt"),
                ("select.event", "item +ldt")
            ]
        }`
        """

        return

    @property
    def root(self):
        """Returns the class TreeData object."""
        return self.__class__._tree_nodes

    @property
    def view(self):
        """Returns the class TreeView object."""
        return self.__class__._tree_view
