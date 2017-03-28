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

        if len(cache.commands) == 1:
            macro.add_command(command = cache.commands[0], index = idx)

        if len(cache.commands) > 1:
            macro.add_block(block = cache.commands, name = "", index = idx)

        macro.unsaved_changes = True
        idx += 1

        macro.select(idx - 1)

        macro.rebuild_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_QUIET


lx.bless(LastBlockInsertClass, 'replay.lastBlockInsert')
