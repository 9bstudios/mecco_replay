import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Maps the currently-open Macro to a key."""
    def commander_execute(self, msg, flags):
        modo.dialogs.alert("Not Implemented.", "Command not yet implemented.")

    def basic_Enable(self, msg):
        return False

lx.bless(CommandClass, 'replay.mapToKey')
