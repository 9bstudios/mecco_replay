# python

from var import *
from TreeData import TreeData
from TreeNode import TreeNode
from TreeView import TreeView

class Lumberjack(object):
    """Metaclass containing everything necessary to create a working treeview in MODO.

    A Lumberjack object contains all of the necessary methods to:
        - bless a treeview object
        - create and maintain a class-wide persistent data object for tree data
        - generate a node object for use in the treeview object
        - update the data object, nodes, and treeview to keep all three in sync
        - auto-generate input mapping regions
        - easily implement common list-management commands, like:
            - refresh data
            - add node
            - delete node
            - reparent node
            - explicit reorder
            - drag/drop reorder
        - retrieve any and all up-to-date tree data by:
            - tree selection state
            - internal active state
            - node id
            - node search"""

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
