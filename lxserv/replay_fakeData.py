import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Populates the `ReplayLumberjack()` class with fake values for testing."""

    def commander_execute(self, msg, flags):
        jack = replay.ReplayLumberjack()

        task = jack.add_child()
        task.values['name'].value = "Render"
        task.values['command'].value = 'render'
        task.values['enable'].value = True



lx.bless(CommandClass, 'replay.fakeData')
