# python

import lx, lxifc, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Deletes the currently-selected command from the `Macro()` object."""
    def commander_execute(self, msg, flags):
    
        macro = replay.Macro()

        # collect list of selected paths
        paths = list()
        for line in macro.selected_descendants:
            paths.append(line.path)

        target = macro.primary
                    
        if target is None:
            return
                    
        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoToBlock(paths, target.path, ""))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if len(replay.Macro().selected_descendants) == 0:
            return False

        for command in replay.Macro().selected_descendants:
            if not command.can_add_to_block():
                return False

        return True

class UndoToBlock(lxifc.Undo):
    def __init__(self, paths, target_path, name):
        self.m_paths = paths
        self.m_paths.sort()
        self.m_target_path = target_path
        self.m_name = name
        
    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()
        
        nodes = list()
        # Collectiong nodes since paths will be invalidated during move
        for path in self.m_paths:
            nodes.append(macro.node_for_path(path))
            
        target_node = macro.add_block(name = self.m_name, comment=[], meta = [], suppress=False, path = self.m_target_path)
        
        # Storing new paths after creating target_node for undo
        del self.m_paths[:]
        for node in nodes:
            self.m_paths.append(node.path)
            
        idx = 0
        for node in nodes:
            node.path = target_node.path + [idx]
            idx += 1
            
        self.m_target_path = target_node.path

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()
        
        target_node = macro.node_for_path(self.m_target_path)
        
        nodes = list()
        
        # Each move will validate next index
        for path in self.m_paths:
            child = target_node.children[0]
            nodes.append(child)
            child.path = path
            
        self.m_target_path = target_node.path
        target_node.delete()
        
        # Restoring initial paths for redo
        del self.m_paths[:]
        for node in nodes:
            self.m_paths.append(node.path)

        self.finalize_command(macro)


lx.bless(CommandClass, 'replay.selToBlock')
