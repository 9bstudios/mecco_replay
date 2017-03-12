import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Sets the row color for the currently-selected macro command(s)."""
    def commander_arguments(self):
        return [
            {
                'name': 'color_name',
                'datatype': 'string',
                'default': 'none',
                'values_list_type': 'popup',
                'values_list': [
                    'none',
                    'red',
                    'magenta',
                    'pink',
                    'brown',
                    'orange',
                    'yellow',
                    'green',
                    'light_g',
                    'cyan',
                    'blue',
                    'light_blue',
                    'ultrama',
                    'purple',
                    'light_pu',
                    'dark_grey',
                    'grey',
                    'white'
                ]
            }
        ]

    def commander_execute(self, msg, flags):
        color_name = self.commander_arg_value(0, 'none')

        # Add actions needed to undo and redo this command
        actionList = ColorActionList()
        for line in replay.Macro().selected_descendants:
            actionList.append(line.index, line.row_color, color_name)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLineColor(actionList))

class ColorActionList:
    def __init__(self):
        self.m_actions = list()

    def append(self, index, prev_color, new_color):
        """Add action in action list"""
        self.m_actions.append((index, prev_color, new_color))

    def iter_redo(self):
        """iterate actions for redo"""
        for index, prev_color, new_color in self.m_actions:
            yield (index, new_color)

    def iter_undo(self):
        """iterate actions for undo"""
        for index, prev_color, new_color in self.m_actions:
            yield (index, prev_color)

class UndoLineColor(lxifc.Undo):
    def __init__(self, actionList):
        self.m_actionList = actionList

    def apply(self, actions):
        """Change colors for each item in actions"""
        macro = replay.Macro()

        # Change color of selected nodes
        for index, color in actions:
            macro.children[index].row_color = color

        # Rebuild view
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        self.apply(self.m_actionList.iter_redo())
    
    def undo_Reverse(self):
        self.apply(self.m_actionList.iter_undo())

lx.bless(CommandClass, 'replay.lineColor')
