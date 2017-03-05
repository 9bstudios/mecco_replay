import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Populates the `ReplayLumberjack()` class with fake values for testing."""

    def commander_execute(self, msg, flags):
        macro = replay.Macro()

        commands = [
            ('Primitive', 'script.run "macro.scriptservice:27554333777:macro"'),
            ('Transform Channel', 'transform.channel pos.X 1.0'),
            ('Primitive', 'script.run "macro.scriptservice:19601433555:macro"'),
            ('Transform Channel', 'transform.channel pos.X -1.0'),
            ('Primitive', 'script.run "macro.scriptservice:47158833888:macro"'),
            ('Transform Channel', 'transform.channel pos.Y 1.0')
        ]

        for command in commands:
            macro_command = macro.add_command(command_string=command[1])
            macro_command.values['name'].value = command[0]
            # macro_command.values['command'].value = command[1]
            macro.rebuild_view()

lx.bless(CommandClass, 'replay.fakeData')
