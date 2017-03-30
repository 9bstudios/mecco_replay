# python

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
                'values_list_type': self.values_list_type,
                'flags':['query']
            }, {
                'name': 'ButtonName',
                'datatype': 'string',
                'flags':['optional', 'hidden']
            }
        ]
        
    def values_list_type(self):
        return 'sPresetText'

    def list_commands(self):
        return lx.eval('query commandservice commands ?')

    def commander_execute(self, msg, flags):
        # Get script
        script = self.commander_arg_value(0).replace("\q","?")
        ButtonName = self.commander_arg_value(1)

        macro = replay.Macro()

        path = None
        if macro.primary is None:
            # If there's no primary node, insert at end
            path = macro.root.path + [len(macro.children)]
        else:
            # If there's a primary node, insert right after it
            path = macro.primary.path
            path[-1] += 1

        for line in script.split('\n'):
            macro.add_command(command = line, path = path, ButtonName = ButtonName)
            macro.unsaved_changes = True
            path[-1] += 1

        path[-1] -= 1
        macro.select(path)

        macro.rebuild_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

class LineInsertSpecialClass(LineInsertClass):
    """Same as `replay.lineInsert`, except it isn't undoable and doesn't show up
    in macros and command history. Used for adding lines during recording."""

    def list_commands(self):
        return [
            ('scene.load', 'Open...'),
            ('scene.save', 'Save'),
            ('scene.save rename', 'Save As...'),
            ('scene.save export', 'Export...'),
            ('preset.do', 'Preset Do'),
        ]
        
    def values_list_type(self):
        return 'popup'

class LineInsertQuietClass(LineInsertClass):
    """Same as `replay.lineInsert`, except it isn't undoable and doesn't show up
    in macros and command history. Used for adding lines during recording."""

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_QUIET


lx.bless(LineInsertClass, 'replay.lineInsert')
lx.bless(LineInsertSpecialClass, 'replay.lineInsertSpecial')
lx.bless(LineInsertQuietClass, 'replay.lineInsertQuiet')
