import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):

    def commander_arguments(self):
        return [
            {
                'name': 'mode',
                'datatype': 'string',
                'default': 'index',
                'values_list_type': 'popup',
                'values_list': ['up', 'down', 'top', 'bottom', 'index']
            }, {
                'name': 'index',
                'datatype': 'integer',
                'default': 0
            }
        ]

    def commander_execute(self, msg, flags):
        pass


lx.bless(CommandClass, 'replay.lineReorder')
