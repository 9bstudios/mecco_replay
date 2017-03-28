# python

import lx, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Maps the currently-open Macro to a key."""
    def commander_execute(self, msg, flags):
        # Stop recording
        lx.eval('replay.record stop')

        macro = replay.Macro()

        if macro.file_path:
            lx.eval('cmds.mapKey command:{@{%s}}' % macro.file_path)

        else:
            default_path = lx.eval('query platformservice alias ? {scripts:}')

            # Get the path from the user, if not given as argument:
            file_path = modo.dialogs.customFile(
                dtype = 'fileOpen',
                title = message("MECCO_REPLAY", "KEY_MAPPING_SCRIPT"),
                names = macro.import_format_names,
                unames = macro.import_format_unames,
                patterns = macro.import_format_patterns,
                path = default_path
            )
            if file_path is None:
                return

            lx.eval('cmds.mapKey command:{@{%s}}' % file_path)


lx.bless(CommandClass, 'replay.mapToKey')
