import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Saves the current ReplayMacro() object to the destination stored in its
    `file_path` property. If `file_path` is `None`, prompt for a destination. Unlike
    `replay.fileExport`, this command only supports saving to the LXM format."""
    def commander_execute(self, msg, flags):
        # For save prompt, see http://modo.sdk.thefoundry.co.uk/td-sdk/dialogs.html#custom-file-dialog
        pass


lx.bless(CommandClass, 'replay.fileSave')
