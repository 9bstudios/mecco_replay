import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    "Fires the `Macro().run()` method."
    def commander_execute(self, msg, flags):
        replay.Macro().run()


lx.bless(CommandClass, 'replay.play')
