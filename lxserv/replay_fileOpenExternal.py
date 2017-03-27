# python

# Open in external editor.
# Be sure to close in MODO editor.
# Also add "recent" shortcuts to re-open recent files.
# Also add default location for saving and opening (scripts folder).

import lx, modo, replay
import replay.commander as commander

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Opens the currently-open Macro in the filesystem text editor."""
    def commander_execute(self, msg, flags):

        # Stop recording
        lx.eval('replay.record stop')

        file_path = replay.Macro().file_path
        lx.eval('replay.fileClose')
        lx.eval('file.open {%s}' % file_path)

    def basic_Enable(self, msg):
        if not replay.Macro().file_path:
            return False
        return True


lx.bless(CommandClass, 'replay.fileOpenExternal')
