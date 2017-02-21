import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):

    def commander_arguments(self):
        return [
            {
                'name': 'dish1',
                'datatype': 'string',
                'label': 'First Dish',
                'default': 'bacon',
                'values_list_type': 'popup',
                'values_list': ['bacon', 'quinoa']
            }, {
                'name': 'dish2',
                'datatype': 'string',
                'label': 'Second Dish',
                'default': 'eggs',
                'values_list_type': 'sPresetText',
                'values_list': ['eggs', 'kale']
            }
        ]

    def commander_execute(self, msg, flags):
        pass


lx.bless(CommandClass, 'replay.fileExport')
