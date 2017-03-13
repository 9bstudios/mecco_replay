import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    "Fires the `Macro().run()` method."
    def commander_execute(self, msg, flags):
        replay.Macro().run()

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        if replay.Macro().is_empty:
            return False
        return True


lx.bless(CommandClass, 'replay.play')
