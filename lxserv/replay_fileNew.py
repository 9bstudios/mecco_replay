import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):

    """Create a new macro and close the current one."""
    def commander_execute(self, msg, flags):

        # There's really  no concept of a "blank" document. We just start
        # from a blank macro by closing the current one.
        lx.eval('replay.fileClose')

lx.bless(CommandClass, 'replay.fileNew')
