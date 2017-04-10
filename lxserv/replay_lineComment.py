# python

import lx, lxifc, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Inserts a comment-only command object into the `Macro().commands` list."""

    def commander_arguments(self):
        return [
            {
                'name': 'comment',
                'datatype': 'string',
                'default': '',
                'flags':[]
            }
        ]

    def commander_execute(self, msg, flags):
        comment = self.commander_arg_value(0)
        macro = replay.Macro()

        # Check if selection exists
        selecteds = macro.selected_descendants
        if len(selecteds) == 0:
            modo.dialogs.alert(message("MECCO_REPLAY", "NO_SELECTED_COMMAND_MSG"), dtype='warning')
            return

        # Collect list of selected command paths
        paths = list()
        for sel in selecteds:
            paths.append(sel.path)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoInsertComment(paths, comment))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if len(replay.Macro().selected_descendants) == 0:
            return False

        for command in replay.Macro().selected_descendants:
            if not command.can_add_command():
                return False

        return True


class UndoInsertComment(lxifc.Undo):
    def __init__(self, paths, comment):
        self.m_paths = paths
        self.m_comment = comment
        self.m_line_counts_before = [-1]*len(self.m_paths)

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()

        # Iterate all selected paths and add comment for each
        for path_idx in xrange(0, len(self.m_paths)):
            # path - path of command to modify
            path = self.m_paths[path_idx]
            # Store line count of old comment for restoring in undo
            self.m_line_counts_before[path_idx] = len(macro.node_for_path(path).user_comment_before)
            # Add # before each line in comment and append it
            for line in self.m_comment.split('\n'):
                macro.node_for_path(path).user_comment_before.append(line)

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()
        # Iterate all selected indices and remove previously added comments
        for path_idx in xrange(0, len(self.m_paths)):
            # Get path of selected item
            path = self.m_paths[path_idx]
            # Get count of lines in comment before adding new ones
            line_count_before = self.m_line_counts_before[path_idx]
            # Cat comment to restore previous state
            macro.node_for_path(path).user_comment_before = macro.node_for_path(path).user_comment_before[:line_count_before]

        self.finalize_command(macro)

lx.bless(CommandClass, 'replay.lineComment')
