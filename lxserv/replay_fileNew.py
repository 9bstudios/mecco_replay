import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):

    """Create a new macro and close the current one."""
    def commander_execute(self, msg, flags):

        # There's really  no concept of a "blank" document. We just start
        # from a blank macro by closing the current one.
        lx.eval('!!replay.fileClose')

        # Stop recording
        lx.eval('replay.record stop')

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        return True

lx.bless(CommandClass, 'replay.fileNew')
