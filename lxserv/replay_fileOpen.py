import lx, modo, replay, os

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Reads a file from disk and parses it into the `Macro()` object's built-in
    parse methods."""

    def commander_arguments(self):
        return [
            {
                'name': 'path',
                'datatype': 'string',
                'flags': ['optional']
            }
        ]

    def basic_ButtonName(self):
        input_path = self.commander_arg_value(0)
        if input_path:
            return os.path.basename(input_path)
        else:
            lx.notimpl()

    def commander_execute(self, msg, flags):

        # Try to get the path from the command line:
        input_path = self.commander_arg_value(0)

        macro = replay.Macro()

        default_path = lx.eval('query platformservice alias ? {scripts:}')

        # Get the path from the user, if not given as argument:
        if not input_path:
            input_path = modo.dialogs.customFile(
                dtype = 'fileOpen',
                title = 'Open LXM file',
                names = macro.import_format_names,
                unames = macro.import_format_unames,
                patterns = macro.import_format_patterns,
                path = default_path
            )
            if input_path is None:
                return

        # Parse the file in replay.Macro() and rebuild the view:
        macro.parse(input_path)
        macro.rebuild_view()

        lx.eval('replay.fileOpenAddRecent {%s}' % input_path)

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

lx.bless(CommandClass, 'replay.fileOpen')
