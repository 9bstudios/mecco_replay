# python

import lx, lxifc, modo, replay
import pyperclip

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):

        # collect list of selected paths
        lxm = replay.Macro().render_LXM_selected()
        pyperclip.copy(lxm)

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        for node in replay.Macro().selected_descendants:
            if isinstance(node, replay.MacroBaseCommand):
                return True
        return False

lx.bless(CommandClass, 'replay.copySelection')
