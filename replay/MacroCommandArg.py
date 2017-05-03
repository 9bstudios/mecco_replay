# python
'''
The MacroCommandArg module contains the MacroCommandArg class, which is serves
as single API to all aspects of a command within the macro
'''
import lx
import re
import lumberjack

class MacroCommandArg(lumberjack.TreeNode):
    '''
    Contains everything pertaining to a single command argument in the macro.
    Each MacroCommand object will create one MacroCommandArg child for each
    argument.

    Args:
        parent (MacroCommand): parent MacroCommand instance
        arg_index (int): argument position within command
        \**kwargs: varkwargs

    Returns:
        MacroCommandArg: command argument
    '''
    def __init__(self, parent, arg_index, **kwargs):
        super(self.__class__, self).__init__(state=lumberjack.fTREE_VIEW_ITEM_ATTR, **kwargs)

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
        self.columns['command'] = lumberjack.TreeValue()
        self.columns['command'].input_region = 'MacroCommandArg'
        self.columns['command'].value = None

        # `enable` field is empty for arguments
        self.columns['enable'] = lumberjack.TreeValue()
        self.columns['enable'].input_region = None
        self.columns['enable'].display_value = ''

        # `prefix` field is empty for arguments
        self.columns['prefix'] = lumberjack.TreeValue()
        self.columns['prefix'].input_region = None
        self.columns['prefix'].display_value = ''

        # `name` field contains the argument name as a `value`,
        # and the argument's username (nice name) as a `display_value`
        self.columns['name'] = lumberjack.TreeValue()
        self.columns['name'].input_region = 'MacroCommandArg'
        self.columns['name'].color.special_by_name('gray')

        # Query argument metadata
        self.retreive_arg_meta()

        # If a command string (it's actually a list of strings) has been passed in, parse it:
        if bool(kwargs.get('arg_string')) and \
            all(isinstance(elem, basestring) for elem in kwargs.get('arg_string')):

            self.parse_string(kwargs.get('arg_string'))

    def can_change_suppress(self):
        '''
        Whether or not the supression of this argument can be changed

        Args:
            None

        Returns:
            bool: False
        .. todo:
            - what is the point of having functions that have no logic and are
              not properties?
              def __init__(self): self.can_change_suppress = False       Done.
        '''
        return False

    def can_change_color(self):
        '''
        Whether or not the color of this argument's GUI widget can be changed

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def can_add_command(self):
        '''
        Whether or not a command can be added to this argument

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def can_add_to_block(self):
        '''
        Whether or not this argument can be added to a block

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def can_copy(self):
        '''
        Whether or not this argument can be copied

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def can_insert_after(self):
        '''
        Whether or not this argument can be inserted after another

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def can_delete(self):
        '''
        Whether or not this argument can be deleted

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def can_change_name(self):
        '''
        Whether or not this argument's name can be changed

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def value():
        doc = '''
        dict: local context
        The value property is really a proxy for the command cell value.
        If you set it to a string, it will try to convert it to to the
        appropriate datatype based on argType.
        '''
        def fget(self):
            return self.columns['command'].value
        def fset(self, value):
            self.columns['command'].value = self.convert_string_to_value(value)

            if self.columns['command'].value is None:
                self.columns['name'].color.special_by_name('gray')
            else:
                self.columns['name'].color.special_by_name('default')
        return locals()

    value = property(**value())

    def display_prefix():
        '''dict: locdoc = al context
        Gets and sets the display of the command prefix for this argument
        '''
        def fget(self):
            return self.columns['prefix'].display_value
        def fset(self, value):
            self.columns['prefix'].display_value = value
        return locals()

    display_prefix = property(**display_prefix())

    def asString():
        doc = '''
        dict: local context
        Gets and sets whether or not the argument value is displayed as a string
        '''
        def fget(self):
            return (self.columns['prefix'].display_value == "%")
        def fset(self, value):
            self.columns['prefix'].display_value = "%" if value else ""
        return locals()

    asString = property(**asString())

    def argName():
        doc = '''
        dict: local context
        Gets and sets the name for this argument's name cell value
        '''
        def fget(self):
            return self.columns['name'].value
        def fset(self, value):
            self.columns['name'].value = value
        return locals()

    argName = property(**argName())

    def argUsername():
        doc = '''
        dict: local context
        Gets and sets the display_value cell, which controls display of the user name
        '''
        def fget(self):
            return self._argUsername
        def fset(self, value):
            # Since the `display_value` getter will return color and font markup,
            # we need to store the username in both the `display_value` for the `name`
            # column, and also in an internal `_argUsername` variable.
            self._argUsername = value
            self.columns['name'].display_value = value
        return locals()

    argUsername = property(**argUsername())

    def argType():
        doc = '''
        dict: local context
        Gets and sets the argType property
        '''
        def fget(self):
            return self._argType
        def fset(self, value):
            self._argType = value
        return locals()

    argType = property(**argType())

    def argTypeName():
        doc = '''
        dict: local context
        Gets and sets the argTypeName property
        '''
        def fget(self):
            return self._argTypeName
        def fset(self, value):
            self._argTypeName = value
        return locals()

    argTypeName = property(**argTypeName())

    def argDesc():
        doc = '''
        dict: local context
        Gets and sets the argDesc property
        '''
        def fget(self):
            return self._argDesc
        def fset(self, value):
            self._argDesc = value
        return locals()

    argDesc = property(**argDesc())

    def argExample():
        doc = '''
        dict: local context
        Gets and sets the argExample property
        '''
        def fget(self):
            return self._argExample
        def fset(self, value):
            self._argExample = value
        return locals()

    argExample = property(**argExample())

    def canEval(self):
        '''
        Whether or the argument can be evaluated

        Args:
            None

        Returns:
            bool: False
        '''
        return False

    def retreive_arg_meta(self):
        '''
        Retrieve a list of arguments and datatypes from modo's commandservice.
        See http://sdk.luxology.com/wiki/Commandservice#command.argNames

        Args:
            None

        Returns:
            None

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
            ]
        '''
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
        self.argUsername = "%s \x03(c:4113)(%s)" % (values_list[arg_index], self.argName)

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
        '''
        Parse a single modo argument string into its constituent parts and stores
        it for display in the treeview.

        Args:
            command_string (str): modo argument string

        Returns:
            None

        Raises:
            Exception

        .. todo:
            - raising a generic exception does not help much with debugging via
              traceback.  if the exception is related to a bad arg name then
              raise a ValueError.
        '''
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


    def convert_string_to_value(self, arg_value):
        '''
        Convenience method for converting strings to argument values

        Args:
            arg_value (object): argument value

        Returns:
            str or None
        '''
        if arg_value is None:
            return None

        return str(arg_value)
