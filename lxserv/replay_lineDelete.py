import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):
        # NOTE: We have to remove the command from the Macro() object, but also
        # remove it from the ReplayLumberjack() treeview.
        pass


lx.bless(CommandClass, 'replay.lineDelete')
