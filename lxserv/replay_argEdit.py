# python

import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Editor for command argument values. Accepts an argName and a value query.
    Designed specifically for use with `replay.argEditFCL`."""

    def commander_arguments(self):
        return [
            {
                'name': 'argName',
                'datatype': 'string',
                'flags': ['reqforvariable']
            }, {
                'name': 'value',
                'label': self.argLabel,
                'datatype': 'string', # required, but ignored. Could be anything.
                'flags': ['variable', 'query']
            }
        ]

    def commander_notifiers(self):
        # We need to update our values whenever the replay notifier fires for
        # selection state changes and tree updates.
        return [("replay.notifier", "")]

    def args_by_argName(self, argName):
        """Returns a list of argument nodes in the current selection with a given
        `argName` property. Probably not as fast as it should be."""
        arg_nodes = set()
        for node in replay.Macro().selected_commands:
            for arg in node.args:
                if arg.argName == argName:
                    arg_nodes.add(arg)
        return arg_nodes

    def can_float(self, argName):
        """Returns `True` if all argument is of unspecified type and values can
        be converted to `Float`.

        Some command arguments in MODO have undefined (generic) `argType` parameters.
        In these cases, a string is the fail-safe. But many of these generic values
        are actually numeric, and the string editor in MODO is not ideal for editing
        numbers. Workaround: if the value has an `argType` of 0 and Python can
        successfully convert it to a `float` value, do it."""
        for arg in self.args_by_argName(argName):
            if arg.argType != 0:
                return False
            try:
                float(arg.value)
            except:
                return False
        return True

    def commander_execute(self, msg, flags):
        """Fires whenever the value is updated in the form. Stores changes in the
        proper place."""
        argName = self.commander_args()['argName']
        argValue = self.commander_args()['value']

        for arg in self.args_by_argName(argName):
            arg.value = argValue

        # Notify the TreeView to update itself.
        replay.Macro().refresh_view()

        # TODO For some reason this breaks minisliders.
        # notifier = replay.Notifier()
        # notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def commander_query(self, argIndex):
        """Fires whenever the value is displayed in the form. Should return the value(s)
        to be displayed in the edit field. If multiple values are provided, MODO will
        display "mixed..." in the edit field for batch editing."""
        argName = self.commander_args()['argName']

        argValues = set()
        for arg in self.args_by_argName(argName):
            argValues.add(arg.value)

        if not argValues:
            return None

        if self.can_float(argName):
            values_list = [float(v) for v in argValues]
        else:
            values_list = list(argValues)

        return values_list[0] if len(argValues) == 1 else values_list

    def argLabel(self):
        """Displays the proper label for each argument, rather than a generic one."""

        return self.commander_args()['argName']

    def basic_ArgType(self, argIndex):
        """Returns sTYPE_INTEGER, sTYPE_FLOAT, or sTYPE_STRING depending on the
        datatype stored in the `MacroCommandArg` object. You'd think this would
        be straightforward, but no. This is MODO."""

        argName = self.commander_args()['argName']

        # First, figure out if we have exactly one argType to work with. If we have
        # zero or more than one, we have to use a string.
        argTypes = set()
        for arg in self.args_by_argName(argName):
            argTypes.add((arg.argType, arg.argTypeName))

        if not argTypes: return lx.symbol.sTYPE_STRING
        if len(argTypes) > 1: return lx.symbol.sTYPE_STRING

        # Now that we've established that we only have one argType, act like it.
        argType = list(argTypes)[0]

        # If an `argTypeName` is defined in the arg object, use it.
        argTypeName = argType[1]
        if argTypeName:
            return argTypeName

        # In many cases, however, we won't have a proper argTypeName :(
        else:

            # If we don't have an argTypeName, check if it can be a float.
            if self.can_float(argName):
                return lx.symbol.sTYPE_FLOAT

            # If not, fall back on the `arg.argType` property:
            #   0: generic
            #   1: integer
            #   2: float
            #   3: string

            lookup = [
                lx.symbol.sTYPE_STRING, # generic object
                lx.symbol.sTYPE_INTEGER,
                lx.symbol.sTYPE_FLOAT,
                lx.symbol.sTYPE_STRING
            ]
            return lookup[argType[0]]

    def basic_Enable(self, msg):
        """If nothing is selected, gray out the UI. (In practice this should never
        happen since we're using an FCL to generate these based on selection.)"""

        return bool(replay.Macro().selected_descendants)

lx.bless(CommandClass, 'replay.argEdit')
