import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):

        # collect list of selected indices
        indices = list()
        for line in replay.Macro().selected_descendants:
            indices.append(line.index)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLineDelete(indices))

class UndoLineDelete(lxifc.Undo):
    def __init__(self, indices):
        self.m_indices = indices
        # Need to delete indices sorted in reverse order to not invalidate other indices
        self.m_indices.sort(reverse=True)
        self.m_deleted_commands = list()

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()
        del self.m_deleted_commands[:]

        # delete selected indices and store them in json form to be able to undo
        for index in self.m_indices:
            child = macro.children[index]
            self.m_deleted_commands.append((index, child.render_json()))
            child.delete()

        self.finalize_command(macro)
    
    def undo_Reverse(self):
        macro = replay.Macro()

        # Sort indices in ascending order for undo operation
        self.m_deleted_commands.sort(key=lambda x: x[0])

        # Restore deleted commands
        for removed_index, json in self.m_deleted_commands:
            macro.add_command(command_json = json, index = removed_index)
            macro.children[removed_index].selected = True

        self.finalize_command(macro)


lx.bless(CommandClass, 'replay.lineDelete')
