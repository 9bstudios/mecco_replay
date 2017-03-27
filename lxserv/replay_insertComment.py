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
                'datatype': 'string'
            }
        ]

    def commander_execute(self, msg, flags):
        comment = self.commander_arg_value(0)
        macro = replay.Macro()

        # Check if selection exists
        selecteds = macro.selected_children
        if len(selecteds) == 0:
            modo.dialogs.alert(message("MECCO_REPLAY", "NO_SELECTED_COMMAND_MSG"), dtype='warning')
            return

        # Collect list of selected command indices
        indices = list()
        for sel in selecteds:
            indices.append(sel.index)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoInsertComment(indices, comment))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        return bool(replay.Macro().selected_descendants)


class UndoInsertComment(lxifc.Undo):
    def __init__(self, indices, comment):
        self.m_indices = indices
        self.m_comment = comment
        self.m_line_counts_before = [-1]*len(self.m_indices)

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()

        # Iterate all selected indices and add comment for each
        for index_idx in xrange(0, len(self.m_indices)):
            # index - index of command to modify
            index = self.m_indices[index_idx]
            # Store line count of old comment for restoring in undo
            self.m_line_counts_before[index_idx] = len(macro.children[index].user_comment_before)
            # Add # before each line in comment and append it
            for line in ("#" + line for line in self.m_comment.split('\n')):
                macro.children[index].user_comment_before.append(line)

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()
        # Iterate all selected indices and remove previously added comments
        for index_idx in xrange(0, len(self.m_indices)):
            # Get index of selected item
            index = self.m_indices[index_idx]
            # Get count of lines in comment before adding new ones
            line_count_before = self.m_line_counts_before[index_idx]
            # Cat comment to restore previous state
            macro.children[index].user_comment_before = macro.children[index].user_comment_before[:line_count_before]

        self.finalize_command(macro)


lx.bless(CommandClass, 'replay.insertComment')
