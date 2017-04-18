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
        
        macro = replay.Macro()
        if macro.primary is None:
            path = [0]
            old_primary = None
        else:
            path = list(macro.primary.path)
            old_primary = list(path)
            path[-1] += 1
            
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            paste = UndoPaste(lxm, path, old_primary)
            try:
                paste.undo_Forward()
            except:
                return
            undo_svc.Record(paste)

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if replay.Macro().primary is not None and not replay.Macro().primary.can_insert_after():
            return False

        return True

class UndoPaste(lxifc.Undo):
    def __init__(self, lxm, path, old_primary):
        self.m_lxm = lxm
        self.m_path = path
        self.m_old_primary_path = old_primary
        self.m_added_nodes = list()

    def finalize_command(self):
        """Does common command finalizing operations"""
        macro = replay.Macro()
        macro.rebuild_view()
        macro.unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()

        self.m_added_nodes = macro.parse_and_insert_string(self.m_lxm, list(self.m_path))
        macro.select(self.m_path)

        self.finalize_command()

    def undo_Reverse(self):
        for node in self.m_added_nodes:
            node.delete()
        
        macro = replay.Macro()        
        macro.select(self.m_old_primary_path)

        self.finalize_command()


lx.bless(CommandClass, 'replay.clipboardPaste')
