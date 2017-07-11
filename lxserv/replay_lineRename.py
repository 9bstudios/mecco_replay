# python

import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Sets the row color for the currently-selected macro command(s)."""
    def commander_arguments(self):
        return [
            {
                'name': 'name',
                'datatype': 'string',
                'default': '',
                'flags':[]
            }
        ]

    def commander_execute(self, msg, flags):
        name = self.commander_arg_value(0, 'none')

        # Add actions needed to undo and redo this command
        actionList = NameActionList()
        for line in replay.Macro().selected_descendants:
            actionList.append(line.path, line.name, name)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLineRename(actionList))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if len(replay.Macro().selected_descendants) == 0:
            return False

        for command in replay.Macro().selected_descendants:
            if not command.can_change_name():
                return False

        return True

class NameActionList:
    def __init__(self):
        self.m_actions = list()

    def append(self, path, prev_name, new_name):
        """Add action in action list"""
        self.m_actions.append((path, prev_name, new_name))

    def iter_redo(self):
        """iterate actions for redo"""
        for path, prev_name, new_name in self.m_actions:
            yield (path, new_name)

    def iter_undo(self):
        """iterate actions for undo"""
        for path, prev_name, new_name in self.m_actions:
            yield (path, prev_name)

class UndoLineRename(lxifc.Undo):
    def __init__(self, actionList):
        self.m_actionList = actionList

    def apply(self, actions):
        """Change colors for each item in actions"""
        macro = replay.Macro()

        # Change name of selected nodes
        for path, name in actions:
            macro.node_for_path(path).name = name

        # Rebuild view
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        self.apply(self.m_actionList.iter_redo())

    def undo_Reverse(self):
        self.apply(self.m_actionList.iter_undo())


lx.bless(CommandClass, 'replay.lineRename')
