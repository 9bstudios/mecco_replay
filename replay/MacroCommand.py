# python

import lx
import re
import lumberjack

class MacroCommand(lumberjack.TreeNode):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts. Note that if the `command`
    property is `None`, the `comment_before` property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)"""

    _args = {}
    _suppress = False
    _whitespace_before = None
    _comment_before = None
    _prefix = None
    _replay_meta = {}

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # Create default command value object and set formatting
        self.values['command'] = lumberjack.TreeValue()
        # 4113 is a special gray color for grayed out text in MODO
        self.values['command'].color.special = 4113

        # Create default enable value object and set formatting
        self.values['enable'] = lumberjack.TreeValue()
        self.values['enable'].icon_resource = 'MIMG_CHECKMARK'
        self.values['enable'].display_value = ''

        # Create default name value object
        self.values['name'] = lumberjack.TreeValue()

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

        # Get the argument information for this command:
        self.retreive_args()

        # Parse the arguments for this command:
        self.parse_args(command_string[-1][len(full_command.group(0)):])

    def parse_args(self, args_string):

        # Get all the arguments:
        args = re.findall(r'(\S+)', args_string)

        # Process all the arguments:
        for arg_number, arg in enumerate(args):

            # Get the argument value and, if given, its name:
            full_argument = re.search(r'(\S+):(\S+)', arg)

            if full_argument:

                arg_name = full_argument.group(1)

                # Check if the name of the argument is correct:
                if arg_name in [self.args[i]['argNames'] for i in range(len(args))]:
                    arg_number = [self.args[i]['argNames'] for i in range(len(args))].index(arg_name)
                else:
                    raise NameError('Wrong argument')

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
