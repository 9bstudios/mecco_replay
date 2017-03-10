import lx, modo, replay

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

    def commander_execute(self, msg, flags):

        # Try to get the path from the command line:
        input_path = self.commander_arg_value(0)

        macro = replay.Macro()

        # Get the path from the user, if not given as argument:
        if not input_path:
            input_path = modo.dialogs.customFile(
                dtype = 'fileOpen',
                title = 'Open LXM file',
                names = macro.import_format_names,
                unames = macro.import_format_unames,
                patterns = macro.import_format_patterns
            )
            if input_path is None:
                return

        # Parse the file in replay.Macro() and rebuild the view:
        macro.parse_and_insert(input_path)
        macro.rebuild_view()

        replay.Macro().unsaved_changes = True

lx.bless(CommandClass, 'replay.fileInsert')
