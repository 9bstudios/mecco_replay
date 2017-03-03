import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Throws up a `replay.chameleon` dialog requesting all of the necessary values
    to edit a given command in the `ReplayMacro().commands` list."""
    def commander_execute(self, msg, flags):
        pass


lx.bless(CommandClass, 'replay.lineEdit')