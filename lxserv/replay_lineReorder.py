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
            modo.dialogs.alert("Empty selection", 'Wrong mode "%s".' % mode, dtype='warning')
            return

        macro = replay.Macro()

        # Checking index range
        if (mode == 'index') and (index >= len(macro.children)):
            modo.dialogs.alert("Empty selection", 'Index "%s" is out of range.' % index, dtype='warning')
            return

        # Checking if selection exists
        if len(macro.selected_children) == 0:
            modo.dialogs.alert("Empty selection", "There are no selected commands to reorder", dtype='warning')
            return

        # Getting
        sel_children = macro.selected_children

        # If going up, we move up starting with the top of the list and move down.
        if mode == "up":
            for child in sel_children:
                child.reorder_up()

        elif mode == "down":
            # If going any other direction, start
            sel_children.sort(key=lambda x: x.index, reverse=True)

            for child in sel_children:
                child.reorder_down()

        elif mode == "top":
            # If going any other direction, start
            sel_children.sort(key=lambda x: x.index, reverse=True)

            for child in sel_children:
                child.reorder_top()

        elif mode == "bottom":
            for child in sel_children:
                child.reorder_bottom()

        elif mode == "index":
            for child in sel_children:
                child.index = index

        macro.rebuild_view()
        replay.Macro().unsaved_changes = True


lx.bless(CommandClass, 'replay.lineReorder')
