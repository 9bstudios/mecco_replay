# python

import lx, lxifc, modo, replay, replay.commander

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Removes values for all selected arguments."""

    def commander_execute(self, msg, flags):
        # collect list of selected paths
        paths = list()
        for node in replay.Macro().selected_descendants:
            if isinstance(node, replay.MacroCommandArg):
                paths.append(node.path)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoArgClear(paths))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        return bool(replay.Macro().selected_descendants)

class UndoArgClear(lxifc.Undo):
    def __init__(self, paths):
        self.m_paths = paths
        self.m_cleared_values = list()

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()
        del self.m_cleared_values[:]

        # Save values in m_cleared_values and clear them
        for path in self.m_paths:
            child = macro.node_for_path(path)
            self.m_cleared_values.append(child.value)
            child.value = None

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()

        assert(len(self.m_paths) == len(self.m_cleared_values))
        # Restore cleared values
        for idx in range(0, len(self.m_paths)):
            path = self.m_paths[idx]
            value = self.m_cleared_values[idx]
            child = macro.node_for_path(path)
            child.value = value

        self.finalize_command(macro)


lx.bless(CommandClass, 'replay.argClear')
