# python

import lx, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class RunScriptCommand(replay.commander.CommanderClass):

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
                title = message("MECCO_REPLAY", "RUN_DIALOG_TITLE"),
                names = macro.import_format_names,
                unames = macro.import_format_unames,
                patterns = macro.import_format_patterns
            )
            if input_path is None:
                return

        if macro.file_path == input_path and macro.unsaved_changes and not macro.is_empty:
            if modo.dialogs.yesNo(message("MECCO_REPLAY", "ASK_FOR_SAVE_BEFORE_RUN_DIALOG_TITLE"), message("MECCO_REPLAY", "ASK_FOR_SAVE_BEFORE_RUN_DIALOG_MSG")) == 'yes':
                macro.render(macro.file_format, macro.file_path)

        lx.eval('@{%s}' % input_path)

    def basic_Enable(self, msg):
        return True


lx.bless(RunScriptCommand, 'replay.runScript')
