import lx, lxifc, modo, replay

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
            modo.dialogs.alert("Warning: There is no selected command(s)", dtype='warning')
            return

        # Collect list of selected command indices
        indices = list()
        for sel in selecteds:
            indices.append(sel.index)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoInsertComment(indices, comment))


class UndoInsertComment(lxifc.Undo):
    def __init__(self, indices, comment):
        self.m_indices = indices
        self.m_comment = comment
        self.m_line_counts_before = [-1]*len(self.m_indices)

    def finalize_command(self, macro):
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()
        for index_idx in xrange(0, len(self.m_indices)):
            index = self.m_indices[index_idx]
            self.m_line_counts_before[index_idx] = len(macro.children[index].user_comment_before)
            for line in ("#" + line for line in self.m_comment.split('\n')):
                macro.children[index].user_comment_before.append(line)

        self.finalize_command(macro)
    
    def undo_Reverse(self):
        macro = replay.Macro()
        for index_idx in xrange(0, len(self.m_indices)):
            index = self.m_indices[index_idx]
            line_count_before = self.m_line_counts_before[index_idx]
            macro.children[index].user_comment_before = macro.children[index].user_comment_before[:line_count_before]

        self.finalize_command(macro)
        

lx.bless(CommandClass, 'replay.insertComment')
