# python

import os
import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    "Fires the `Macro().run()` method."
    def commander_execute(self, msg, flags):
        file_path = lx.eval('query platformservice alias ? {kit_mecco_replay:}')
        file_path = os.path.join(file_path, "Replay_TempFile.LXM")
        file_format = "lxm"
        replay.Macro().render(file_format, file_path)
        lx.eval('@{%s}' % file_path)

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        if replay.Macro().is_empty:
            return False
        return True


lx.bless(CommandClass, 'replay.play')
