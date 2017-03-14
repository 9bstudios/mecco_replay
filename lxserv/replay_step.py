import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Fires the next step in the macro, allowing you to fire each frame in a Macro
    one-by-one."""
    def commander_execute(self, msg, flags):
        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLineColor())

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        if replay.Macro().is_empty:
            return False
        if not replay.Macro().selected_descendants:
            return False
        return True

class UndoLineColor(lxifc.Undo):
    def __init__(self):
        # Indices to save for undo operation
        self.m_prev_index = -1
        self.m_next_index = -1

    def undo_Forward(self):
        macro = replay.Macro()
        undo_svc = lx.service.Undo()

        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            # Execute primary command and store indices for undo
            self.m_prev_index, self.m_next_index = macro.run_next_line()
        else:
            # This means undo_Forward is executing second time and user doing redo
            # operations. In this case since redo of executed operation will do actual
            # job we only need to move primary node one step down.
            macro.children[self.m_next_index].selected = True
            macro.children[self.m_prev_index].selected = False
        macro.refresh_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Reverse(self):
        macro = replay.Macro()
        # Undo of executed operation will revert the modifications
        # so we only need to move primary node one step up
        macro.children[self.m_prev_index].selected = True
        macro.children[self.m_next_index].selected = False

        macro.refresh_view()
        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)


lx.bless(CommandClass, 'replay.step')
