import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Sets the row color for the currently-selected macro command(s)."""
    def commander_execute(self, msg, flags):
        pass

lx.bless(CommandClass, 'replay.lineColor')
