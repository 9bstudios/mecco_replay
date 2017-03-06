import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Throws up a `replay.chameleon` dialog requesting all of the necessary values
    to edit a given command in the `Macro().commands` list."""
    def commander_execute(self, msg, flags):
        modo.dialogs.alert("Not Implemented.", "Command not yet implemented.")


lx.bless(CommandClass, 'replay.lineEdit')
