import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Inserts a whitespace-only command object into the `ReplayMacro().commands` list."""

    def commander_execute(self, msg, flags):
        pass


lx.bless(CommandClass, 'replay.insertWhitespace')
