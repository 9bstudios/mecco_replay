# python

import lx
import re
import lumberjack

class MacroCommandArg(lumberjack.TreeNode):
    """Contains everything pertaining to a single command argument in the macro.
    Each `MacroCommand` object will create one `MacroCommandArg` child for each
    argument."""

    def __init__(self, parent, arg_index, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # We have to manually pass these in from the parent because the `parent`
        # parameter won't be operational until the object has finished `__init__()`.
        self._parent = parent
        self._arg_index = arg_index

        # Argument metadata placeholders
        self._argUsername = None
        self._argType = None
        self._argTypeName = None
        self._argDesc = None
        self._argExample = None

        # `command` field displays the actual argument value
        self.values['command'] = lumberjack.TreeValue()
        self.values['command'].input_region = 'MacroCommandArg'
        self.values['command'].value = None

        # `enable` field is empty for arguments
        self.values['enable'] = lumberjack.TreeValue()
        self.values['enable'].display_value = ''

        # `prefix` field is empty for arguments
        self.values['prefix'] = lumberjack.TreeValue()
        self.values['prefix'].display_value = ''

        # `name` field contains the argument name as a `value`,
        # and the argument's username (nice name) as a `display_value`
        self.values['name'] = lumberjack.TreeValue()
        self.values['name'].input_region = 'MacroCommandArg'
        self.values['name'].color.set_with_name('gray')

        # Query argument metadata
        self.retreive_arg_meta()

        # If a command string (it's actually a list of strings) has been passed in, parse it:
        if bool(kwargs.get('arg_string')) and \
            all(isinstance(elem, basestring) for elem in kwargs.get('arg_string')):

            self.parse_string(kwargs.get('arg_string'))

    def value():
        doc = "The value property is really a proxy for the `command` cell value."
        def fget(self):
            return self.values['command'].value
        def fset(self, value):
            self.values['command'].value = value
            for column, value in self.values.iteritems():
                if value.value is not None:
                    value.color.set_with_name('default')
        return locals()

    value = property(**value())

    def argName():
        doc = "The argName property is really a proxy for the `name` cell value."
        def fget(self):
            return self.values['name'].value
        def fset(self, value):
            self.values['name'].value = value
        return locals()

    argName = property(**argName())

    def argUsername():
        doc = "The argUsername property is really a proxy for the `name` cell `display_value`."
        def fget(self):
            return self._argUsername
        def fset(self, value):
            # Since the `display_value` getter will return color and font markup,
            # we need to store the username in both the `display_value` for the `name`
            # column, and also in an internal `_argUsername` variable.
            self._argUsername = value
            self.values['name'].display_value = value
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

    def retreive_arg_meta(self):
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

        base_command = self.parent.command
        arg_index = self._arg_index

        if not base_command:
            raise Exception("Invalid parent command.")
            return

        # Names of the arguments for the current command.
        if not lx.evalN("query commandservice command.argNames ? {%s}" % base_command):
            raise Exception("Parent command has no args. Why do I exist? (Big Questions In Life)")
            return

        # Unlike other metadata, we store these two directly inside the value objects for the columns.
        values_list = lx.evalN("query commandservice command.argNames ? {%s}" % base_command)
        self.argName = values_list[arg_index]

        values_list = lx.evalN("query commandservice command.argUsernames ? {%s}" % base_command)
        self.argUsername = values_list[arg_index]

        # These are the ones I care about for now. If there are others later, we can add them.
        query_terms = [
            'argTypes',
            'argTypeNames',
            'argDescs',
            'argExamples'
        ]

        # The list of query_terms is arbitrary. I'm just grabbing everything I think is important.
        for term in query_terms:
            # Remove the last character from the term to make it singular (argNames becomes argName)
            property_name = term[:-1]
            # Get the full list of values (for all args)
            # Note the use of `lx.evalN` as opposed to the normal `lx.eval`. We need to be certain
            # that we always receive a list in response, even if the list length is 1.
            values_list = lx.evalN('query commandservice command.%s ? {%s}' % (term, base_command))
            # Run the query.
            setattr(self, property_name, values_list[arg_index])

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
