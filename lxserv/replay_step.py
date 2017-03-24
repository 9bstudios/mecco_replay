import lx, lxifc, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Fires the next step in the macro, allowing you to fire each frame in a Macro
    one-by-one."""
    def commander_execute(self, msg, flags):
        # Register Undo object performing operation and apply it
        macro = replay.Macro()
        if macro.all_suppressed():
            modo.dialogs.alert(message("MECCO_REPLAY", "EMPTY_MACRO"), message("MECCO_REPLAY", "EMPTY_MACRO_MSG"), dtype='warning')
            return
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            step = UndoStep()
            try:
                step.undo_Forward()
            except:
                return
            undo_svc.Record(step)

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        if replay.Macro().is_empty:
            return False
        return all(node.canEval() for node in replay.Macro().selected_descendants)

class UndoStep(lxifc.Undo):
    def __init__(self):
        # Indices to save for undo operation
        self.m_prev_path = []
        self.m_next_path = []

    def undo_Forward(self):
        macro = replay.Macro()
        undo_svc = lx.service.Undo()

        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            # Execute primary command and store indices for undo
            self.m_prev_path, self.m_next_path = macro.run_next_line()
        else:
            # This means undo_Forward is executing second time and user doing redo
            # operations. In this case since redo of executed operation will do actual
            # job we only need to move primary node one step down.
            macro.node_for_path(self.m_next_path).selected = True
            macro.node_for_path(self.m_prev_path).selected = False
        macro.refresh_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Reverse(self):
        macro = replay.Macro()
        # Undo of executed operation will revert the modifications
        # so we only need to move primary node one step up
        macro.node_for_path(self.m_prev_path).selected = True
        macro.node_for_path(self.m_next_path).selected = False

        macro.refresh_view()
        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)


lx.bless(CommandClass, 'replay.step')
