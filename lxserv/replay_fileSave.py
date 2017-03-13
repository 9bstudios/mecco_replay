import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Saves the current Macro() object to the destination stored in its
    `file_path` property. If `file_path` is `None`, prompt for a destination. Unlike
    `replay.fileExport`, this command only supports saving to the LXM format."""

    def commander_arguments(self):
        return [
               {
                   'name': 'path',
                   'datatype': 'string',
                   'flags': ['optional']
               }
           ]

    def commander_execute(self, msg, flags):
        macro = replay.Macro()

        file_path = macro.file_path
        file_format = macro.file_format
        # If there is no associated file path try to get from command line or prompt the user for new destination

        default_path = lx.eval('query platformservice alias ? {scripts:}')

        if file_path is None:
            # Try to get the path from the command line:
            file_path = self.commander_arg_value(0)
            file_format = "lxm"

            # Prompt the user
            if not file_path:
                file_path = modo.dialogs.customFile(dtype = 'fileSave', title = 'Save LXM file', \
                       names = ('LXM',), unames = ('LXM file'), ext=('LXM',), path = default_path)
                if file_path is None:
                    return
            # And save it for the next time
            macro.file_path = file_path

        macro.render(file_format, file_path)

        lx.eval('replay.fileOpenAddRecent {%s}' % input_path)

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        if replay.Macro().is_empty:
            return False
        return True


lx.bless(CommandClass, 'replay.fileSave')
