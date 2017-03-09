# python

import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Inserts a comment-only command object into the `Macro().commands` list."""

    def commander_arguments(self):
        return [
            {
                'name': 'query',
                'datatype': 'string',
                'values_list_type': 'fcl',
                'values_list': self.list_commands,
                'flags': ['query']
            }
        ]

    def commander_notifiers(self):
        return [("replay.notifier", "")]

    def list_commands(self):
        nodes = replay.Macro().selected_commands

        args = set()
        for node in nodes:
            for arg in node.args:
                args.add(arg.argName)

        commands_list = []
        for arg in args:
            commands_list.append('replay.argEdit %s ?' % arg)

        return commands_list



lx.bless(CommandClass, 'replay.argEditFCL')
