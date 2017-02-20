# # python
#
# class TreeData(object):
#     """Class for storing and accessing lumberjack data objects.
#
#     Tree views in MODO are a cross between a 2D spreadsheet and a nodal tree:
#     there are a fixed number of columns in the list (like a spreadsheet), but
#     each row is capable of having child rows. The Items list is a perfect
#     example: each item in the list is a row, and each item has the same
#     columns in the list. But each item is also capable of having child Items
#     within the list.
#
#     A lumberjack TreeData object stores a static list of 'columns',
#     and list of nested nodes in the tree.
#
#     COLUMNS:
#     --------
#
#     Each column should be a dictionary with required keys 'internal-name' and 'width'.
#     Optional keys include 'icon-resource' and 'primary'. The primary column is
#     the one where the expand/collapse carrot will be displayed (e.g. column 4
#     in the items list).
#
#     The 'internal-name' will be used as the column header string unless a different string
#     is provided in a message table. Note that message tables for columns support
#     multiple names, and will automatically choose the longest name that fits,
#     falling back to the icon (if available) if it can't fit any username.
#
#     `'columns': [
#         {
#             'internal-name': 'enable',
#             'width': 20,
#             'icon-resource': 'myIconResource'
#         }, {
#             'internal-name': 'name',
#             'width': -1,
#             'primary': True
#         }, {
#             'internal-name': 'value',
#             'width': -3
#         }
#     ]`
#
#     NODES:
#     ------
#
#     Each node should have a unique alphanumeric 'id', a list of 'values'
#     corresponding to each column, and may also have a list of 'children'
#     in the same format. (The 'id' is an arbitrary handle for internal reference,
#     and is not displayed anywhere in the MODO UI.)
#
#     `{
#         'id': 1,
#         'values': {
#             'enable': { 'value': True },
#             'name': { 'value': 'A' },
#             'value': { 'value': 1.0 }
#         }
#     }`
#
#     NOTE: A node with no children is known as a "leaf". Trees can be
#     arbitrarily deep, and any node can have any number of children. Any node may
#     also have a 'flags' key for formatting codes (some of which are listed
#     in var.py as fTREE_VIEW_*)
#
#     Any node or value may have an optional 'input-region' key for input mapping within
#     MODO. This should correspond to the strings defined in the `input_regions()` method
#     for the lumberjack object.
#
#     VALUES:
#     -------
#
#     In a node, the 'values' key should contain a dictionary
#     with keys corresponding to the column names defined above. If a column entry
#     is missing, the cell will be left blank. Keys that do not correspond to any
#     predefined column internal name will be ignored.
#
#     Each value entry must contain a 'value' key OR a 'cell-command' and
#     'batch-command' keys. A 'value' key will print a literal value in the cell.
#     If a 'cellCmd' and 'batchCmd' are found, the cell will instead use the
#     CellCommand() and BatchCommand() methods to display dynamic content
#     (e.g. minislider).
#
#     In addition to the 'values' parameter, optional keys include attributes like:
#
#         'color' = "rgb(255, 255, 255)"
#             # "hsl(120, 60%, 70%)"
#             # "#ffffff"
#             # "#fff"
#             # "red"
#
#         'font-weight' = 'normal'
#             # 'bold'
#
#         'font-style' = 'normal'
#             # 'italic'
#
#         # NOTE: The datatype parameter is optional. If omitted, the python
#         # datatype of the value will be used.
#
#         'datatype' = 'float'
#             # 'acceleration'
#             # 'angle'
#             # 'angle3'
#             # 'axis'
#             # 'boolean'
#             # 'color'
#             # 'color1'
#             # 'date'
#             # 'datetime'
#             # 'filepath'
#             # 'float'
#             # 'float3'
#             # 'force'
#             # 'integer'
#             # 'light'
#             # 'mass'
#             # 'percent'
#             # 'percent3'
#             # 'speed'
#             # 'string'
#             # 'time'
#             # 'uvcoord'
#             # 'vertmapname'
#
#         'tooltip' = '@table@message@'
#
#     Lumberjack will also add UI-specific data to the TreeData object, though
#     the end-user of the data is unlikely to need it. It's crucial that these
#     elements remain in the data object, lest Bad Things happen. This includes:
#
#     '_primary' - The 'primary' node is typically the one most recently clicked.
#     '_selected' - If True, the nodes is currently selected.
#     '_selectable' - Self-explanatory.
#     '_flags' - Bitwise flags for things like expand/contract, row color, etc.
#
#     COMMAND NODES:
#     --------------
#
#     Command nodes are grayed-out nodes that only appear in the tree for the
#     purpose of firing a command, e.g. the (new group), (new form), and
#     (new control) nodes in the Form Editor.
#
#     To avoid confusing these nodes with data nodes, these should be added
#     as metadata to the parent node, rather than as literal nodes within
#     the data structure.
#
#     In the below example, the command node will be added to the final slot
#     amongst the children of node 1.
#
#     `{
#         'id': 1,
#         'values': {
#             'enable': { 'value': True },
#             'name': { 'value': 'A' },
#             'value': { 'value': 1.0 }
#         }
#         'children': [...]
#         'command-nodes': [
#             {
#                 'command': 'myGreatCommand',
#                 'label': '(My Great Command)',
#                 'index': -1
#             }
#         ]
#     }`
#
#
#     EXAMPLE DATA STRUCTURE:
#     -----------------------
#
#     `{
#         'columns': [
#             {
#                 'internal-name': 'enable',
#                 'width': 20,
#                 'icon-resource': 'myIconResource'
#             }, {
#                 'internal-name': 'name',
#                 'width': -1,
#                 'primary': True
#             }, {
#                 'internal-name': 'value',
#                 'width': -3
#             }
#         ],
#         'data': {
#             id: 'root', # Root node id is semantic-only; it is ignored.
#             children: [
#                 {
#                     'id': 1,
#                     'values': {
#                         'enable': { 'value': True },
#                         'name': { 'value': 'A' },
#                         'value': { 'value': 1.0 }
#                     }
#                     'children': [
#                         {
#                             'id': 2,
#                             'values': {
#                                 'enable': {
#                                     'color': 'hdr(1.0, 1.0, 0.0)'
#                                     'value': False
#                                     },
#                                 'name': {
#                                     'color': '#123456',
#                                     'font-weight': 'bold',
#                                     'font-style': 'italic',
#                                     'value': 'B'
#                                     },
#                                 'value': {
#                                     'value': 2.0
#                                     }
#                             }
#                         }
#                     ],
#                     'command-nodes': [
#                         {
#                             'command': 'myGreatCommand',
#                             'label': '(My Great Command)',
#                             'index': -1
#                         }
#                     ]
#                 }, {
#                     'id': 3,
#                     'values': {
#                         'enable': { 'value': True },
#                         'name': { 'value': 'C' },
#                         'value': { 'value': 3.0 }
#                     }
#                 }
#             ]
#         }
#     }`
#     """
#
#     def __init__(self, columns=[], data={}):
#         self._data = data
#
#     def rebuild(self, data):
#         self._data = data
#
#     def update(self, node_id, column_name, value_dict):
#         # TODO
#         # Recursively search for cell by node_id and column_name, then replace
#         # its 'values' dictionary with value_dict
#         pass
#
#     @property
#     def data(self):
#         return self._data
#
#     @property
#     def root(self):
#         # TODO
#         # returns root node object
#         pass
