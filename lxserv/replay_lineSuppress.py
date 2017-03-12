import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Sets the selected command's `suppress` property in the `Macro()` object's
    `commands` list. Can be queried to return the current state of the selected command."""

    def commander_execute(self, msg, flags):
        # Collect selected indices
        indices = list()
        for line in replay.Macro().selected_descendants:
            indices.append(line.index)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLineSuppress(indices))

class UndoLineSuppress(lxifc.Undo):
    def __init__(self, indices):
        self.m_indices = indices

    def toggle(self):
        """Toggle suppress for each item in indices"""
        macro = replay.Macro()

        # Toggle suppress flag of selected nodes
        for index in self.m_indices:
            macro.children[index].suppress = False if macro.children[index].suppress else True

        # Rebuild view
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        self.toggle()
    
    def undo_Reverse(self):
        self.toggle()

lx.bless(CommandClass, 'replay.lineSuppress')
