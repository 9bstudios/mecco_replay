import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Populates the `ReplayLumberjack()` class with fake values for testing."""

    def commander_execute(self, msg, flags):
        a = replay.ReplayLumberjack()

        b = a.add_child()
        b.values['name'].value = "Adam"
        b.values['value'].value = 34
        b.values['enable'].value = True

        b = a.add_child()
        b.values['name'].value = "Robin"
        b.values['value'].value = 32
        b.values['enable'].value = True

        c = b.add_child()
        c.values['name'].value = "Iris"
        c.values['value'].value = 3
        c.values['enable'].value = True

        c = b.add_child()
        c.values['name'].value = "Ian"
        c.values['value'].value = 0
        c.values['enable'].value = True

        c = b.add_child()
        c.values['name'].value = "Ignatius"
        c.values['value'].value = 0
        c.values['enable'].value = False



lx.bless(CommandClass, 'replay.fakeData')
