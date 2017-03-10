# python

import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Removes values for all selected arguments."""

    def commander_execute(self, msg, flags):
        nodes = replay.Macro().selected_descendants

        for node in [n for n in nodes if isinstance(n, replay.MacroCommandArg)]:
            node.value = None

        replay.Macro().refresh_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def basic_Enable(self, msg):
        return bool(replay.Macro().selected_descendants)

lx.bless(CommandClass, 'replay.argClear')
