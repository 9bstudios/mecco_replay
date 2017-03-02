import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Sets the selected command's `suppress` property in the `ReplayMacro()` object's
    `commands` list. Can be queried to return the current state of the selected command."""

    def commander_arguments(self):
        return [
            {
                'name': 'mode',
                'datatype': 'boolean',
                'default': True,
                'flags': ['query', 'optional']
            }
        ]

    def commander_execute(self, msg, flags):
        pass


lx.bless(CommandClass, 'replay.lineSuppress')
