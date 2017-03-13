import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

class CommandClass(replay.commander.CommanderClass):
    """Export the current `Macro()` to LXM, PY, or JSON using its built-in
    export methods. Accepts optional format and destination arguments. If either
    of these is not provided, a `modo.dialogs.customFile()` will be thrown."""

    def commander_arguments(self):
        return [
            {
                'name': 'format',
                'datatype': 'string',
                'default': replay.Macro().export_format_names,
                'values_list_type': 'popup',
                'values_list': replay.Macro().export_format_names,
                'flags': ['optional']
            }, {
                'name': 'destination',
                'datatype': 'string',
                'flags': ['optional']
            }
        ]

    def commander_execute(self, msg, flags):
        """Saves the current Macro() object to the destination stored in its
        `file_path` property. If `file_path` is `None`, prompt for a destination. Unlike
        `replay.fileSave` this command can save in multiple formats."""

        macro = replay.Macro()

        format_val = self.commander_arg_value(0)
        file_path = self.commander_arg_value(1)

        default_path = lx.eval('query platformservice alias ? {scripts:}')

        if file_path is None:
            file_path = modo.dialogs.customFile(
                dtype = 'fileSave',
                title = 'Export file',
                names = macro.export_format_names,
                unames = macro.export_format_unames,
                ext = macro.export_format_extensions,
                path = default_path
            )
            if file_path is None:
                return
            format_val = lx.eval('dialog.fileSaveFormat ?')

        replay.Macro().render(format_val, file_path)

    def basic_Enable(self, msg):
        if replay.Macro().is_empty:
            return False
        return True

lx.bless(CommandClass, 'replay.fileExport')
