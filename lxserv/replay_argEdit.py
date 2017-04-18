# python

import math
import lx, lxifc, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class ArgEditClass(replay.commander.CommanderClass):
    """Editor for command argument values. Accepts an argName and a value query.
    Designed specifically for use with `replay.argEditFCL`."""
    
    def asString(self):
        return False

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
                'values_list_type': self.arg_values_list_type,
                'values_list': self.arg_values_list,
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
        
    def selected_args(self):
        for node in replay.Macro().selected_commands:
            for arg in node.args:
                yield arg
                
        for arg in replay.Macro().selected_args:        
            yield arg

    def args_by_argName(self, argName):
        """Returns a list of argument nodes in the current selection with a given
        `argName` property. Probably not as fast as it should be."""
        arg_nodes = set()
        for arg in self.selected_args():
            if arg.argName == argName:
                arg_nodes.add(arg)
        return arg_nodes

    def commands_by_argName(self, argName):
        """Returns a list of argument nodes in the current selection with a given
        `argName` property. Probably not as fast as it should be."""
        commands = list()
        for arg in self.selected_args():
            if arg.argName == argName:
                commands.append((arg.parent, arg.index))
        return commands

    def commander_execute(self, msg, flags):
        """Fires whenever the value is updated in the form. Stores changes in the
        proper place."""
        try:
            argName = self.commander_args()['argName']
            asString = self.asString()
            argValue = self.commander_args()['value']
            
            paths = list()

            for command, argIndex in self.commands_by_argName(argName):
                arg = command.args[argIndex]
                paths.append(arg.path)
                
            argEdit = UndoArgEdit(asString, argValue, paths)
                
            undo_svc = lx.service.Undo()
            argEdit.undo_Forward()
            undo_svc.Record(argEdit)
                
        except Exception as e:
            pass

    def arg_values_list(self):
        datatype, hints, default = self.arg_info(1)
        if hints is None:
            return None
            
        names = list()
        indices = set()
        for idx, name in hints:
            if idx not in indices:
                indices.add(idx)
                names.append(name)

        return names

    def arg_values_list_type(self):
        datatype, hints, default = self.arg_info(1)
        if hints is None:
            return None
        return 'popup'

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

        datatype, hints, default = self.arg_info(1)

        argValues = set()
        for arg in self.args_by_argName(argName):
            argValues.add((arg.value))

        # If there are no values to return, don't bother.
        if not argValues:
            return lx.result.OK

        values_list = list(argValues)

        # RETURN VALUES
        # -------------

        # Need to add the proper datatype based on result from commander_query
        for value in values_list:
            # Sometimes we get passed empty values. Ignore those.
            if value is None:
                value = default

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
                    raise Exception(message("MECCO_REPLAY", "INVALID_STRING"), value, type(value), datatype)

            # Text Value Hints
            elif (datatype == lx.symbol.sTYPE_INTEGER) and hints:
                for idx, name in hints:
                    if name == value:
                        va.AddInt(idx)

            # Booleans
            elif datatype == lx.symbol.sTYPE_BOOLEAN:
                va.AddInt(1 if value.lower() in ['true', 'on', 'yes'] else 0)

            # Integers
            elif datatype in [
                    lx.symbol.sTYPE_INTEGER,
                    lx.symbol.sTYPE_BOOLEAN
                    ]:
                va.AddInt(int(value if value else 0))

            # Floats
            elif datatype in [
                    lx.symbol.sTYPE_ACCELERATION,
                    lx.symbol.sTYPE_AXIS,
                    lx.symbol.sTYPE_COLOR1,
                    lx.symbol.sTYPE_FLOAT,
                    lx.symbol.sTYPE_FORCE,
                    lx.symbol.sTYPE_LIGHT,
                    lx.symbol.sTYPE_DISTANCE,
                    lx.symbol.sTYPE_MASS,
                    lx.symbol.sTYPE_PERCENT,
                    lx.symbol.sTYPE_SPEED,
                    lx.symbol.sTYPE_TIME,
                    lx.symbol.sTYPE_UVCOORD
                    ]:
                va.AddFloat(float(value))

            # Angles need to be converted to radians
            elif datatype in [lx.symbol.sTYPE_ANGLE]:
                va.AddFloat(math.radians(float(value)))

            # Vectors (i.e. strings that need parsing)
            elif datatype in [
                    lx.symbol.sTYPE_ANGLE3,
                    lx.symbol.sTYPE_COLOR,
                    lx.symbol.sTYPE_DISTANCE3,
                    lx.symbol.sTYPE_FLOAT3,
                    lx.symbol.sTYPE_PERCENT3,
                    '&item'
                    ]:
                emptyValue = va.AddEmptyValue()
                emptyValue.SetString(str(value))

            # If the datatype isn't handled explicitly above, we try adding it
            # to a generic value object. Failing that, barf.
            else:
                try:
                    va.AddValue(value)
                except:
                    raise Exception(message("MECCO_REPLAY", "QUERY_DATATYPE_DETECT_ERROR"))

        return lx.result.OK

    def argLabel(self):
        """Displays the proper label for each argument, rather than a generic one."""

        return self.commander_args()['argName']

    def basic_ArgType(self, argIndex):
        type, hints, default = self.arg_info(argIndex)
        return type

    def arg_info(self, argIndex):
        """Returns sTYPE_INTEGER, sTYPE_FLOAT, or sTYPE_STRING depending on the
        datatype stored in the `MacroCommandArg` object. You'd think this would
        be straightforward, but no. This is MODO."""

        argName = self.commander_args()['argName']
        asString = self.asString()

        types = set()

        # Loop over all command args with name argName
        for command, argIndex in self.commands_by_argName(argName):
            arg = command.args[argIndex]
            # Get type coming from meta

            hints = None
            default = None
            argTypeName = None

            if asString or command.markedAsString(argIndex):
                argTypeName = lx.symbol.sTYPE_STRING
                default = command.args[argIndex].value
                hints = None
            else:
                attrs = command.attributes()
                argTypeName = attrs.arg(argIndex).type_name(lx.symbol.sTYPE_STRING)
                default = attrs.arg(argIndex).value_as_string(command.args[argIndex].value)
                hints = attrs.arg(argIndex).hints(None)

            if argTypeName:
                types.add((argTypeName, None if hints is None else tuple(hints), default))

            # If we have more than one type no need to continue. Return 'string'
            if len(types) > 1:
                break;

        if len(types) == 1:
            # If all argument types are identical return it
            arg_info = list(types)[0]
            # Nasty bug: if we edit a color, we must reset the color
            # else crash.
            if arg_info[0] == lx.symbol.sTYPE_COLOR:
                replay.Macro().reset_color_on_select = True

            return arg_info
        else:
            # If args doesn't have type or have many use string
            return (lx.symbol.sTYPE_STRING, None, "")

    def basic_Enable(self, msg):
        return bool(replay.Macro().selected_descendants)

class ArgEditAsStringClass(ArgEditClass):

    def asString(self):
        return True
        
class UndoArgEdit(lxifc.Undo):
    def __init__(self, asString, argValue, paths):
        self.m_asString = asString
        self.m_argValue = argValue
        self.m_paths = paths
        self.m_storedValues = list()

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_VALUE)
        
    def store_in_arg_value(self, command, argIndex, argValue):
        attrs = command.attributes()
        argTypeName = attrs.arg(argIndex).type_name()
        if argTypeName == lx.symbol.sTYPE_INTEGER:
            hints = attrs.arg(argIndex).hints()
            for idx, name in hints:
                if idx == int(argValue):
                    return name

        return argValue

    def undo_Forward(self):
        macro = replay.Macro()
        
        del self.m_storedValues[:]

        for path in self.m_paths:
            arg = macro.node_for_path(path)
            command = arg.parent
            if self.m_asString:
                self.m_storedValues.append((arg.value, command.markedAsString(path[-1])))
                
                arg.value = self.m_argValue
                command.markArgumentAsString(path[-1])
            else:
                self.m_storedValues.append(arg.value)
                arg.value = self.store_in_arg_value(command, path[-1], self.m_argValue)

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()

        for idx in range(len(self.m_paths)):
            path = self.m_paths[idx]
            arg = macro.node_for_path(path)
            command = arg.parent
            if self.m_asString:
                val, asString = self.m_storedValues[idx]
                arg.value = val
                command.markArgumentAsString(path[-1], asString)
            else:
                val = self.m_storedValues[idx]
                arg.value = val

        self.finalize_command(macro)

lx.bless(ArgEditClass, 'replay.argEdit')
lx.bless(ArgEditAsStringClass, 'replay.argEditAsString')
