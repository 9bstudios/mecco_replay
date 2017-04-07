# python

import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):

        # collect list of selected paths
        paths = list()
        for line in replay.Macro().selected_descendants:
            paths.append(line.path)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLineDelete(paths))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if len(replay.Macro().selected_descendants) == 0:
            return False

        for command in replay.Macro().selected_descendants:
            if not command.can_delete():
                return False

        return True

class UndoLineDelete(lxifc.Undo):
    def __init__(self, paths):
        self.m_paths = paths
        # Need to delete paths sorted in reverse order to not invalidate other paths
        # Default list comparision working in our case
        self.m_paths.sort(reverse=True)
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

        # delete selected paths and store them in json form to be able to undo
        for path in self.m_paths:
            child = macro.node_for_path(path)
            self.m_deleted_commands.append((path, child.render_json()))
            child.delete()

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()

        # Sort paths in ascending order for undo operation
        # Default list comparision working in our case
        self.m_deleted_commands.sort(key=lambda x: x[0])

        # Restore deleted commands
        for removed_path, json in self.m_deleted_commands:
            macro.add_command(command_json = json, path = removed_path)
            macro.node_for_path(removed_path).selected = True

        self.finalize_command(macro)


lx.bless(CommandClass, 'replay.lineDelete')
