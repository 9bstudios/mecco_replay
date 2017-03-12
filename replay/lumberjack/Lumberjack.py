# python

import lx, traceback
from TreeNode import TreeNode
from TreeView import TreeView

class Lumberjack(object):
    """Metaclass containing everything necessary to create
    and manage a working treeview in MODO.

    COMMON OPERATIONS
    -----------------

    TreeView object must be blessed in order to be available in MODO.
    Several parameters are required as a prerequisite of blessing, see
    bless() method for more. TreeView can only be blessed
    once per session.

    `Lumberjack().bless({})`

    The Lumberjack() root node is available with the `.root` property, but
    all of its methods are also available on the Lumberjack() object itself
    for convenience and readability.

    `Lumberjack().root # gets root node`
    `Lumberjack().add_child(**kwargs) # equiv of .root.add_child()`
    `Lumberjack().tail_commands = [TreeNode()] # add UI commands to bottom of children`

    Nodes have methods for various manipulations and properties for meta
    properties like row color. Note that input mapping regions can be added
    to rows or individual values (i.e. cells) as needed.

    `Lumberjack().children[n].selectable = False`
    `Lumberjack().children[n].selected = True`
    `Lumberjack().children[n].setParent(node)`
    `Lumberjack().children[n].clear_children(node)`
    `Lumberjack().children[n].delete()`
    `Lumberjack().children[n].delete_descendants()`
    `Lumberjack().children[n].row_color = row_color_string`
    `Lumberjack().children[n].input_region = region_name`
    `Lumberjack().children[n].children`
    `Lumberjack().children[n].descendants` # children, grandchildren, etc.
    `Lumberjack().children[n].ancestors` # parents, grandparents, etc.
    `Lumberjack().children[n].tier # returns number of ancestors`

    Nodes have a `values` property containing keys for each column in the
    TreeView. The value property has set/get built-in, but also contains
    properties for metadata like color, font_weight, font_style, etc.
    An optional display_value overrides the value parameter for display
    in the TreeView UI, but the `value` is always used internally.

    `Lumberjack().children[n].columns[col_name] = value`
    `Lumberjack().children[n].columns[col_name].value = value # equiv of above`
    `Lumberjack().children[n].columns[col_name].display_value = display_value`
    `Lumberjack().children[n].columns[col_name].input_region = region_name`
    `Lumberjack().children[n].columns[col_name].color.set_with_hex("#ffffff")`
    `Lumberjack().children[n].columns[col_name].font.set_bold()`
    `Lumberjack().children[n].columns[col_name].font.set_italic()`

    Attributes are TreeNodes that appear under the `+` sign in the MODO UI.
    They have the same columns as other nodes, but are separate from the
    node's children.

    `Lumberjack().children[n].addAttribute(**kwargs)`
    `Lumberjack().children[n].attribute[attribute_name] = attribute_value`

    Various tree-wide properties and methods are available for the TreeView
    from the Lumberjack object itself.

    `Lumberjack().selected # list of selected nodes`
    `Lumberjack().primary # most recently selected node (usually)`
    `Lumberjack().all_nodes # all nodes in tree`
    `Lumberjack().find(column_name, search_term) # list of matches`
    'Lumberjack().clear_selection()'

    Rebuild and Refresh methods are built into the various manipulation
    methods in Lumberjack, so there is no need to manually Refresh or Rebuild
    the treeview."""

    # A given MODO instance may create multiple TreeView class instances for display
    # in the UI. As such, we use class variables within the TreeView to keep those
    # various views in sync.

    # This means, however, that if we use the Lumberjack wrapper to bless multiple
    # different TreeViews, they will conflict with one another unless we create
    # a subclass of TreeView that is unique to the Lumberjack() object in question.

    # Life. It's complicated.
    class _TreeViewSubclass(TreeView):
        pass

    _root = None
    _tree_view = None
    _blessed = False
    _internal_name = ""
    _ident = ""
    _nice_name = ""
    _viewport_type = ""
    _primary = None

    # In case you need to extend the TreeNode class, you can inherit TreeNode in
    # your own class and then tell your Lumberjack Object to use it by changing
    # the TreeNodeClass property.
    _TreeNodeClass = TreeNode

    def __init__(self):
        """A lumberjack class is a self-contained model-view-controller system.

        It maintains:
        - a `TreeNode()` object
        - a `TreeView()` object

        The TreeNode object is the data moel, the TreeView is the view model,
        and the lumberjack object acts as controller."""

        pass

    @classmethod
    def bless(cls, viewport_type, nice_name, internal_name, ident, column_definitions, input_regions, notifiers):
        """Blesses the TreeView into existence in the MODO GUI.

        Requires seven arguments.

        :param viewport_type:   category in the MODO UI popup
                                vpapplication, vp3DEdit, vptoolbars, vpproperties, vpdataLists,
                                vpinfo, vpeditors, vputility, or vpembedded

        :param nice_name:       display name for the treeview in window title bars, etc
                                should ideally be a message table lookup '@table@message@'

        :param internal_name:   name of the treeview server (also used in config files)

        :param ident:           arbitrary unique four-letter all-caps identifier (ID4)

        :param column_definitions:
                                A dictionary containing, at minimum, a key called 'list' containing a list
                                of dictionaries corresponding to each column in the view. The 'name' strings
                                for each column must correspond with the value entries for each node.

                                Columns are semi-static in the Python API: they can be changed, but those
                                changes only update when a new treeview is initiated. Don't expect to change
                                columns on the fly.

                                Example:

                                ```
                                column_definitions = {
                                    'primary_position': 1,
                                    'list': [
                                            {
                                                'name':'name',
                                                # negative integers are summed and then divided for relative widths.
                                                # in this example, -1 + -3 == -4, so -1/-4 is 25%.
                                                'width':-1
                                            }, {
                                                'name':'enable',
                                                # positive integers are pixel values (i.e. 20px)
                                                'width':20
                                            }, {
                                                'name':'value',
                                                'width':-3
                                            }
                                        ]
                                }
                                ```

                                Somewhat confusingly, the "primary" column (i.e. the one with the carrot twirldown
                                for revealing child nodes) is not necessarily the left-most column. The items
                                list is a good example of this.

                                The TreeView API wants us to provide the "primary" column as the first item
                                in the list, but then _move_ it to a different slot using the `treeview_PrimaryColumnPosition()`
                                method. Confusing. As. Hell. And apparently it works differently internally.
                                Grumble grumble.

                                So we hack it. In the above example, we might want to move the 'name' column
                                to the right of the 'enable' column using the 'primary_position' key, which sets the
                                value returned by `treeview_PrimaryColumnPosition()`.

        :param input_regions:   list of regions for input remapping. These can be implemented from
                                within the data object itself as described in TreeData(), and used
                                in InputRemapping config files, like this:

                                <atom type="InputRemapping">
                                    <hash type="Region" key="treeViewConfigName+(contextless)/(stateless)+regionName@rmb">render</hash>
                                </atom>

                                NOTE: slot zero [0] in the list is reserved for the .anywhere region.
                                Don't use it.
                                ```
                                [
                                    '(anywhere)',       # 0 reserved for .anywhere
                                    'regionNameOne',    # 1
                                    'regionNameTwo'     # 2
                                ]
                                ```

        :param notifiers:       Returns a list of notifier tuples for auto-updating the tree. Optional.
                                ```
                                [
                                    ("select.event", "polygon +ldt"),
                                    ("select.event", "item +ldt")
                                ]
                                ```
        """

        # Can only be blessed once per session.
        if cls._blessed:
            raise Exception('%s class has already been blessed.' % cls.__name__)

        # The `TreeNode()` object is the root of the tree, and all other nodes
        # will be children of this node. The root node is NOT visible in the GUI.
        cls._root = cls._TreeNodeClass(
            column_definitions = column_definitions.get('list', []),
            controller = cls()
        )

        # Our internal handle for the view itself.
        cls._tree_view = cls._TreeViewSubclass(
            root = cls._root,
            primary_column_position = column_definitions.get('primary_position', 0),
            input_regions = input_regions,
            controller = cls()
        )

        # We store these as read-only properties of the class, just in case
        # we ever need them.
        cls._internal_name = internal_name
        cls._ident = ident
        cls._nice_name = nice_name
        cls._viewport_type = viewport_type

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
            # Remember: we've created a Lumberjack-specific subclass of our `TreeView()` class for
            # the blessing, just in case more than one Lumberjack subclass exists.
            lx.bless(cls._TreeViewSubclass, server_name, tags)

            # Make sure it doesn't happen again.
            cls._blessed = True

        except:
            traceback.print_exc()
            raise Exception('Unable to bless %s.' % cls.__name__)

    @property
    def root(self):
        """Returns the class `TreeNode()` object."""
        if self.__class__._root:
            return self.__class__._root
        else:
            raise Exception('%s: Root cannot be accessed before `bless()`.' % self.__class__.__name__)

    @property
    def treeview(self):
        """Returns the class `TreeView()` object."""
        if self.__class__._tree_view:
            return self.__class__._tree_view
        else:
            raise Exception('%s: Root cannot be accessed before `bless()`.' % self.__class__.__name__)

    @property
    def selected_descendants(self):
        """Returns the selected `TreeNode()` objects in the tree."""
        return self.root.selected_descendants

    @property
    def selected_children(self):
        """Returns the selected `TreeNode()` objects at the root of the tree."""
        return self.root.selected_children

    def select_event(self):
        """Fired by `TreeNode` objects whenever the node's `selected` property is changed.
        Implement in Lumberjack subclass to fire custom notifiers, etc."""
        pass

    def clear_selection(self):
        """Returns the selected `TreeNode()` objects in the tree."""
        return self.root.deselect_descendants()

    def primary():
        doc = """The primary node is typically the most recently selected."""
        def fget(self):
            return self._primary
        def fset(self, value):
            self.__class__._primary = value
        return locals()

    primary = property(**primary())

    def TreeNodeClass():
        doc = """The `TreeNode()`` subclass to use when populating the tree.

        By default, Lumberjack populates itself with vanilla `TreeNode` objects.
        Should you need to extend `TreeNode` to include application-specific functionality,
        you can inherit `TreeNode` into your own class, and supply your class to Lumberjack
        using the `TreeNodeClass` property."""
        def fget(self):
            return self._TreeNodeClass
        def fset(self, value):
            self._TreeNodeClass = value
        return locals()

    TreeNodeClass = property(**TreeNodeClass())

    def column_definitions():
        doc = """List of columns and their widths for the treeview in the
        format `('name', width)`, where width can be a positive integer in pixels
        or a negative integer representing a width relative to the total of all
        netagive values. Set during bless. Cannot change during a session."""
        def fget(self):
            return self._root.column_definitions
        return locals()

    column_definitions = property(**column_definitions())

    def children():
        doc = """A list of `TreeNode()` objects that are children of the current
        node. Note that children appear under the triangular twirl in the listview
        GUI, while attributes appear under the + sign."""
        def fget(self):
            return self.root.children
        def fset(self, value):
            self.root.children = value
        return locals()

    children = property(**children())

    def all_nodes():
        doc = """Returns a list of all all_nodes in the tree."""
        def fget(self):
            all_nodes = []
            for child in self.root.children:
                all_nodes.append(child)
                all_nodes.extend(child.descendants)
            return all_nodes
        return locals()

    all_nodes = property(**all_nodes())

    def tail_commands():
        doc = """List of `TreeNode()` objects appended to the bottom of the node's list
        of children, e.g. (new group), (new form), and (new command) in Form Editor.
        Command must be mapped using normal input remapping to the node's input region."""
        def fget(self):
            return self.root.tail_commands
        def fset(self, value):
            self.root.tail_commands = valuegg
        return locals()

    tail_commands = property(**tail_commands())

    def add_child(self, **kwargs):
        """Adds a child `TreeNode()` to the current node and returns it."""
        if not 'parent' in kwargs:
            kwargs['parent'] = self.root
        newNode = self._TreeNodeClass(**kwargs)
        if 'index' not in kwargs:
            kwargs['parent'].children.append(newNode)
        else:
            kwargs['parent'].children.insert(kwargs['index'], newNode)
        return newNode

    def clear(self):
        """Deletes all nodes from the tree."""
        self.primary = None
        self.root.delete_descendants()

    def find(self, column_name, search_term, regex=False):
        """Returns a list of `TreeNode()` objects with values matching search criteria.

        Unless regex is enabled, the search_term requires an exact match.

        :param column_name: (str) name of the column to search
        :param search_term: (str, bool, int, or float) value to search for
        :param regex: (bool) use regular expression"""

        return self.root.find_in_descendants(column_name, search_term, regex)

    def rebuild_view(self):
        """Rebuilds the `TreeView()` object from scratch. Must run every time any
        structural change occurs in the node tree. Note: if cell values have changed
        but the overal structure of the node tree has not changed, use `refresh()`
        for performance."""

        # NOTE: We must _both_ notify attributes _and_ shape. (Facepalm.)
        self.treeview.notify_NewAttributes()
        self.treeview.notify_NewShape()

    def refresh_view(self):
        """Refreshes `TreeView()` cell values, but not structure. Must run every
        time a cell value changes in the node tree. Note: structural changes
        (e.g. adding/removing nodes, reordering, reparenting) require the
        `rebuild()`` method."""

        self.treeview.notify_NewAttributes()
