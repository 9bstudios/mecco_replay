import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Populates the `ReplayLumberjack()` class with fake values for testing."""

    def commander_execute(self, msg, flags):
        jack = replay.ReplayMacro()

        commands = [
            ('Primitive', 'script.run "macro.scriptservice:27554333777:macro"'),
            ('Transform Channel', 'transform.channel pos.X 1.0'),
            ('Primitive', 'script.run "macro.scriptservice:19601433555:macro"'),
            ('Transform Channel', 'transform.channel pos.X -1.0'),
            ('Primitive', 'script.run "macro.scriptservice:47158833888:macro"'),
            ('Transform Channel', 'transform.channel pos.Y 1.0')
        ]

        for command in commands:
            jack.add_command(command)

lx.bless(CommandClass, 'replay.fakeData')
