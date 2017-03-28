# python

import lx
import lxifc
import re
import json
import lumberjack
from MacroCommandArg import MacroCommandArg
from CommandAttributes import CommandAttributes


class MacroCommand(lumberjack.TreeNode):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts. Note that if the `command`
    property is `None`, the `comment_before` property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)"""

    _args = {}
    _suppress = False
    _user_comment_before = []

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        self._user_comment_before = []

        # Create default command value object and set formatting
        self.columns['command'] = lumberjack.TreeValue()
        # 4113 is a special gray color for grayed out text in MODO
        self.columns['command'].color.special_by_name('gray')
        self.columns['command'].input_region = 'MacroCommandCommand'

        # Create default enable value object and set formatting
        self.columns['enable'] = lumberjack.TreeValue()
        # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
        self.columns['enable'].display_value = ''
        self.columns['enable'].input_region = 'MacroCommandEnable'
        self.columns['enable'].color.special_by_name('gray')

        # Create default dialogs value object and set formatting
        self.columns['prefix'] = lumberjack.TreeValue()
        self.columns['prefix'].input_region = 'MacroCommandPrefix'

        # Create default name value object
        self.columns['name'] = lumberjack.TreeValue()
        self.columns['name'].input_region = 'MacroCommandCommand'
        # self.columns['name'].icon_resource = 'uiicon_replay.suppress'

        if kwargs.get('suppress') != None:
            self.direct_suppress = kwargs.get('suppress')

        # If a command string (it's actually a list of strings) has been passed in, parse it:
        if bool(kwargs.get('command')):
            self.parse_string(kwargs.get('command'), kwargs.get('comment'), kwargs.get('suppress'))
        elif bool(kwargs.get('command_json')):
            self.parse_json(kwargs.get('command_json'))

        if bool(kwargs.get('ButtonName')):
            self.columns['name'].value = kwargs.get('ButtonName')

    def attributes(self):
        return CommandAttributes(string=self.render_LXM_without_comment())

    def draggable(self):
        return True

    def canEval(self):
        return not self.suppress

    def command():
        doc = "The base MODO command, e.g. `item.name`."
        def fget(self):
            command = self.columns.get('command')
            if command:
                return command.value
            else:
                return None
        def fset(self, value):
            self.columns['command'].value = value
            self.retreive_args()
            self.columns['name'].value = self.command_meta()['username']
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
            return self.columns['prefix'].value
        def fset(self, value):
            self.columns['prefix'].value = value
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

    def can_change_suppress(self):
        if hasattr(self.parent, 'suppress'):
            return not self.parent.suppress
        else:
            return True

    def update_suppress_for_node_and_descendants(self):
        if hasattr(self, 'suppress'):
            if not self.suppress:
                # If not suppressed, display a checkmark and store True
                self.columns['enable'].value = True
                self.columns['enable'].display_value = ''
                # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
                self.columns['name'].color.special_by_name('default')
                self.columns['prefix'].color.special_by_name('default')
            elif self.suppress:
                # If it is suppressed, display nothing and store False
                self.columns['enable'].value = False
                self.columns['enable'].display_value = '#'
                # self.columns['enable'].icon_resource = None
                self.columns['name'].color.special_by_name('gray')
                self.columns['prefix'].color.special_by_name('gray')

        for child in self.children:
            if hasattr(child, 'suppress'):
                child.update_suppress_for_node_and_descendants()

    def direct_suppress():
        doc = "Boolean. True if command suppressed directly not by suppressing block."
        def fget(self):
            return self._suppress

        def fset(self, is_suppressed):
            # Set the internal _suppress value. This value is used when we do things
            # like render to LXM, etc.
            self._suppress = is_suppressed

            # Set the `enable` column display. This is purely visual.
            self.update_suppress_for_node_and_descendants()

        return locals()

    direct_suppress = property(**direct_suppress())

    def suppress():
        doc = "Boolean. Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            if hasattr(self.parent, 'suppress'):
                return self._suppress or self.parent.suppress
            return self._suppress

        return locals()

    suppress = property(**suppress())

    def parse_meta(self, line):
        meta = re.search(r'^\# replay\s+(\S+):(.+)$', line)
        if meta is not None:
            return (meta.group(1), meta.group(2))
        else:
            return None

    def render_meta(self, name, val):
        return "# replay {n}:{v}".format(n=name, v=val)

    def comment_before():
        doc = """String to be added as comment text before the command. Long strings
        will automatically be broken into lines of 80 characters or less. Appropriate
        comment syntax will be rendered at export time. Include only the raw string."""
        def fget(self):
            res = list(self._user_comment_before)
            for key, val in self.meta.iteritems():
                if val != None:
                    res.append(self.render_meta(key, val))
            return res
        def fset(self, value):
            del self._user_comment_before[:]
            for line in value:
                meta = self.parse_meta(line)
                if meta is None:
                    self._user_comment_before.append(line)
                else:
                    (name, val) = meta
                    self.meta[name] = val
        return locals()

    comment_before = property(**comment_before())

    def user_comment_before():
        doc = """String to be added as comment text before the command. Long strings
        will automatically be broken into lines of 80 characters or less. Appropriate
        comment syntax will be rendered at export time. Include only the raw string."""
        def fget(self):
            return self._user_comment_before
        def fset(self, value):
            self._user_comment_before = value
        return locals()

    user_comment_before = property(**user_comment_before())

    def parse_string(self, command, comment, suppress):
        """Parse a normal MODO command string into its constituent parts, and
        stores those in the `command` and `args` properties for the object."""

        # Get the comments before the command, if any:
        if comment is not None:
            self.user_comment_before = comment
        else:
            self.user_comment_before = []

        # Get the prefix and the command:
        full_command = re.search(r'([!?+]*)(\S+)', command)

        if full_command is None:
            raise Exception("Wrong command")

        # Get the suppress flag
        self.direct_suppress = suppress

        # Get the prefix, if any:
        if full_command.group(1): self.prefix = full_command.group(1)

        # Get the command:
        self.command = full_command.group(2)

        # Parse the arguments for this command:
        self.parse_args(command[len(full_command.group(0)):])

    def parse_json(self, command_json):
        """Parse a MODO command in json struct into its constituent parts, and
        stores those in the `command` and `args` properties for the object."""

        command_json = command_json["command"]

        # Retrive command, prefix and comment
        self.command = command_json["name"]
        self.direct_suppress = command_json["suppress"]
        self.prefix = command_json["prefix"]
        self.comment_before = command_json["comment"]
        #return {"command" : {"name" : self.command, "prefix" : self.prefix, "comment" : self.comment_before, "args": args_list}}

        # Retrive args
        json_args = command_json["args"]

        # Assign arg values
        for arg in self.args:
            json_arg = next((x for x in json_args if x['argName'] == arg.argName))
            if json_arg is not None:
                arg.value = None if json_arg['value'] is None else json_arg['value']

    def get_next_arg_name(self, args_string):

        if not args_string: return None, None

        start = re.search(r'\S', args_string)
        if not start:
            args_string = None
            return None, args_string
        if start.group() in ["'", '"', '{']:
            return None, args_string
        start_index = start.start()

        next_space = re.search(r'\s|$', args_string[start_index:])
        if not next_space:
            args_string = None
            return None, args_string
        next_space_index = start_index + next_space.start()

        colon = re.search(r':', args_string[start_index:next_space_index])
        if not colon:
            return None, args_string
        colon_index = start_index + colon.start()

        string_wrapper = re.search(r'["\'{]', args_string[start_index:colon_index])
        if string_wrapper:
            return None, args_string

        result = args_string[start_index:colon_index]
        args_string_left = args_string[colon_index+1:]

        return result, args_string_left

    def get_next_arg_value(self, args_string):

        if not args_string: return None, None

        start = re.search(r'\S', args_string)
        if not start:
            args_string = None
            return None, args_string
        start_index = start.start()

        if start.group() == "'":
            start_index += 1
            finish_index = start_index + re.search(r"'", args_string[start_index:]).start()
        elif start.group() == '"':
            start_index += 1
            finish_index = start_index + re.search(r'"', args_string[start_index:]).start()
        elif start.group() == '{':
            start_index += 1
            finish_index = start_index + re.search(r'}', args_string[start_index:]).start()
        else:
            finish_index = start_index + re.search(r'\s|$', args_string[start_index:]).start()

        result = args_string[start_index:finish_index]
        args_string_left = args_string[finish_index+1:]

        return result, args_string_left

    def parse_args(self, args_string):
        """Parse a string containing arguments and stores them in 'args'."""

        arg_counter = 0

        while args_string and arg_counter < len(self.args):

            # Get the next argument's name (if given) and value:
            arg_name, args_string = self.get_next_arg_name(args_string)
            arg_value, args_string = self.get_next_arg_value(args_string)
            if not arg_value: break

            # Get the argument number:
            if arg_name:

                # Check if the name of the argument is correct:
                if arg_name in [self.args[i].argName for i in range(len(self.args))]:
                    arg_number = [self.args[i].argName for i in range(len(self.args))].index(arg_name)
                else:
                    raise Exception("Wrong argument name.")

            else:

                arg_number = arg_counter

            # Set the value of the argument:
            self.args[arg_number].value = arg_value

            # Increase the argument counter, and check if it's not out of bounds:
            if arg_counter == len(self.args): raise Exception("Error in parsing: too many arguments detected.")
            arg_counter += 1

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
            self.args.append(MacroCommandArg(
                parent=self,
                arg_index=n,
                controller=self._controller
            ))


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
        """Construct MODO command string from stored internal parts. Also adds comments"""
        res = list(self.comment_before)
        if self.direct_suppress:
            res.append("# replay suppress:")

        res.append(("# " if self.direct_suppress else "") + self.render_LXM_without_comment())
        return res

    def render_LXM_without_comment(self):
        """Construct MODO command string from stored internal parts."""

        result = '{prefix}{command}'.format(prefix=(self.prefix if self.prefix is not None else ""), command=self.command)

        def wrap_quote(value):
            if re.search(r"\W", value):
                return "\"{0}\"".format(value)
            else:
                return value

        for arg in self.args:
            if arg.value is not None:
                result += " {name}:{value}".format(name=arg.argName, value=wrap_quote(str(arg.value)))
        return result

    def render_Python(self):
        """Construct MODO command string wrapped in lx.eval() from stored internal parts."""

        res = list(self.comment_before)
        if self.direct_suppress:
            res.append("# replay suppress:")
        res.append(("# " if self.direct_suppress else "") + "lx.eval({command})".format(command=repr(self.render_LXM_without_comment().replace("'", "\\'"))))
        return res

    def render_json(self):
        """Construct MODO command string in json format from stored internal parts."""

        full_cmd = '{prefix}{command}'.format(prefix=(self.prefix if self.prefix is not None else ""), command=self.command)

        args_list = list()
        for arg in self.args:
            arg_dict = dict()
            arg_dict['value'] = arg.value
            arg_dict['argName'] = arg.argName
            arg_dict['argUsername'] = arg.argUsername
            arg_dict['argType'] = arg.argType
            arg_dict['argTypeName'] = arg.argTypeName
            arg_dict['argDesc'] = arg.argDesc
            arg_dict['argExample'] = arg.argExample
            args_list.append(arg_dict)

        return {"command" : {"name" : self.command, "prefix" : self.prefix, "suppress": self.direct_suppress, "comment" : self.comment_before, "args": args_list}}

    def run(self):
        """Runs the command."""

        if self.suppress:
            return

        # Build the MODO command string:
        command = self.render_LXM_without_comment()

        # Run the command:
        lx.eval(command)
