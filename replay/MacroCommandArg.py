# python

import lx
import re
import json
import lumberjack

class MacroCommandArg(lumberjack.TreeNode):
    """Contains everything pertaining to a single command argument in the macro.
    Each `MacroCommand` object will create one `MacroCommandArg` child for each
    argument.

    An `arg_name` is required. All other argument metadata can be added using
    the various `arg*` properties, or added as optional kwargs during init."""

    def __init__(self, arg_name, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        self._base_command = base_command
        self._arg_name = arg_name

        # Create default command value object and set formatting
        self.values['command'] = lumberjack.TreeValue()
        self.values['command'].input_region = 'MacroCommandArg'

        # Create default enable value object and set formatting
        self.values['enable'] = lumberjack.TreeValue()
        self.values['enable'].display_value = ''

        # Create default name value object
        self.values['name'] = lumberjack.TreeValue()
        self.values['name'].input_region = 'MacroCommandArg'

        # If a command string (it's actually a list of strings) has been passed in, parse it:
        if bool(kwargs.get('arg_string')) and \
            all(isinstance(elem, basestring) for elem in kwargs.get('arg_string')):

            self.parse_string(kwargs.get('arg_string'))

        properties = [
            'value',
            'argName',
            'argUsername',
            'argType',
            'argTypeName',
            'argDesc',
            'argExample'
        ]

        for prop in properties:
            if kwargs.get(prop):
                setattr(self, prop, kwargs.get(prop))
            else:
                setattr(self, prop, None)

    def value():
        doc = "The value property."
        def fget(self):
            return self._value
        return locals()

    value = property(**value())

    def argName():
        doc = "The argName property."
        def fget(self):
            return self._argName
        return locals()

    argName = property(**argName())

    def argUsername():
        doc = "The argUsername property."
        def fget(self):
            return self._argUsername
        def fset(self, value):
            self._argUsername = value
        return locals()

    argUsername = property(**argUsername())

    def argType():
        doc = "The argType property."
        def fget(self):
            return self._argType
        def fset(self, value):
            self._argType = value
        return locals()

    argType = property(**argType())

    def argTypeName():
        doc = "The argTypeName property."
        def fget(self):
            return self._argTypeName
        def fset(self, value):
            self._argTypeName = value
        return locals()

    argTypeName = property(**argTypeName())

    def argDesc():
        doc = "The argDesc property."
        def fget(self):
            return self._argDesc
        def fset(self, value):
            self._argDesc = value
        return locals()

    argDesc = property(**argDesc())

    def argExample():
        doc = "The argExample property."
        def fget(self):
            return self._argExample
        def fset(self, value):
            self._argExample = value
        return locals()

    argExample = property(**argExample())

    def parse_string(self, command_string):
        """Parse a single MODO argument string into its constituent parts and stores
        it for display in the treeview."""

        # Get the argument value and, if given, its name:
        full_argument = re.search(r'(\S+):(\S+)', arg)

        if full_argument:

            arg_name = full_argument.group(1)

            # Check if the name of the argument is correct:
            if arg_name in [self.args[i]['argNames'] for i in range(len(args))]:
                arg_number = [self.args[i]['argNames'] for i in range(len(args))].index(arg_name)
            else:
                raise Exception("Wrong argument name.")

            arg_value = full_argument.group(2)

        else:

            arg_value = arg

        # Clean the argument value of "", '' and {} wraps:
        if arg_value[0] == '"' or arg_value[0] == "'" or arg_value[0] == '{':
            arg_value = arg_value[1:-1]

        # Set the value of the argument:
        self._args[arg_number]['argValues'] = arg_value
