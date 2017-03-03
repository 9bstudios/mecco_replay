# python

import lx

import re

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
    _replay_meta = {}

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
                'argValue': 'Value of the argument.'
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

    def replay_meta():
        doc = """A dictionary of metadata values for use in the GUI editor. These are stored
        as specially-formatted comments within the code itself. These could include things like
        row color.

        e.g. {'row_color': 'red'}

        Renders as:
        # replay_meta row_color: 'red'"""
        def fget(self):
            return self._replay_meta
        def fset(self, value):
            self._replay_meta = value
        return locals()

    replay_meta = property(**replay_meta())

    def parse_string(self, command_string):
        """Parse a normal MODO command string into its constituent parts, and
        stores those in the `command` and `args` properties for the object."""

        # Get the prefix and the command:
        full_command = re.search(r'([!?+]*)(\S+)', command_string)

        # Get the prefix, if any:
        if full_command.group(1): self.prefix = full_command.group(1)

        # Get the command:
        self.command = full_command.group(2)

        # Get the argument information for this command:
        self.retreive_args()

        # Parse the arguments for this command:
        self.parse_args(command_string[len(full_command.group(0)):])

    def parse_args(self, args_string):

        # Get all the arguments:
        args = re.findall(r'(\S+)', args_string)

        # TODO: What if an invalid argument is passed in? Error handling?
        # Process all the arguments:
        for arg_number, arg in enumerate(args):

            # Check if the name of the argument has been given:
            full_argument = re.search(r'(\S+):(\S+)', arg)
            if full_argument:
                arg_name = full_argument.group(1)
                arg_number = [self.args[i]['argNames'] for i in range(len(args))].index(arg_name)
                arg_value = full_argument.group(2)
            else:
				arg_value = arg

            # Clean the argument value of "", '' and {} wraps:
            if arg_value[0] == '"' or arg_value[0] == "'" or arg_value[0] == '{':
				arg_value = arg_value[1:-1]

            # Set the value of the argument:
            self._args[arg_number]['argValues'] = arg_value

    def command_meta(self):
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
                'argValue': 'Value of the argument.'
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
        self._args = []

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
        for n in range(len(argNames)):
            arg_dict = {}
            for term in query_terms:
                arg_dict[term] = lx.eval('query commandservice command.%s ? %s' % (term, self.command))[n]
            arg_dict['argValues'] = None
            self._args.append(arg_dict)

    def render_LXM(self):
        """Construct MODO command string from stored internal parts."""

        result = '{prefix}{command}'.format(prefix=(self.prefix if self.prefix is not None else ""), command=self.command)

        def wrap_quote(value):
            if re.search(r"\s", value):
                return "\"{0}\"".format(value)
            else:
                return value

        for arg_dict in self.args:
            if arg_dict['argValues'] is not None:
                result += " {name}:{value}".format(name=arg_dict['argNames'], value=wrap_quote(arg_dict['argValues']))
        return result

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

    def is_empty():
        doc = """Return true if there are no recorded commands."""
        def fget(self):
            return len(self.commands) == 0
        return locals()

    is_empty = property(**is_empty())

    @classmethod
    def parse_LXM(cls, input_path):
        """Parse an LXM file and store its commands in the `commands` property."""

        # Open the .lxm input file
        input_file = open(input_path, 'r')

        # Save input path
        cls.file_path = input_path

        # Loop over the lines to get all the command strings:
        for input_line in input_file:
            if not input_line: continue

            # TODO: Ultimately we need to attach comments to whichever command
            # follows them using the `comment_before` property.
            # Skip comments:
            if input_line[0] == "#": continue

            # Parse the command and store it in the commands list:
            cls._commands.append(ReplayMacroCommand(input_line))

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
