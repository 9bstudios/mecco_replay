# python

# Joe Angell [12:23 PM]
# - Flag the variable datatype arguments with VARIABLE_DATATYPE
# - Flag any arguments that need to be set to resolve the variable datatype with REQFORVARIABLE.  For example, item.channel needs to know which channel its targeting before it can figure out the datatype for the "value" argument
# - Implement ArgSetDatatype() to return the datatype.
#
# In your case, I expect the REQFORVARIABLE argument to be called "argument", and
# represents a specific argument on the command, with the command itself being the
# one selected in the tree (rather than providing it as yet another argument).
# The VARIABLE_DATATYPE argument would be "value", and would be queriable.

import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Inserts a comment-only command object into the `Macro().commands` list."""

    def commander_arguments(self):
        return [
            {
                'name': 'argName',
                'datatype': 'string',
                'flags': ['reqforvariable']
            }, {
                'name': 'argument',
                'label': self.argLabel,
                'datatype': 'string', # required, but ignored. Could be anything.
                'flags': ['variable', 'query']
            }
        ]

    def commander_notifiers(self):
        return [("replay.notifier", "")]

    def commander_execute(self, msg, flags):
        argName = self.commander_arg_value(0)
        argValue = self.commander_argStrings['value']
        nodes = replay.Macro().selected_children

        for node in nodes:
            for arg in node.args:
                if arg.argName == argName:
                    arg.value = argValue

        replay.Macro().refresh_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def commander_query(self, argIndex):
        argName = self.commander_arg_value(0)
        nodes = replay.Macro().selected_children

        argValues = set()
        for node in nodes:
            for arg in node.args:
                if arg.argName == argName:
                    argValues.add(arg.value)

        if not argValues:
            return None

        if len(argValues) == 1:
            return list(argValues)[0]

        else:
            return list(argValues)

    def argLabel(self):
        return self.commander_arg_value(0)

    def basic_ArgType(self, argIndex):
        argName = self.commander_arg_value(0)
        nodes = replay.Macro().selected_children

        argTypes = set()
        for node in nodes:
            for arg in node.args:
                if arg.argName == argName:
                    argTypes.add(arg.argTypeName)

        if not argTypes:
            return None

        if len(argTypes) > 1:
            # Oops, there's more than one datatype in the selection.
            # String is our fallback.
            return lx.symbol.sTYPE_STRING

        return list(argTypes)[0]

    def basic_Enable(self, msg):
        return bool(replay.Macro().selected_children)

lx.bless(CommandClass, 'replay.argEdit')
