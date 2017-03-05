import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):

    def commander_arguments(self):
        return [
               {
                   'name': 'path',
                   'datatype': 'string',
                   'flags': ['optional']
               }
           ]

    """Saves the current Macro() object to the destination stored in its
    `file_path` property. If `file_path` is `None`, prompt for a destination. Unlike
    `replay.fileExport`, this command only supports saving to the LXM format."""
    def commander_execute(self, msg, flags):
        # If macro is empty throw warning and return
        if replay.Macro().is_empty:
           modo.dialogs.alert("Empty macro", "There are no recorded commands to save", dtype='warning')
           return

        file_path = replay.Macro().file_path
        # If there is no associated file path try to get from command line or prompt the user for new destination
        if file_path is None:
            # Try to get the path from the command line:
            file_path = self.commander_arg_value(0)
            
            # Prompt the user
            if not file_path:
                file_path = modo.dialogs.customFile(dtype = 'fileSave', title = 'Save LXM file', \
                       names = ('LXM',), unames = ('LXM file'), ext=('LXM',))
                if file_path is None:
                    return
            # And save it for the next time
            replay.Macro().file_path = file_path

        replay.Macro().render_LXM(file_path)


lx.bless(CommandClass, 'replay.fileSave')
