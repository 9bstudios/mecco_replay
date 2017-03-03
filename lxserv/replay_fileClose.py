import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Close the current `Macro()` and, if necessary, prompt user to save changes."""

    def commander_execute(self, msg, flags):
        pass

lx.bless(CommandClass, 'replay.fileClose')
