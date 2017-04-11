# python

import lx, modo, replay, os

class LastBlockInsertClass(replay.commander.CommanderClass):
    """Insetrs commands from RecordingCache into Macro as single block."""

    def commander_arguments(self):
        return []

    def commander_execute(self, msg, flags):

        macro = replay.Macro()

        idx = -1
        if macro.primary is None:
            # If there's no primary node, insert at zero
            idx = len(macro.children)
        else:
            # If there's a primary node, insert right after it
            idx = macro.primary.index + 1

        cache = replay.RecordingCache()

        if len(cache.commands) == 0:
            return

        lx.out("cache = ", cache.commands)
        self.count = 0
        if len(cache.commands) == 1 and not cache.commands[0].is_block():
            macro.add_command(command = cache.commands[0].command, index = idx)
        else:
            self.insert_root(cache.root, macro.root, idx)            

        macro.unsaved_changes = True
        idx += 1

        macro.select(idx - 1)

        macro.rebuild_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)
        
    def insert_root(self, root, rootNode, index):
        macro = replay.Macro()
        lx.out("root = ", root)
        if self.count == 5:
            return
        else:
            self.count += 1
        if root.is_block():
            block = macro.add_block(block = [], name = "", parent = rootNode, index = index)
            index = 0
            for command in root.children:
                self.insert_root(command, block, index)
                index += 1
        else:
            macro.add_command(command = root.command, parent = rootNode, index = index)
       
    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_QUIET


lx.bless(LastBlockInsertClass, 'replay.lastBlockInsert')
