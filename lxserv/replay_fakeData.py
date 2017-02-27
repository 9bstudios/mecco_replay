import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):

    def commander_execute(self, msg, flags):
        a = replay.ReplayLumberjack()

        a.add_child().add_child().add_child()
        a.add_child()
        a.add_child()



lx.bless(CommandClass, 'replay.fakeData')
