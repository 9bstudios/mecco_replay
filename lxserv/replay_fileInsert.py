import lx, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Reads a file from disk and parses it into the `Macro()` object's built-in
    parse methods."""

    _path = lx.eval('query platformservice alias ? {scripts:}')

    def commander_arguments(self):
        return [
            {
                'name': 'path',
                'datatype': 'string',
                'flags': ['optional']
            }
        ]

    def commander_execute(self, msg, flags):

        # Stop recording
        lx.eval('replay.record stop')

        # Try to get the path from the command line:
        input_path = self.commander_arg_value(0)

        macro = replay.Macro()

        # Get the path from the user, if not given as argument:
        if not input_path:
            input_path = modo.dialogs.customFile(
                dtype = 'fileOpen',
                title = message("MECCO_REPLAY", "OPEN_DIALOG_TITLE"),
                names = macro.import_format_names,
                unames = macro.import_format_unames,
                patterns = macro.import_format_patterns,
                path = self._path
            )
            if input_path is None:
                return
            self.__class__._path = input_path

        # Parse the file in replay.Macro() and rebuild the view:
        try:
            macro.parse('insert', input_path)
            replay.Macro().unsaved_changes = True
        except Exception as err:
            modo.dialogs.alert(message("MECCO_REPLAY", "OPEN_FILE_FAIL"), message("MECCO_REPLAY", "OPEN_FILE_FAIL_MSG", str(err)), dtype='warning')
            
        finally:
            macro.rebuild_view()
            notifier = replay.Notifier()
            notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    # def basic_Enable(self, msg):
    #     if lx.eval('replay.record query:?'):
    #         return False
    #     if not replay.Macro().file_path:
    #         return False
    #     return True

lx.bless(CommandClass, 'replay.fileInsert')
