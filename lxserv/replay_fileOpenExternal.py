# python

# Open in external editor.
# Be sure to close in MODO editor.
# Also add "recent" shortcuts to re-open recent files.
# Also add default location for saving and opening (scripts folder).

import lx, modo, replay
from os.path import basename
import replay.commander as commander
from replay import message as message


"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Opens the currently-open Macro in the filesystem text editor."""


    def commander_execute(self, msg, flags):

        # Stop recording
        lx.eval('replay.record stop')

        file_path = replay.Macro().file_path

        if file_path is None:
            lx.eval('replay.saveAs')

        try:
            file_path = replay.Macro().file_path
            lx.eval('!!file.open {%s}' % file_path)
            lx.eval('replay.fileClose')
        except:
            modo.dialogs.alert(
                message("MECCO_REPLAY", "OPEN_FILE_FAIL"),
                message("MECCO_REPLAY", "OPEN_FILE_FAIL_MSG", basename(file_path))
            )

    def basic_Enable(self, msg):
        if not replay.Macro().file_path:
            return False
        return True


lx.bless(CommandClass, 'replay.fileOpenExternal')
