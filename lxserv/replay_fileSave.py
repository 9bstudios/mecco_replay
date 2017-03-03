import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Saves the current ReplayMacro() object to the destination stored in its
    `file_path` property. If `file_path` is `None`, prompt for a destination. Unlike
    `replay.fileExport`, this command only supports saving to the LXM format."""
    def commander_execute(self, msg, flags):
        # For save prompt, see http://modo.sdk.thefoundry.co.uk/td-sdk/dialogs.html#custom-file-dialog

        # If search string is empty throw warning and return
        if replay.ReplayMacro().is_empty:
           modo.dialogs.alert("Empty macro", "There are no recorded commands to save", dtype='warning')
           return

        file_path = replay.ReplayMacro().file_path
        # If there is no associated file path prompt the user for new destination
        if file_path is None:
            file_path = modo.dialogs.customFile(dtype = 'fileSave', title = 'Save LXM file', \
                   names = ('LXM',), unames = ('LXM file'), patterns = ('*.LXM', '*.lxm'))
            # And save it for the next time
            replay.ReplayMacro().file_path = file_path

        replay.ReplayMacro().render_LXM(file_path)


lx.bless(CommandClass, 'replay.fileSave')
