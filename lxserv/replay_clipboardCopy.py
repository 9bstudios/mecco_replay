# python

import lx, lxifc, modo, replay
import pyperclip

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):

        lxm = replay.Macro().render_LXM_selected()
        pyperclip.copy(lxm)

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if len(replay.Macro().selected_descendants) == 0:
            return False

        for command in replay.Macro().selected_descendants:
            if not command.can_copy():
                return False

        return True

lx.bless(CommandClass, 'replay.clipboardCopy')
