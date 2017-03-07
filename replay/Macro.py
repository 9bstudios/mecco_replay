# python

import lx, re, os
import json
import lumberjack
from MacroCommand import MacroCommand

class Macro(lumberjack.Lumberjack):
    """Our own Replay-specific subclass of the Lumberjack treeview class. This
    class will be instantiated any time MODO wants to use it, which can be
    pretty often.

    It is effectively a Singleton: most of its methods are class-wide, so we don't need to
    store a specific instance of the class, but rather work with the class itself.

    Also contains everything necessary to store, manage, and save a MODO maco or
    script using Replay. All macro management commands make use of this object class.

    To work around the lack of a gloal namespace in MODO, `Macro()` objects
    work entirely with class variables and classmethods."""

    _file_path = None
    _file_format = None

    # export formats in (file extension, user name of format, file pattern)
    _export_formats = {
                       'lxm' : ('lxm', 'LXM file', '*.LXM;*.lxm'),
                       'py' : ('py', 'Python file', '*.py'),
                       'json' : ('json', 'JSON file', '*.json')
                       }
    _current_line = 0

    # We extend the default Lumberjack `TreeNode` object for our own nefarious purposes.
    # To use this class in Lumberjack, we set the `_TreeNodeClass` to our `TreeNode` subclass.
    _TreeNodeClass = MacroCommand

    def __init__(self):
        super(self.__class__, self).__init__()

    def file_path():
        doc = """The file path for the current macro. If None, assume that the macro
        is unsaved, and needs a save-as. When a macro is loaded and parsed, be
        sure to set this value. (It will not be set automatically.)"""
        def fget(self):
            return self.__class__._file_path
        def fset(self, value):
            self.__class__._file_path = value
        return locals()

    file_path = property(**file_path())

    def file_format():
        doc = """The file format for the current macro. If None, assume that the macro
        is unsaved, and needs a save-as."""
        def fget(self):
            return self.__class__._file_format
        def fset(self, value):
            self.__class__._file_format = value
        return locals()

    file_format = property(**file_format())

    def commands():
        doc = """The list of `MacroCommand()` objects for the macro, in
        order from first to last."""
        def fget(self):
            return self.root.children
        return locals()

    commands = property(**commands())

    def format_names():
        doc = """List of format names used internally."""
        def fget(self):
            return self.__class__._export_formats.keys()
        return locals()

    format_names = property(**format_names())

    def format_unames():
        doc = """List of format User names used to display in file dialogs."""
        def fget(self):
            res = list()
            for val in self.__class__._export_formats.itervalues():
                res.append(val[1])
            return res
        return locals()

    format_unames = property(**format_unames())

    def format_patterns():
        doc = """List of format patterns used to display in file open dialogs."""
        def fget(self):
            res = list()
            for val in self.__class__._export_formats.itervalues():
                res.append(val[2])
            return res
        return locals()

    format_patterns = property(**format_patterns())

    def format_extensions():
        doc = """List of extensions to be used in file dialogs."""
        def fget(self):
            res = list()
            for val in self.__class__._export_formats.itervalues():
                res.append(val[0])
            return res
        return locals()

    format_extensions = property(**format_extensions())

    def name_by_extension(self, extension):
        doc = """Returns format name by given extension"""
        for key, val in self.__class__._export_formats.iteritems():
            if val[0].lower() == extension.lower():
                return key

        return self.__class__._export_formats.keys()[0]

        # Return lxm for unknown extensions

    def is_empty():
        doc = """Return true if there are no recorded commands."""
        def fget(self):
            return len(self.commands) == 0
        return locals()

    is_empty = property(**is_empty())

    def add_command(self, **kwargs):
        return self.add_child(**kwargs)

    def parse(self, input_path):
        """Parse a macro file and store its commands in the `commands` property."""
        self.root.deselect_descendants()
        self.root.delete_descendants()

        format_name = self._parse_and_insert(input_path)

        # Store file path and extension
        self.file_path = input_path
        self.file_format = format_name

    def parse_and_insert(self, input_path):
        if self.primary is None:
            # If there's no primary node, insert at zero
            self._parse_and_insert(input_path, index=0)
        else:
            # If there's a primary node, insert right after it
            self._parse_and_insert(input_path, index=self.primary.index+1)

    def _parse_and_insert(self, input_path, **kwargs):
        """Parse a macro file and store its commands in the `commands` property."""

        # Parse file extension
        unused, file_extension = os.path.splitext(input_path)
        file_extension = file_extension[1:]

        # Lookup extension name
        format_name = self.name_by_extension(file_extension)

        if format_name == "lxm":
            self.parse_LXM(input_path, **kwargs)
        elif format_name == "py":
            self.parse_Python(input_path, **kwargs)
        else:
            self.parse_json(input_path, **kwargs)
        return format_name

    def parse_LXM(self, input_path, **kwargs):
        """Parse an LXM file and store its commands in the `commands` property."""

        # Open the .lxm input file and save the path:
        input_file = open(input_path, 'r')

        first_line = True

        command_with_comments = []
        # Loop over the lines to get all the command strings:
        for input_line in input_file:
            if first_line:
                first_line = False
                if input_line != "#LXMacro#\n":
                    raise Exception("Wrong shebang {sb}".format(sb=input_line))
                continue

            if not input_line: continue

            command_with_comments.append(input_line[:-1])

            # If this line is a comment, just append it to the full command:
            if input_line[0] == "#":
				continue

            kwargs['index'] = kwargs.get('index', 0)

            # Parse the command and store it in the commands list:
            self.add_command(command_string = command_with_comments, **kwargs)
            command_with_comments = []

            # We need to increment the index with each loop, lest we insert nodes in reverse order
            kwargs['index'] += 1

        # Close the .lxm input file:
        input_file.close()

    def parse_Python(self, input_path, **kwargs):
        """Parse a Python file and store its commands in the `commands` property.
        If the python code contains anything other than `lx.eval` and `lx.command`
        calls, parse will raise an error."""

        # Open the .py input file:
        input_file = open(input_path, 'r')

        try:
            first_line = True

            command_with_comments = []
            # Loop over the lines to get all the command strings:
            for input_line in input_file:
                if first_line:
                    first_line = False
                    if input_line != "# python\n":
                        raise Exception("Wrong shebang {sb}".format(sb=input_line))
                    continue

                if not input_line: continue

                # If this line is a comment, just append it to the full command:
                if input_line[0] == "#":
                    command_with_comments.append(input_line[:-1])
	            continue

                # Replace lx.eval with function returning command
                store_lx_eval = lx.eval
                def return_cmd(cmd):
                    return cmd
                lx.eval = return_cmd

                cmd = eval(input_line)

                # Restore lx.eval
                lx.eval = store_lx_eval
                if cmd is not None:
                    command_with_comments.append(cmd)

                # Parse the command and store it in the commands list:
                self.add_command(command_string = command_with_comments, **kwargs)
                command_with_comments = []

        except:
            # Close the .lxm input file:
            input_file.close()

            # Restore lx.eval
            lx.eval = store_lx_eval
            raise Exception('Failed to parse file "%s".' % input_path)

        # Close the .lxm input file:
        input_file.close()

    def parse_json(self, input_path, **kwargs):
        """Parse a json file and store its commands in the `commands` property."""

        # Open the .lxm input file and save the path:
        input_file = open(input_path, 'r')

        # Read the content
        content = input_file.read()

        # Parse json
        jsonStruct = json.loads(content)

        # Close the .lxm input file:
        input_file.close()

        # Loop over the commands to get all the command json data:
        for cmdJson in jsonStruct:
            self.add_command(command_json = cmdJson, **kwargs)

    def run(self):
        """Runs the macro."""

        # Run every command in the macro:
        for command in self.commands:
            command.run()

    def run_next_line(self):
        """Runs the next line in the macro, i. e. the primary one."""

        # Select the primary command:
        command = self.primary

        # If there's a primary selected command, run it:
        if command:
            command.run()
        else:
			return

        # Get the index for the next command, which will now be the primary one:
        next_command_index = self.commands.index(command) + 1
        if next_command_index == len(self.commands): next_command_index = 0

        # Set as primary the next command:
        command.selected = False
        self.commands[next_command_index].selected = True

    def render_LXM(self, output_path):
        """Generates an LXM string for export."""

        # Open the .lxm file
        output_file = open(output_path, 'w')

        output_file.write("#LXMacro#\n")

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            lines = command.render_LXM()
            for line in lines:
                output_file.write(line + "\n")

        output_file.close()

    def render_Python(self, output_path):
        """Generates a Python string for export."""
        # Open the .py file
        output_file = open(output_path, 'w')

        output_file.write("# python\n")

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            lines = command.render_Python()
            for line in lines:
                output_file.write(line + "\n")

        output_file.close()

    def render_json(self, output_path):
        """Generates a json string for export."""

        # Open the .py file
        output_file = open(output_path, 'w')

        res = list()
        # Loop over the commands to get all the command json data:
        for command in self.commands:
            res.append(command.render_json())

        output_file.write(json.dumps(res, indent=4))

        output_file.close()

    def render(self, format_val, file_path):
        if format_val == "lxm":
            self.render_LXM(file_path)
        elif format_val == "py":
            self.render_Python(file_path)
        else:
            self.render_json(file_path)

    def insert_comment_before_current_command(self, comment):
        selecteds = self.selected_children
        if len(selecteds) == 0:
            raise Exception("There is no selected command")
        for sel in selecteds:
            for line in ("#" + line for line in comment.split('\n')):
                sel.user_comment_before.append(line)
