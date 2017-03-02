import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """Reorders the selected command within the `ReplayMacro()` object.
    `mode` argument can move command `up` one space, `down` one space, to the `top`,
    to the `bottom`, or to a specific `index` as specified in the `index` argument.
    (`index` argument is ignored unless `mode` is set to `index`.)"""

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
                'default': 0,
                'flags': ['optional']
            }
        ]

    def commander_execute(self, msg, flags):
        pass


lx.bless(CommandClass, 'replay.lineReorder')
