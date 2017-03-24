import lx, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):

    """Close the current `Macro()` and, if necessary, prompt user to save changes."""
    def commander_execute(self, msg, flags):
        # Stop recording
        lx.eval('replay.record stop')

        macro = replay.Macro()

        # Hack to fix crash bug.
        macro.select_event_treeview()

        if not macro.file_path:
            return

        if not macro.unsaved_changes:
            return

        if modo.dialogs.yesNo(message("MECCO_REPLAY", "REVERT_DIALOG_TITLE"), message("MECCO_REPLAY", "REVERT_FILE_MSG")) == 'yes':

            # No unsaved changes
            macro.unsaved_changes = False

            # Clear current data
            macro.clear()

            # Reload saved data
            macro.parse(macro.file_path)

            # Rebuild treeview
            macro.rebuild_view()

            notifier = replay.Notifier()
            notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def basic_Enable(self, msg):
        if replay.Macro().file_path and replay.Macro().unsaved_changes:
            return True
        return False

lx.bless(CommandClass, 'replay.fileRevert')
