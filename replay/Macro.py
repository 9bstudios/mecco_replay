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
    _commands = []
    _export_formats = ['lxm', 'py', 'json']

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
            return self._file_path
        def fset(self, value):
            self._file_path = value
        return locals()

    file_path = property(**file_path())

    def commands():
        doc = """The list of `MacroCommand()` objects for the macro, in
        order from first to last."""
        def fget(self):
            return self._commands
        return locals()

    commands = property(**commands())

    def export_formats():
        doc = """The list of `MacroCommand()` objects for the macro, in
        order from first to last."""
        def fget(self):
            return self._export_formats
        return locals()

    export_formats = property(**export_formats())

    def is_empty():
        doc = """Return true if there are no recorded commands."""
        def fget(self):
            return len(self.commands) == 0
        return locals()

    is_empty = property(**is_empty())

    def add_command(self, **kwargs):
        return self.add_child(**kwargs)

    def parse_LXM(self, input_path):
        """Parse an LXM file and store its commands in the `commands` property."""

        self.root.delete_descendants()

        # Open the .lxm input file
        input_file = open(input_path, 'r')

        # Save input path
        self.file_path = input_path

        # Loop over the lines to get all the command strings:
        for input_line in input_file:
            if not input_line: continue

            # TODO: Ultimately we need to attach comments to whichever command
            # follows them using the `comment_before` property.
            # Skip comments:
            if input_line[0] == "#": continue

            # Parse the command and store it in the commands list:
            self.add_command(input_line)

    @classmethod
    def parse_Python(cls):
        """Parse a Python file and store its commands in the `commands` property.
        If the python code contains anything other than `lx.eval` and `lx.command`
        calls, parse will raise an error."""
        pass

    @classmethod
    def parse_json(cls):
        """Parse a json file and store its commands in the `commands` property.
        Note that json must be formatted exactly as exported using the `render_json()`
        method, else parse will raise an error."""
        pass

    def run(self):
        """Runs the macro."""
        for command in self.commands:
            # See http://modo.sdk.thefoundry.co.uk/wiki/Python#lx.command
            pass

    @classmethod
    def render_LXM(cls, output_path):
        """Generates an LXM string for export."""

        # Open the .lxm input file
        output_file = open(output_path, 'w')

        # Loop over the commands to get all the command strings:
        for command in cls.commands:
            text = connand.render_LXM()
            output_file.write(text + "\n")

    @classmethod
    def render_Python(cls):
        """Generates a Python string for export."""
        pass

    @classmethod
    def render_json(cls):
        """Generates a json string for export."""
        pass
