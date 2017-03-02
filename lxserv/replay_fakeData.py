import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Populates the `ReplayLumberjack()` class with fake values for testing."""

    def commander_execute(self, msg, flags):
        jack = replay.ReplayLumberjack()

        commands = [
            ('Primitive', 'script.run "macro.scriptservice:27554333777:macro"'),
            ('Transform Channel', 'transform.channel pos.X 1.0'),
            ('Primitive', 'script.run "macro.scriptservice:19601433555:macro"'),
            ('Transform Channel', 'transform.channel pos.X -1.0'),
            ('Primitive', 'script.run "macro.scriptservice:47158833888:macro"'),
            ('Transform Channel', 'transform.channel pos.Y 1.0')
        ]

        for command in commands:
            task = jack.add_child()
            task.values['name'].value = command[0]
            task.values['command'].value = command[1]
            task.values['command'].color.special = 4113
            task.values['enable'].value = True
            task.values['enable'].cell_command = 'select.typeFrom "item;pivot;center;edge;polygon;vertex;ptag" ?'
            task.values['enable'].batch_command = 'select.typeFrom "item;pivot;center;edge;polygon;vertex;ptag" ?'

lx.bless(CommandClass, 'replay.fakeData')
