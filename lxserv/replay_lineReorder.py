import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Reorders the selected command within the `Macro()` object.
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
        # Get arguments
        mode = self.commander_arg_value(0)
        index = self.commander_arg_value(1)

        # Checking mode validity
        if mode not in ['up', 'down', 'top', 'bottom', 'index']:
            raise Exception('Wrong mode "%s".' % mode)

        macro = replay.Macro()

        # Checking index range
        if (mode == 'index') and (index >= len(macro.children)):
            raise Exception('Index "%s" is out of range.' % index)

        # Checking if selection exists
        if len(macro.selected_children) == 0:
            modo.dialogs.alert("Empty selection", "There are no selected commands to reorder", dtype='warning')
            return

        # reorder commands
        macro.reorder(mode, index)

        macro.refresh_view()


lx.bless(CommandClass, 'replay.lineReorder')
