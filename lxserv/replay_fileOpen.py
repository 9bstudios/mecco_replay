import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Reads a file from disk and parses it into the `Macro()` object's built-in
    parse methods."""

    def commander_execute(self, msg, flags):

        # Get the complete file path from the user:
        input_path = modo.dialogs.customFile(dtype = 'fileOpen', title = 'Open LXM file', \
           names = ('LXM',), unames = ('LXM file'), patterns = ('*.LXM', '*.lxm'))

        replay.Macro().parse_LXM(input_path)
        replay.Macro().rebuild_view()

lx.bless(CommandClass, 'replay.fileOpen')
