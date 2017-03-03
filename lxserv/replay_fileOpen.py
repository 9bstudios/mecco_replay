import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Reads a file from disk and parses it into the `ReplayMacro()` object's built-in
    parse methods."""

    def commander_execute(self, msg, flags):

        # Get the complete file path from the user:
        input_path = modo.dialogs.customFile(dtype = 'fileOpen', title = 'Open LXM file', \
           names = ('LXM',), unames = ('LXM file'), patterns = ('*.LXM', '*.lxm'))

        replay.ReplayMacro().parse_LXM(input_path)

lx.bless(CommandClass, 'replay.fileOpen')
