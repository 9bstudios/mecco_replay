import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):

        for line in replay.Macro().selected_descendants: line.delete()

        replay.Macro().rebuild_view()
        replay.Macro().unsaved_changes = True


lx.bless(CommandClass, 'replay.lineDelete')
