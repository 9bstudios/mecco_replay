import lx, lxifc, modo, replay
from replay import message as message

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

        # Create action list needed to perform this operation
        actionList = self.prepare_action_list(mode, index)

        # Return on errors
        if actionList is None:
            return

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoReorder(actionList))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        return bool(replay.Macro().selected_descendants)

    def prepare_action_list(self, mode, index):

        # Checking mode validity
        if mode not in ['up', 'down', 'top', 'bottom', 'index']:
            modo.dialogs.alert(message("REPLAY_LINE_REORDER", "DLG_TITLE1"), message("REPLAY_LINE_REORDER", "DLG_MSG1", mode), dtype='warning')
            return None

        macro = replay.Macro()

        # Checking index range
        if (mode == 'index') and (index >= len(macro.children)):
            modo.dialogs.alert(message("REPLAY_LINE_REORDER", "DLG_TITLE2"), message("REPLAY_LINE_REORDER", "DLG_MSG2", index), dtype='warning')
            return None

        # Checking if selection exists
        if len(macro.selected_children) == 0:
            modo.dialogs.alert(message("REPLAY_LINE_REORDER", "DLG_TITLE3"), message("REPLAY_LINE_REORDER", "DLG_MSG3"), dtype='warning')
            return None

        actionList = MoveActionList()

        # Getting
        sel_children = macro.selected_children

        # If going up, we move up starting with the top of the list and move down.
        if mode == "up":
            for child in sel_children:
                actionList.append(child.index, child.index - 1)

        elif mode == "down":
            # If going any other direction, start
            sel_children.sort(key=lambda x: x.index, reverse=True)

            for child in sel_children:
                actionList.append(child.index, child.index - 1)

        elif mode == "top":
            for child in sel_children:
                actionList.append(child.index, 0)

        elif mode == "bottom":
            # If going any other direction, start
            sel_children.sort(key=lambda x: x.index, reverse=True)

            for child in sel_children:
                actionList.append(child.index, len(child.parent.children) - 1)

        elif mode == "index":
            # Sort all children standing below target index in reverse order
            sel_children_above = [x for x in sel_children if x.index > index]
            sel_children_below = [x for x in sel_children if x.index <= index]
            sel_children_below.sort(key=lambda x: x.index, reverse=True)
            for child in sel_children_above + sel_children_below:
                actionList.append(child.index, index)

        return actionList


class MoveActionList:
    """ Contains list of source and target indices
        Provides generators for undo and redo operations"""
    def __init__(self):
        self.m_actions = list()

    def append(self, from_idx, to_idx):
        self.m_actions.append((from_idx, to_idx))

    def iter_redo(self):
        """Iterates indiex pairs for redo"""
        for action in self.m_actions:
            yield action

    def iter_undo(self):
        """Iterates indiex pairs for undo"""
        for from_idx, to_idx in reversed(self.m_actions):
            yield (to_idx, from_idx)

class UndoReorder(lxifc.Undo):
    def __init__(self, actionList):
        self.m_actionList = actionList

    def reorder(self, indices):
        """Reorder indices of marco.children for each index pair in indices"""
        macro = replay.Macro()

        # change indices
        for from_idx, to_idx in indices:
            macro.children[from_idx].index = to_idx

        # Rebuild view
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        self.reorder(self.m_actionList.iter_redo())

    def undo_Reverse(self):
        self.reorder(self.m_actionList.iter_undo())


lx.bless(CommandClass, 'replay.lineReorder')
