# python

import lx, lxifc, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

class CommandClass(replay.commander.CommanderClass):
    """Selects the first command or block node in the Macro."""

    def commander_execute(self, msg, flags):
        replay.Macro().clear_selection()
        try:
            replay.Macro().commands[0].selected = True
        except:
            pass


lx.bless(CommandClass, 'replay.lineSelectFirst')
