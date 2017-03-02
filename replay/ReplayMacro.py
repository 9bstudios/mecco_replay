# python

class ReplayMacroCommand(object):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts. Note that if the `command`
    property is `None`, the `comment_before` property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)"""

    _command = None
    _args = {}
    _suppress = False
    _whitespace_before = None
    _comment_before = None
    _prefix = None
    _meta = {}

    def __init__(self, command_string=None):
        if command_string is not None:
            self.parse_string(command_string)

    def command():
        doc = "The base MODO command, e.g. `item.name`."
        def fget(self):
            return self._command
        def fset(self, value):
            self._command = value
        return locals()

    command = property(**command())

    def prefix():
        doc = """Usually one or two characters to prepend to the command string to
        suppress or force dialogs, etc. e.g. `!mesh.cleanup`

        `'!'`   - Suppress dialogs.
        `'!!'`  - Suppress all dialogs.
        `'+'`   - Show dialogs.
        `'++'`  - Show all dialogs.
        `'?'`   - Show command dialog.

        See http://sdk.luxology.com/wiki/Command_System:_Executing#Special_Prefixes"""
        def fget(self):
            return self._prefix
        def fset(self, value):
            self._prefix = value
        return locals()

    prefix = property(**prefix())

    def args():
        doc = """A list of dictionaries with arguments, values, and datatypes.
        [
            {
                'argName': 'argname',
                'argUsername': 'Argument Name',
                'argType': 0, # 0 for generic objects, 1 for integers, 2 for floats an 3 for strings
                'argTypeName': 'boolean',
                'argDesc': 'What the argument does.',
                'argExample': 'Example if available.'
            }
        ]"""
        def fget(self):
            return self._args
        def fset(self, value):
            self._args = value
        return locals()

    args = property(**args())

    def suppress():
        doc = "Boolean. Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            return self._suppress
        def fset(self, value):
            self._suppress = value
        return locals()

    suppress = property(**suppress())

    def whitespace_before():
        doc = """Integer number of lines to insert before the current command when
        exporting to code."""
        def fget(self):
            return self._whitespace_before
        def fset(self, value):
            self._whitespace_before = value
        return locals()

    whitespace_before = property(**whitespace_before())

    def comment_before():
        doc = """String to be added as comment text before the command. Long strings
        will automatically be broken into lines of 80 characters or less. Appropriate
        comment syntax will be rendered at export time. Include only the raw string."""
        def fget(self):
            return self._comment_before
        def fset(self, value):
            self._comment_before = value
        return locals()

    comment_before = property(**comment_before())

    def meta():
        doc = """A dictionary of metadata values for use in the GUI editor. These are stored
        as specially-formatted comments within the code itself. These could include things like
        row color.

        e.g. {'row_color': 'red'}

        Renders as:
        # replay meta row_color: 'red'"""
        def fget(self):
            return self._meta
        def fset(self, value):
            self._meta = value
        return locals()

    meta = property(**meta())

    def parse_string(self, command_string):
        """Parse a normal MODO command string into its constituent parts, and
        stores those in the `command` and `args` properties for the object."""
        pass

    def meta(self):
        """Returns a dict of metadata for the command from the MODO commandservice,
        as listed here: http://sdk.luxology.com/wiki/Commandservice#command.username."""

        if not self.command:
            raise Exception("Command string not set.")
            return

        query_terms = [
            'desc',
            'usage',
            'example',
            'flags',
            'username',
            'tooltip',
            'help',
            'icon'
        ]

        meta = {}

        for term in query_terms:
            meta[term] = lx.eval("query commandservice command.%s ? %s" % (term, self.command))

        return meta

    def retreive_args(self):
        """Retrieve a list of arguments and datatypes from MODO's commandservice.
        See http://sdk.luxology.com/wiki/Commandservice#command.argNames

        Example:
        [
            {
                'argName': 'argname',
                'argUsername': 'Argument Name',
                'argType': 0, # 0 for generic objects, 1 for integers, 2 for floats an 3 for strings
                'argTypeName': 'boolean',
                'argDesc': 'What the argument does.',
                'argExample': 'Example if available.'
            }
        ]"""

        if not self.command:
            raise Exception("Command string not set.")
            return

        # Names of the arguments for the current command.
        argNames = lx.eval("query commandservice command.argNames ? %s" % self.command)

        # No arguments to report
        if not argNames:
            return

        # Create placeholders for each arg
        self.args = [{}] * len(argNames)

        # These are the ones I care about for now. If there are others later, we can add them.
        query_terms = [
            'argNames',
            'argUsernames',
            'argTypes',
            'argTypeNames',
            'argDescs',
            'argExamples'
        ]

        # Populate the list.
        for n, term in enumerate(query_terms):
            self.args[n][term] = x.eval('query commandservice command.%s ? %s' % (term, self.command))


class ReplayMacro(object):
    """Contains everything necessary to store, manage, and save a MODO maco or
    script using Replay. All macro management commands make use of this object class.

    To work around the lack of a gloal namespace in MODO, `ReplayMacro()` objects
    work entirely with class variables and classmethods."""

    _file_path = None
    _commands = []
    _export_formats = ['lxm', 'py', 'json']

    def __init__(self):
        pass

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
        doc = """The list of `ReplayMacroCommand()` objects for the macro, in
        order from first to last."""
        def fget(self):
            return self._commands
        def fset(self, value):
            self._commands = value
        return locals()

    commands = property(**commands())

    def export_formats():
        doc = """The list of `ReplayMacroCommand()` objects for the macro, in
        order from first to last."""
        def fget(self):
            return self._export_formats
        return locals()

    export_formats = property(**export_formats())

    def parse_LXM(self, input_file):
        """Parse an LXM file and store its commands in the `commands` property."""
        
        input_string = input_file.read()
        

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
        for command in self.commands:
            # See http://modo.sdk.thefoundry.co.uk/wiki/Python#lx.command
            pass

    def render_LXM(self):
        """Generates an LXM string for export."""
        pass

    def render_Python(self):
        """Generates a Python string for export."""
        pass

    def render_json(self):
        """Generates a json string for export."""
        pass
