import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    "Fires the `ReplayMacro().run()` method."
    def commander_execute(self, msg, flags):
        replay.ReplayMacro().run()


lx.bless(CommandClass, 'replay.play')
