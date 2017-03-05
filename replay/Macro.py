# python

import lx, re
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

    def current_line():
        doc = """The current line in the macro, used to execute step-by-step. It is 
        initially set to zero, to start with the first command. It is increased after 
        running a step, so the run_next_line executes the next line next time."""
        def fget(self):
            return self.__class__._current_line
        def fset(self, value):
            self.__class__._current_line = value
        return locals()

    current_line = property(**current_line())

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

    def format_extensions():
        doc = """List of extensions to be used in file dialogs."""
        def fget(self):
            res = list()
            for val in self.__class__._export_formats.itervalues():
                res.append(val[0])
            return self._export_formats.keys()
        return locals()

    format_extensions = property(**format_extensions())

    def is_empty():
        doc = """Return true if there are no recorded commands."""
        def fget(self):
            return len(self.commands) == 0
        return locals()

    is_empty = property(**is_empty())

    def add_command(self, **kwargs):
        return self.add_child(**kwargs)

    """Clear all commands and relevant data"""
    def clear(self):
        self.root.delete_descendants()
        self.file_path = None

    def parse_LXM(self, input_path):
        """Parse an LXM file and store its commands in the `commands` property."""

        self.root.delete_descendants()

        # Open the .lxm input file and save the path:
        input_file = open(input_path, 'r')
        self.file_path = input_path

        command_with_comments = []
        # Loop over the lines to get all the command strings:
        for input_line in input_file:
            if not input_line: continue

            command_with_comments.append(input_line)

            # If this line is a comment, just append it to the full command:
            if input_line[0] == "#":
				continue

            # Parse the command and store it in the commands list:
            self.add_command(command_string=command_with_comments)
            command_with_comments = []

        # Close the .lxm input file:
        input_file.close()

    def parse_Python(self):
        """Parse a Python file and store its commands in the `commands` property.
        If the python code contains anything other than `lx.eval` and `lx.command`
        calls, parse will raise an error."""
        pass

    def parse_json(self):
        """Parse a json file and store its commands in the `commands` property.
        Note that json must be formatted exactly as exported using the `render_json()`
        method, else parse will raise an error."""
        pass

    def run(self):
        """Runs the macro."""
        
        # Run every command in the macro:
        for command in self.commands:
            command.run()

    def run_next_line(self):
        """Runs the next line in the macro."""
        
        # Select current command and run it:
        command = self.commands[self.current_line]
        command.run()
        
        # Increase the line counter, so next time we execute the next command:
        self.current_line += 1

        # If the line counter is out of bounds, restart the counter:
        # NOTE: This will probably be changed in the future.
        if self.current_line == len(self.commands):
			self.current_line = 0

    def render_LXM(self, output_path):
        """Generates an LXM string for export."""

        # Open the .lxm input file
        output_file = open(output_path, 'w')

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            text = command.render_LXM()
            output_file.write(text + "\n")

        output_file.close()

    def render_Python(self):
        """Generates a Python string for export."""
        # Open the .lxm input file
        output_file = open(output_path, 'w')

        output_file.write("# python\n")

        # Loop over the commands to get all the command strings:
        for command in self.commands:
            text = command.render_Python()
            output_file.write(text + "\n")

        output_file.close()

    def render_json(self):
        """Generates a json string for export."""
        pass
