import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Reads a file from disk and parses it into the `ReplayMacro()` object's built-in
    parse methods."""

    def commander_execute(self, msg, flags):
        # prompt for file open using http://modo.sdk.thefoundry.co.uk/td-sdk/dialogs.html#custom-file-dialog
        pass


lx.bless(CommandClass, 'replay.fileOpen')
