import lx, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):

    """Deletes selected nodes and clears selected arg values. Mapped to delete and backspace key in Replay."""
    def commander_execute(self, msg, flags):
        primary = replay.Macro().primary

        if not primary:
            return

        if isinstance(primary, (replay.MacroCommand, replay.MacroBlockCommand)):
            try:
                lx.eval('replay.lineDelete')
            except:
                pass

        elif isinstance(primary, replay.MacroCommandArg):
            try:
                lx.eval('replay.argClear')
            except:
                pass

    def basic_Enable(self, msg):
        return True

lx.bless(CommandClass, 'replay.delete')
