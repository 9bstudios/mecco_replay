import lx, modo, replay, os

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class LineInsertClass(replay.commander.CommanderClass):
    """Insetrs one or many lines after primary node."""

    def commander_arguments(self):
        return [
            {
                'name': 'command',
                'datatype': 'string',
                'default': '',
                'values_list': self.list_commands,
                'values_list_type': 'sPresetText',
                'flags':['query']
            }, {
                'name': 'ButtonName',
                'datatype': 'string',
                'flags':['optional']
            }
        ]

    def list_commands(self):
        return lx.eval('query commandservice commands ?')

    def commander_execute(self, msg, flags):
        # Get script
        script = self.commander_arg_value(0)
        ButtonName = self.commander_arg_value(1)

        macro = replay.Macro()

        idx = -1
        if macro.primary is None:
            # If there's no primary node, insert at zero
            idx = len(macro.children)
        else:
            # If there's a primary node, insert right after it
            idx = macro.primary.index + 1

        for line in script.split('\n'):
            macro.add_command(command = line, index = idx, ButtonName = ButtonName)
            macro.unsaved_changes = True
            idx += 1

        macro.select(idx - 1)

        macro.rebuild_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

class LineInsertQuietClass(LineInsertClass):
    """Same as `replay.lineInsert`, except it isn't undoable and doesn't show up
    in macros and command history. Used for adding lines during recording."""

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_QUIET

lx.bless(LineInsertClass, 'replay.lineInsert')
lx.bless(LineInsertQuietClass, 'replay.lineInsertQuiet')
