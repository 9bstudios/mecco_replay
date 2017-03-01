import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class FCLClass(replay_commander.CommanderClass):
    """Renders a Form Command List (FCL) that is rendered in the MODO modes tail."""

    def commander_arguments(self):
        return [
            {
                'name': 'query',
                'datatype': 'boolean',
                'values_list_type': 'fcl',
                'values_list': self.list_commands
            }
        ]

    def commander_execute(self, msg, flags):
        pass

    def list_commands(self):
        return ['noop']

lx.bless(FCLClass, 'replay.ModesTailFCL')


class CommandClass(replay_commander.CommanderClass):
    """Appends an FCL in the modes tail with an @ syntax script call."""

    def commander_arguments(self):
        return [
            {
                'name': 'path',
                'datatype': 'string'
            }
        ]

    def commander_execute(self, msg, flags):
        pass

    def append_to_fcl(self):
        # appends a list of elements that is available to FCLClass.list_commands(),
        # and is also stored between sessions (probably using user values)
        pass


lx.bless(CommandClass, 'replay.addToModesTail')
