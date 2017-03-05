# python

import lx
import re
import json
import lumberjack
from MacroCommandArg import MacroCommandArg

class MacroCommand(lumberjack.TreeNode):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts. Note that if the `command`
    property is `None`, the `comment_before` property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)"""

    _args = {}
    _suppress = False
    _whitespace_before = None
    _comment_before = None
    _replay_meta = {}

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # Create default command value object and set formatting
        self.values['command'] = lumberjack.TreeValue()
        # 4113 is a special gray color for grayed out text in MODO
        self.values['command'].color.special = 4113
        self.values['command'].input_region = 'MacroCommandCommand'

        # Create default enable value object and set formatting
        self.values['enable'] = lumberjack.TreeValue()
        self.values['enable'].icon_resource = 'MIMG_CHECKMARK'
        self.values['enable'].display_value = ''
        self.values['enable'].input_region = 'MacroCommandEnable'

        # Create default dialogs value object and set formatting
        self.values['prefix'] = lumberjack.TreeValue()
        self.values['prefix'].input_region = 'MacroCommandPrefix'

        # Create default name value object
        self.values['name'] = lumberjack.TreeValue()
        self.values['name'].input_region = 'MacroCommandName'

        # If a command string (it's actually a list of strings) has been passed in, parse it:
        if bool(kwargs.get('command_string')) and \
            all(isinstance(elem, basestring) for elem in kwargs.get('command_string')):

            self.parse_string(kwargs.get('command_string'))

    def command():
        doc = "The base MODO command, e.g. `item.name`."
        def fget(self):
            command = self.values.get('command')
            if command:
                return command.value
            else:
                return None
        def fset(self, value):
            self.values['command'].value = value
            self.retreive_args()
            self.values['name'].value = self.command_meta()['username']
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
            return self.values['prefix'].value
        def fset(self, value):
            self.values['prefix'].value = value
        return locals()

    prefix = property(**prefix())

    def args():
        doc = """The `MacroCommand` node's arguments, which should all be
        of class `MacroCommandArg`."""
        def fget(self):
            return self.children
        def fset(self, value):
            self.children = value
        return locals()

    args = property(**args())

    def suppress():
        doc = "Boolean. Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            return self._suppress
        def fset(self, is_suppressed):
            # Set the internal _suppress value. This value is used when we do things
            # like render to LXM, etc.
            self._suppress = is_suppressed

            # Set the `enable` column display. This is purely visual.
            # First, set display_value to a blank string so that we don't show any text.
            self.values['enable'].display_value = ''

            if not is_suppressed:
                # If not suppressed, display a checkmark and store True
                self.values['enable'].value = True
                self.values['enable'].icon_resource = 'MIMG_CHECKMARK'
            elif is_suppressed:
                # If it is suppressed, display nothing and store False
                self.values['enable'].value = False
                self.values['enable'].icon_resource = None

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

        # Get the comments before the command, if any:
        if len(command_string) > 1:
            self.comment_before = command_string[:-1]

        # Get the prefix and the command:
        full_command = re.search(r'([!?+]*)(\S+)', command_string[-1])

        # Get the prefix, if any:
        if full_command.group(1): self.prefix = full_command.group(1)

        # Get the command:
        self.command = full_command.group(2)

        # Parse the arguments for this command:
        self.parse_args(command_string[-1][len(full_command.group(0)):])

    def parse_args(self, args_string):
        """Parse a string containing arguments and stores them in 'args'."""

        # Get all the arguments:
        args = re.findall(r'(\S+)', args_string)

        # Process all the arguments:
        for arg_number, arg in enumerate(args):

            # Try to get the name and the value wrapped in string symbols:
            full_argument = re.search(r'(\S+):["\'{](\S+)["\'}]', arg)

            # Try to get the name and the value with no string symbols:
            if not full_argument:
				full_argument = re.search(r'(\S+):(\S+)', arg)

            # If only the argument value wrapped in string symbols was given, don't use full_argument:
            if re.search(r'["\'{](\S+)["\'}]', arg): full_argument = False

            # Process the argument string, either with or without name:
            if full_argument:

                # Get the argument's name:
                arg_name = full_argument.group(1)

                # Check if the name of the argument is correct:
                if arg_name in [self.args[i].argName for i in range(len(args))]:
                    arg_number = [self.args[i].argName for i in range(len(args))].index(arg_name)
                else:
                    raise Exception("Wrong argument name.")

                # Get the argument's value:
                arg_value = full_argument.group(2)

            else:

                # If the name has not been given, then the value is the full string:
                arg_value = arg

            # Clean the argument value of "", '' and {} wraps:
            if arg_value[0] == '"' or arg_value[0] == "'" or arg_value[0] == '{':
                arg_value = arg_value[1:-1]

            # Set the value of the argument:
            self.args[arg_number].value = arg_value

    def retreive_args(self):
        """Retrieve a list of arguments and datatypes from MODO's commandservice.
        See http://sdk.luxology.com/wiki/Commandservice#command.argNames"""

        if not self.command:
            raise Exception("Command string not set.")
            return

        # Names of the arguments for the current command.
        argNames = lx.evalN("query commandservice command.argNames ? {%s}" % self.command)

        # No arguments to add
        if not argNames:
            return

        # Populate the list.
        for n in range(len(argNames)):
            self.args.append(MacroCommandArg(parent=self, arg_index=n))


    def command_meta(self):
        """Returns a dict of metadata for the command from the MODO commandservice,
        as listed here: http://sdk.luxology.com/wiki/Commandservice#command.username."""

        if not self.command:
            raise Exception("Command string not set.")
            return

        query_terms = [
            'category',
            'desc',
            'usage',
            'example',
            'flags',
            'username',
            'buttonName',
            'tooltip',
            'help',
            'icon'
        ]

        meta = {}

        for term in query_terms:
            meta[term] = lx.eval("query commandservice command.%s ? {%s}" % (term, self.command))

        return meta

    def render_LXM(self):
        """Construct MODO command string from stored internal parts."""

        result = '{prefix}{command}'.format(prefix=(self.prefix if self.prefix is not None else ""), command=self.command)

        def wrap_quote(value):
            if re.search(r"\s", value):
                return "\"{0}\"".format(value)
            else:
                return value

        for arg in self.args:
            if arg.value is not None:
                result += " {name}:{value}".format(name=arg.argName, value=wrap_quote(arg.value))
        return result

    def render_Python(self):
        """Construct MODO command string wrapped in lx.eval() from stored internal parts."""

        return "lx.eval({command})".format(command=repr(self.render_LXM().replace("'", "\\'")))

    def render_json(self):
        """Construct MODO command string in json format from stored internal parts."""

        full_cmd = '{prefix}{command}'.format(prefix=(self.prefix if self.prefix is not None else ""), command=self.command)

        return {full_cmd: self.args}

    def run(self):
        """Runs the command."""

        # Build the MODO command string:
        command = self.render_LXM()

        # Run the command:
        lx.eval(command)
