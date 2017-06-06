# python

import lx, re, os
import json
import copy
import lumberjack
from MacroCommand import MacroCommand
from MacroCommandArg import MacroCommandArg
from MacroBlockCommand import MacroBlockCommand
from Notifier import Notifier
from LXMParser import LXMParser
from CommandAttributes import CommandAttributes

class Macro(lumberjack.Lumberjack):
    '''
    Our own Replay-specific subclass of the Lumberjack treeview class. This
    class will be instantiated any time modo wants to use it, which can be
    pretty often.

    It is effectively a Singleton: most of its methods are class-wide, so we
    don't need to store a specific instance of the class, but rather work with
    the class itself.

    Also contains everything necessary to store, manage, and save a modo macro
    or script using Replay. All macro management commands make use of this
    object class.

    To work around the lack of a global namespace in modo, `Macro()` objects
    work entirely with class variables and classmethods.

    Args:
        None

    Returns:
        Macro

    .. todo::
        - why do you have an init if you aren't changing the constructor logic?
        - In fact Lumberjack takes no args or kwargs so why does it have an init
          either?
        - A good redesign would be to create a modo context class that acts as
          you global space. Context would have a register method that gets
          called within the constructor of Macro, and if an instance is already
          registered Context raises an error.  Alternatively, you could
          construct a Macro upon creation of a context and use
          Context.get_macro() to retrieve it. Thus no class methods and
          attributes.  The later will enable you to build objects in context,
          and thus may obviate your need for builders.
    '''
    _file_path = None
    _file_format = None

    # export formats in (file extension, user name of format, file pattern)
    _import_formats = {
                       'lxm' : ('lxm', 'LXM file', '*.LXM;*.lxm'),
                       'py' : ('py', 'Python file', '*.py'),
                       'json' : ('json', 'JSON file', '*.json')
                       }

    # export formats in (file extension, user name of format, file pattern)
    _export_formats = {
                       'lxm' : ('lxm', 'LXM file', '*.LXM;*.lxm'),
                       'py' : ('py', 'Python file', '*.py'),
                       'json' : ('json', 'JSON file', '*.json')
                       }
    _current_line = 0

    # Keeps track of unsaved changes for use in `replay.fileClose`.
    _unsaved_changes = False

    # If a color has been modified, we'll need to reset (see `replay.argEdit`)
    _reset_color_on_select = False

    def __init__(self):
        super(self.__class__, self).__init__()

    # We extend the default Lumberjack `TreeNode` object for our own nefarious purposes.
    # To use this class in Lumberjack, we overwrite the create_child method to create our `TreeNode` subclasses.
    def create_child_node(self, **kwargs):
        '''
        Override of Lumberjack.create_child that enables the creation of
        TreeNode subclasses

        Args:
            \**kwargs: MacroCommand or MacroBlockCommand kwargs

        Returns:
            MacroCommand or MacroBlockCommand
        '''
        if kwargs.get('type', "command") == "command":
            node = MacroCommand(temporary=self.track_insertions, **kwargs)
        else:
            node = MacroBlockCommand(temporary=self.track_insertions, **kwargs)

        return node

    def file_path():
        doc = '''
        dict: local context
        Gets and sets the file path for the current macro. If None, assume that the macro
        is unsaved, and needs a save-as. When a macro is loaded and parsed, be
        sure to set this value. (It will not be set automatically.)
        '''
        def fget(self):
            return self.__class__._file_path
        def fset(self, value):
            self.__class__._file_path = value
        return locals()

    file_path = property(**file_path())

    def reset_color_on_select():
        doc = '''
        dict: local context
        Gets and sets the UI color upon selection
        If set to True, the next select event will run "select.color {0 0 0}"
        to clear out any color values left behind by an argument edit (see replay.argEdit)
        '''
        def fget(self):
            return self.__class__._reset_color_on_select
        def fset(self, value):
            self.__class__._reset_color_on_select = value
        return locals()

    reset_color_on_select = property(**reset_color_on_select())

    def file_format():
        doc = '''
        dict: local context
        Gets and sets the file format for the current macro
        If None, assume that the macro is unsaved, and needs a save-as.
        '''
        def fget(self):
            return self.__class__._file_format
        def fset(self, value):
            self.__class__._file_format = value
        return locals()

    file_format = property(**file_format())

    def unsaved_changes():
        doc = '''
        dict: local context
        Gets and sets the current macro unsaved changes state
        '''
        def fget(self):
            return self.__class__._unsaved_changes
        def fset(self, value):
            self.__class__._unsaved_changes = value
        return locals()

    unsaved_changes = property(**unsaved_changes())

    def commands():
        doc = '''
        dict: local context
        Gets list of MacroCommand objects for the macro, in order from first to
        last.
        '''
        def fget(self):
            return self.root.children
        return locals()

    commands = property(**commands())


    def selected_commands():
        doc = '''
        dict: local context
        Gets a list of implicitly selected MacroCommand instances,
        including both selected nodes and nodes that have selected descendants.
        '''
        def fget(self):
            nodes = set()
            for node in self.root.selected_descendants:
                if isinstance(node, MacroCommand):
                    if bool(node.selected_descendants) or node.selected:
                        nodes.add(node)
            return list(nodes)
        return locals()

    selected_commands = property(**selected_commands())

    def selected_args():
        doc = '''
        dict: local context
        Gets a list of implicitly selected MacroCommandArg instances,
        including both selected nodes and nodes that have selected descendants.
        '''
        def fget(self):
            nodes = set()
            for node in self.root.selected_descendants:
                if isinstance(node, MacroCommandArg):
                    nodes.add(node)
            return list(nodes)
        return locals()

    selected_args = property(**selected_args())

    @property
    def import_format_names(self):
        '''list: names of import formats'''
        return [k for k, v in self._import_formats.iteritems()]

    @property
    def import_format_extensions(self):
        '''list: extensions of import formats'''
        return [v[0] for k, v in self._import_formats.iteritems()]

    @property
    def import_format_unames(self):
        '''list: unames of import formats'''
        return [v[1] for k, v in self._import_formats.iteritems()]

    @property
    def import_format_patterns(self):
        '''list: patterns of import formats'''
        return [v[2] for k, v in self._import_formats.iteritems()]

    @property
    def export_format_names(self):
        '''list: names of export formats'''
        return [k for k, v in self._export_formats.iteritems()]

    @property
    def export_format_extensions(self):
        '''list: extensions of export formats'''
        return [v[0] for k, v in self._export_formats.iteritems()]

    @property
    def export_format_unames(self):
        '''list: unames of export formats'''
        return [v[1] for k, v in self._export_formats.iteritems()]

    @property
    def export_format_patterns(self):
        '''list: patterns of export formats'''
        return [v[2] for k, v in self._export_formats.iteritems()]

    def is_empty():
        doc = '''
        Gets command empty state
        Returns True if there are no recorded commands.

        Args:
            None

        Returns:
            dict: local context
        '''
        def fget(self):
            return len(self.commands) == 0
        return locals()

    is_empty = property(**is_empty())

    def add_command(self, **kwargs):
        '''
        Adds a command as a child to the kwargs receiver???
        - Arman receiver is a object in which child is added. It could be 'self' and in that case child will be added in 
          Lumberjack tree. It also could be another object. This is used for handling parsing errors. Tree nodes are collected in TmpCommandCache
          object and only if parsing successes Lumberjack content is cleared and new commands are added.

        Args:
            \**kwargs: varkwargs

        Returns:
            None

        .. todo::
            - add_child returns None because it has no return statement, it is
              silly for this command to return the results of a coomand that has
              not return.
            - Arman. If receiver is 'self' add_child (from Lumberjack) returns new node and it is actually used (see lineInsert).
        '''
        node = kwargs.get('receiver', self).add_child(type='command', **kwargs)
        if self.track_insertions:
            self.insertions.append(node)
        return node

    def add_block(self, **kwargs):
        '''
        Adds a command as a block to the kwargs receiver???
        - Arman receiver is a object in which child is added. It could be 'self' and in that case child will be added in 
          Lumberjack tree. It also could be another object. This is used for handling parsing errors. Tree nodes are collected in TmpCommandCache
          object and only if parsing successes Lumberjack content is cleared and new commands are added.

        Args:
            \**kwargs: varkwargs

        Returns:
            None

        .. todo::
            - receiver should be an explicit arg if this method expects it
            - again add_child has no return
            - Arman. If receiver is 'self' add_child (from Lumberjack) returns new node and it is actually used (see lineInsert).
        '''
        node = kwargs.get('receiver', self).add_child(type='block', **kwargs)
        if self.track_insertions:
            self.insertions.append(node)
        return node

    def select_event_treeview(self):
        '''
        Used to prevent modo from crashing when color modified forms disappear
        Fires whenever the TreeView detects a user selection event.

        Args:
            None

        Returns:
            None
        '''
        # Welcome to an advanced course on Stupid Things About Modo!
        # If we modify a color channel and then suddenly our form control
        # disappears (because of a selection change), modo will crash. Yay!
        # For those who do not like this behavior, we black out the current
        # color selection whenever we make a change.
        if self.reset_color_on_select:
            try:
                lx.eval('!!select.color {0 0 0}')
                self.reset_color_on_select = False
            except:
                pass

    def path_event(self):
        '''
        Fired by TreeNode objects whenever the node's path property is changed.

        Args:
            None

        Returns:
            None
        '''
        self.unsaved_changes = True
        notifier = Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def select_event(self):
        '''
        Fires whenever a TreeNode selected state is changed.

        Args:
            None

        Returns:
            None
        '''
        notifier = Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def select(self, index):
        '''
        Selects child node its index in children

        Args:
            index (int): child node index

        Returns:
            MacroCommand or MacroBlockCommand
        '''
        self.root.deselect_descendants()
        if isinstance(index, int):
            self.root.children[index].selected = True
        else:
            self.node_for_path(index).selected = True
                
    def merge_with_build_in(self, file_path):
        if len(self.insertions) == 0:
            return;
        primary_path = self.insertions[0].path[0:1]
        for inserted in self.insertions:
            inserted.delete()
        
        self._parse_and_insert(file_path, path=primary_path, receiver=self)        

    _track_insertions = False
    _insertions = []
    
    def track_insertions():
        def fget(self):
            return self.__class__._track_insertions
        def fset(self, value):
            self.__class__._track_insertions = value
        return locals()

    track_insertions = property(**track_insertions())
    
    def insertions():
        def fget(self):
            return self.__class__._insertions
        def fset(self, value):
            self.__class__._insertions = value
        return locals()

    insertions = property(**insertions())
                
    def start_track_insertions(self, start):
        if start:
            del self.insertions[:]
            self.track_insertions = True
        else:
            self.track_insertions = False

    class TmpCommandCache:
        '''
        Temporary command cache

        Args:
            None

        Returns:
            TmpCommandCache
        '''
        def __init__(self):
            self.child_args = []

        def add_child(self, **kwargs):
            '''
            Adds kwargs to child_args

            Args:
                \**kwargs: child args

            Returns:
                None
            '''
            tmp = dict(kwargs)
            # Need to remove receiver before deepcopy
            tmp.pop('receiver', None)
            self.child_args.append(copy.deepcopy(tmp))

        def children_create_args(self):
            '''
            Yields child args

            Args:
                None

            Yields:
                dict: child args
            '''
            for args in self.child_args:
                yield args

    def parse_and_insert_string(self, string, path):
        '''
        Parse a string and append parsed string to children

        Args:
            string (str): command string
            path (str): filepath to macro

        Returns:
            nodes (list): list of child nodes
        '''
        cache = Macro.TmpCommandCache()

        self.parse_LXM_string(string, receiver=cache, path=path)

        nodes = []
        for kwargs in cache.children_create_args():
            nodes.append(self.add_child(**kwargs))

        return nodes

    def parse(self, mode, input_path):
        '''
        Parse a macro file specified by input_path according to parse mode

        Args:
            mode (str): parse mode. Options include: open and insert
            input_path (str): path to command to be parsed

        Returns:
            None
        '''
        cache = Macro.TmpCommandCache()

        if mode == 'open':
            format_name = self._parse_and_insert(input_path, receiver=cache)
        elif mode == 'insert':
            format_name = self.parse_and_insert(input_path, receiver=cache)
        else:
            raise Exception("Wrong mode")

        if mode == 'open':
            self.root.deselect_descendants()
            self.root.delete_descendants()

        for kwargs in cache.children_create_args():
            self.add_child(**kwargs)

        # Store file path and extension
        if mode == 'open':
            self.file_path = input_path
            self.file_format = format_name
            if len(self.children) != 0:
                self.select(0)

    def parse_and_insert(self, input_path, **kwargs):
        '''
        Parse macro fule specified by input_path and insert

        Args:
            input_path (str): path to command to be parsed
            \**kwargs: varkwargs

        Returns:
            None
        '''
        if self.primary is None:
            # If there's no primary node, insert at zero
            self._parse_and_insert(input_path, path=[0], **kwargs)
        else:
            # If there's a primary node, insert right after it
            path = self.primary.path
            path[-1] += 1
            self._parse_and_insert(input_path, path=path, **kwargs)

    def _parse_and_insert(self, input_path, **kwargs):
        '''
        Parse a macro file and insert new commands at position given by kwargs['path']
        without erasing existing commands.

        Args:
            input_path (str): macro file path
            \**kwargs: varkwargs

        Returns:
            str: format name
        '''
        # Parse file extension
        unused, file_extension = os.path.splitext(input_path)
        file_extension = file_extension[1:]

        # Lookup extension name
        for key, val in self._export_formats.iteritems():
            if val[0] == file_extension.lower():
                format_name = key
                break

        if format_name == "py":
            self.parse_LXM(input_path, **kwargs)
        elif format_name == 'json':
            self.parse_json(input_path, **kwargs)
        else:
            self.parse_LXM(input_path, **kwargs)
        return format_name

    class MacroTreeBuilder:
        '''
        Builder class used for creating Macro instances

        Args:
            macro (Macro): macro
            \**kwargs: varkwargs

        Returns:
            MacroTreeBuilder

        .. todo::
            - remove this from the Macro body, you do not ever include a builder
              class inside the body of the class that it builds
            - Arman. The same could be said about parse_LXM. If parse_LXM is there why to not include 
              the part of it's implementation inside class?
        '''
        def __init__(self, macro, **kwargs):
            self.macro = macro
            if 'path' in kwargs:
                self.path = kwargs.get('path', None)
            else:
                self.path = [kwargs.get('index', 0)]
            kwargs.pop('index', None)
            kwargs.pop('path', None)
            self.kwargs = kwargs
            self.comments = []
            self.meta = []

        def buildType(self, type):
            '''
            File format of Macro

            Args:
                type (str): either lxm or py. Default: py

            Returns:
                None
            '''
            if type == "LXM":
                self.macro.file_format = "lxm"
            else:
                self.macro.file_format = "py"

        def buildCommand(self, line, suppress):
            '''
            Adds a command to the macro

            Args:
                line (str): command
                suppress (bool): whether to suppress the command

            Returns:
                None
            '''
            self.kwargs['path'] = self.path
            self.macro.add_command(command=line, comment=self.comments, meta = self.meta, suppress=suppress, **self.kwargs)
            self.path[-1] += 1

            self.comments = []
            self.meta = []

        def buildBlockStart(self, block, suppress):
            '''
            Begins block command

            Args:
                block (list): block
                suppress (bool): whether to suppress the block

            Returns:
                None
            '''
            self.kwargs['path'] = self.path
            self.macro.add_block(
                name=block[-1][0], comment=self.comments, meta=self.meta,
                suppress=suppress, **self.kwargs
            )
            self.path.append(0)

            self.comments = []
            self.meta = []

        def buildBlockEnd(self, block):
            '''
            Ends a previously started block command

            Args:
                block (list): block

            Returns:
                None
            '''
            del self.path[-1]
            self.path[-1] += 1

            self.comments = []
            self.meta = []

        def buildMeta(self, name, value):
            '''
            Append name and its assosciated metadata to self.meta

            Args:
                name (str): metadata name
                value (str or dict): metadata
            '''
            try:
                self.meta.append((name, json.loads(value)))
            except:
                # For backward compatibility
                self.meta.append((name, value))

        def buildComment(self, comment):
            '''
            Adds comment to self.comments

            Args:
                comment (str): comment to be added

            Returns:
                None
            '''
            self.comments.append(comment)

    def parse_LXM(self, input_path, **kwargs):
        '''
        Parse an LXM file and store its commands in the commands property.

        Args:
            input_path (str): macro file path
            \**kwargs: MacroBuilder kwargs

        .. todo::
            - So this command calls its own builder class, and provides itself
              as a constuctor argument, then a parser, defined within the method
              body, is used to "parse" this builder instance.  What could
              possibly go wrong?
            - Arman: Really don't understand what can go wrong there. Could you please explain?
        '''
        parser = LXMParser()
        builder = Macro.MacroTreeBuilder(self, **kwargs)
        parser.parse(input_path, builder)

    def parse_LXM_string(self, string, **kwargs):
        '''
        Parse an LXM file and store its commands in the commands property.

        Args:
            input_path (str): macro file path
            \**kwargs: MacroBuilder kwargs

        Returns:
            None
        '''
        parser = LXMParser()
        builder = Macro.MacroTreeBuilder(self, **kwargs)
        parser.parseString(string, builder)

    def parse_json(self, input_path, **kwargs):
        '''
        Parse a json file and store its commands in the commands property.

        Args:
            input_path (str): macro file path
            \**kwargs: MacroBuilder kwargs

        Returns:
            None
        '''
        # Open the .lxm input file and save the path:
        input_file = open(input_path, 'r')

        # Read the content
        content = input_file.read()

        # Parse json
        jsonStruct = json.loads(content)

        # Close the .lxm input file:
        input_file.close()

        path = kwargs.get('path', [0])
        if 'path' in kwargs:
            del kwargs['path']

        # Loop over the commands to get all the command json data:
        for cmdJson in jsonStruct:
            kwargs['path'] = path
            self.add_json_command_or_block(cmdJson, **kwargs)
            path[-1] += 1

    def add_json_command_or_block(self, cmdJson, **kwargs):
        '''
        Adds json as command or block to macro

        Args:
            cmdJson (dict): json command
            \**kwargs: MacroBuilder kwargs

        Returns:
            None
        '''
        if 'command' in cmdJson:
            self.add_command(command_json=cmdJson, **kwargs)
        else:
            self.add_block(block_json=cmdJson, **kwargs)

    def run(self):
        '''
        Runs the macro.

        Args:
            None

        Returns:
            None
        '''
        # Run every node with run attribute in the macro:
        for node in self.depth_first_search():
            if hasattr(node, 'run'):
                node.run()

    def all_suppressed(self):
        '''
        Whether all children are suppressed or not

        Args:
            None

        Returns:
            bool: suppression state of all children
        '''
        for child in self.children:
            if not child.suppress:
                return False

        return True

    def run_next_line(self):
        '''
        Runs the next line in the macro, ie. the primary one.

        Args:
            None

        Returns:
            tuple: prev_path, next_path
        '''
        # Select the primary command:
        if self.primary is None:
            self.select(0)

        command = self.primary
        start_path = command.path

        while command is not None and command.suppress:
            command.selected = False
            path = command.path
            path[-1] += 1
            if path[-1] == len(command.parent.children): path[-1] = 0
            if path == start_path:
                # All commands are suppresed
                return None
            command = self.node_for_path(path)

        # If there's a primary selected command, run it:
        if command:
            command.run()
        else:
            return None

        # Get the index for the next command, which will now be the primary one:
        next_command_path = command.path
        next_command_path[-1] += 1
        if next_command_path[-1] == len(command.parent.children): next_command_path[-1] = 0

        while self.node_for_path(next_command_path).suppress:
            next_command_path[-1] += 1
            if next_command_path[-1] == len(command.parent.children): next_command_path[-1] = 0

        # Set as primary the next command:
        command.selected = False
        prev_path = command.path
        self.node_for_path(next_command_path).selected = True
        new_path = next_command_path
        return (prev_path, new_path)

    def shebang(self, lxm, sep):
        '''
        Creates an appropriate shebang for writing to file

        Args:
            lxm (bool): lxm format
            sep (str): separator

        Returns:
            str: header

        '''
        res = ""
        if lxm:
            res = "#LXMacro#" + sep;
        else:
            res = "# python" + sep

        res += "# Made with Replay" + sep
        res += "# mechanicalcolor.com" + sep + sep

        return res

    def render_LXM(self, output_path):
        '''
        Generates an LXM string for export.

        Args:
            output_path (str): export filepath

        Returns:
            None
        '''
        # Open the .lxm file
        output_file = open(output_path, 'w')

        output_file.write(self.shebang(True, '\n'))

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            lines = command.render_LXM()
            for line in lines:
                output_file.write(line + "\n")

        output_file.close()

    def render_LXM_selected(self):
        '''
        Generates an LXM string for export.

        Args:
            None

        Returns:
            str: lxm text
        '''
        # Render shebang
        res = self.shebang(True, os.linesep)

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            lines = command.render_LXM_if_selected()
            for line in lines:
                res += line + os.linesep

        return res

    def render_Python(self, output_path):
        '''
        Generates a Python string for export.

        Args:
            output_path (str): export filepath

        Returns:
            None
        '''
        # Open the .py file
        output_file = open(output_path, 'w')

        output_file.write(self.shebang(False, '\n'))

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            lines = command.render_Python()
            for line in lines:
                output_file.write(line + "\n")

        output_file.close()

    def render_json(self, output_path):
        '''
        Writes commands as json to output path

        Args:
            output_path (str): export filepath

        Returns:
            None
        '''
        # Open the .py file
        output_file = open(output_path, 'w')

        res = list()
        # Loop over the commands to get all the command json data:
        for command in self.commands:
            res.append(command.render_json())

        output_file.write(json.dumps(res, indent=4))

        output_file.close()

    def render(self, format_val, file_path):
        '''
        Renders commands to file_path

        Args:
            format_val (str): format type. Options include: lxm, py. Default: json
            file_path (str): file to be written

        Returns:
            None
        '''
        if format_val == "lxm":
            self.render_LXM(file_path)
        elif format_val == "py":
            self.render_Python(file_path)
        else:
            self.render_json(file_path)

    def on_drag_drop(self, source_nodes):
        '''
        Updates source nodes upon drag'n'drop event

        Args:
            source_nodes (list): list of top level nodes

        Returns:
            None
        '''
        # After drag and drop update suppress state
        for node in source_nodes:
            node.update_suppress_for_node_and_descendants()
