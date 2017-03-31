# python

import lx, lxifc, modo, replay
import pyperclip

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):

        lxm = pyperclip.paste()
        
        if len(lxm.strip()) == 0:
            return

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoPast(lxm))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        
        return True

class UndoPast(lxifc.Undo):
    def __init__(self, lxm):
        self.m_lxm = lxm
        self.m_added_nodes = list()

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()
        
        if macro.primary is None:
            path = [0]
        else:
            path = macro.primary.path
            path[-1] += 1
        
        self.m_added_nodes = macro.parse_and_insert_string(self.m_lxm, path)

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()
        
        for node in self.m_added_nodes:
            node.delete()

        self.finalize_command(macro)


lx.bless(CommandClass, 'replay.pastSelection')
