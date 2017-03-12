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

class UndoLineColor(lxifc.Undo):
    def __init__(self):
        self.m_prev_index = -1
        self.m_next_index = -1

    def undo_Forward(self):
        macro = replay.Macro()
        lx.out("sel = ", [x.index for x in macro.selected_descendants])
        lx.out("prim = ", macro.primary.index)
        self.m_prev_index, self.m_next_index = macro.run_next_line()
        macro.refresh_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)
    
    def undo_Reverse(self):
        macro = replay.Macro()
        macro.children[self.m_prev_index].selected = True
        macro.children[self.m_next_index].selected = False

        macro.refresh_view()
        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

        lx.out("sel_af = ", [x.index for x in macro.selected_descendants])
        lx.out("prim_af = ", macro.primary.index)

lx.bless(CommandClass, 'replay.step')
