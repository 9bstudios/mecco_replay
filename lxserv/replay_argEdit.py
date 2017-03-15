# python

import lx, modo, replay
from replay import message as message

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

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_UNDO

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
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_VALUE)

    def cmd_Query(self, index, vaQuery):
        """Fires whenever the value is displayed in the form. Should return the value(s)
        to be displayed in the edit field. If multiple values are provided, MODO will
        display "mixed..." in the edit field for batch editing."""

        # Create the ValueArray object
        va = lx.object.ValueArray()
        va.set(vaQuery)

        if index != 1:
            return lx.result.OK

        # GATHER VALUES
        # -------------

        argName = self.commander_args()['argName']

        argValues = set()
        for arg in self.args_by_argName(argName):

            # Try to establish datatype by name
            datatype = arg.argTypeName

            # If not, fall back on the `arg.argType` property:
            if not datatype:
                datatype = [
                    lx.symbol.sTYPE_STRING,     # generic object (as string)
                    lx.symbol.sTYPE_INTEGER,    # integer
                    lx.symbol.sTYPE_FLOAT,      # float
                    lx.symbol.sTYPE_STRING      # string
                ][arg.argType]

            argValues.add((arg.value, datatype))

        # If there are no values to return, don't bother.
        if not argValues:
            return lx.result.OK

        # Some arg values will be stored as strings when in fact they should
        # really be numbers. (Since not all MODO command args specify a datatype.)
        # We assume that if the datatype is undeclared and the string can be
        # converted to a float, we should do it.
        if self.can_float(argName):
            values_list = [(float(v), lx.symbol.sTYPE_FLOAT) for (v, d) in argValues]
        else:
            values_list = list(argValues)

        # RETURN VALUES
        # -------------

        # Need to add the proper datatype based on result from commander_query
        for value, datatype in values_list:

            # Sometimes we get passed empty values. Ignore those.
            if value is None:
                continue

            # Sadly, I am not aware of any way of handling datatypes except
            # by manually testing for them and doing the appropriate action.
            # MODO doesn't make this easy.

            # Strings
            if datatype in [
                    lx.symbol.sTYPE_DATE,
                    lx.symbol.sTYPE_DATETIME,
                    lx.symbol.sTYPE_FILEPATH,
                    lx.symbol.sTYPE_STRING,
                    lx.symbol.sTYPE_VERTMAPNAME
                    ]:
                try:
                    va.AddString(str(value))
                except:
                    raise Exception(message("REPLAY_ARG_EDIT", "ERROR1"), value, type(value), datatype)

            # Integers
            elif datatype in [
                    lx.symbol.sTYPE_INTEGER,
                    lx.symbol.sTYPE_BOOLEAN
                    ]:
                va.AddInt(int(value))

            # Floats
            elif datatype in [
                    lx.symbol.sTYPE_ACCELERATION,
                    lx.symbol.sTYPE_ANGLE,
                    lx.symbol.sTYPE_AXIS,
                    lx.symbol.sTYPE_COLOR1,
                    lx.symbol.sTYPE_FLOAT,
                    lx.symbol.sTYPE_FORCE,
                    lx.symbol.sTYPE_LIGHT,
                    lx.symbol.sTYPE_MASS,
                    lx.symbol.sTYPE_PERCENT,
                    lx.symbol.sTYPE_SPEED,
                    lx.symbol.sTYPE_TIME,
                    lx.symbol.sTYPE_UVCOORD
                    ]:
                va.AddFloat(float(value))

            # Vectors (i.e. strings that need parsing)
            elif datatype in [
                    lx.symbol.sTYPE_ANGLE3,
                    lx.symbol.sTYPE_COLOR,
                    lx.symbol.sTYPE_DISTANCE3,
                    lx.symbol.sTYPE_FLOAT3,
                    lx.symbol.sTYPE_PERCENT3
                    ]:
                emptyValue = va.AddEmptyValue()
                emptyValue.SetString(str(value))

            # If the datatype isn't handled explicitly above, we try adding it
            # to a generic value object. Failing that, barf.
            else:
                try:
                    va.AddValue(value)
                except:
                    raise Exception(message("REPLAY_ARG_EDIT", "ERROR2"))

        return lx.result.OK

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
            if argTypeName == lx.symbol.sTYPE_COLOR:
                replay.Macro().reset_color_on_select = True
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
        return bool(replay.Macro().selected_descendants)

lx.bless(CommandClass, 'replay.argEdit')
