import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Sets the selected command's `suppress` property in the `Macro()` object's
    `commands` list. Can be queried to return the current state of the selected command."""

    def commander_execute(self, msg, flags):

        for line in replay.Macro().selected_descendants:
            # Toggle the value
            line.suppress = False if line.suppress else True

        replay.Macro().refresh_view()


lx.bless(CommandClass, 'replay.lineSuppress')
