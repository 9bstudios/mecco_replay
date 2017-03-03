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
            task.values['enable'].value = lx.eval(True)
            # if task.values['enable'].value:
            task.values['enable'].icon_resource = 'MIMG_CHECKMARK'
            task.values['enable'].display_value = ''
            # task.values['enable'].cell_command = 'pref.value animation.chanControls ?'
            # task.values['enable'].batch_command = 'pref.value animation.chanControls ?'
            # task.values['enable'].use_cell_command_for_display = True

            for i in range(3):
                att = task.add_child()
                att.values['name'].value = "arg%s" % i
                att.values['command'].value = "value%s" % i

lx.bless(CommandClass, 'replay.fakeData')
