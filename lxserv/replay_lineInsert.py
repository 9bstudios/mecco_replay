# python

import lx, lxifc, modo, replay, os

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class LineInsertClass(replay.commander.CommanderClass):
    """Insetrs one or many lines after primary node."""

    def commander_arguments(self):
        return [
            {
                'name': 'command',
                'datatype': 'string',
                'default': '',
                'values_list': self.list_commands,
                'values_list_type': self.values_list_type,
                'flags':['query']
            }, {
                'name': 'ButtonName',
                'datatype': 'string',
                'flags':['optional', 'hidden']
            }
        ]
        
    def values_list_type(self):
        return 'sPresetText'

    def list_commands(self):
        return lx.eval('query commandservice commands ?')
        
    def cmd_Flags(self):
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_UNDO

    def commander_execute(self, msg, flags):
        # Get script
        script = self.commander_arg_value(0).replace("\q","?")
        ButtonName = self.commander_arg_value(1)

        macro = replay.Macro()

        path = None
        if macro.primary is None:
            # If there's no primary node, insert at end
            path = macro.root.path + [len(macro.children)]
        else:
            # If there's a primary node, insert right after it
            path = macro.primary.path
            while not macro.node_for_path(path).can_insert_after():
                path = path[:-1]
            path[-1] += 1
            
        lineInsert = UndoLineInsert(script, ButtonName, path)
        
        if self.cmd_Flags() & lx.symbol.fCMD_UNDO != 0:
            # Register Undo object performing operation and apply it
            undo_svc = lx.service.Undo()
            if undo_svc.State() != lx.symbol.iUNDO_INVALID:
                undo_svc.Apply(lineInsert)
        else:
            lineInsert.undo_Forward()
        
    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False

        if replay.Macro().primary is not None and not replay.Macro().primary.can_insert_after():
            return False
            
        return True

class LineInsertSpecialClass(LineInsertClass):
    """Same as `replay.lineInsert`, except it isn't undoable and doesn't show up
    in macros and command history. Used for adding lines during recording."""

    def list_commands(self):
        return [
            ('scene.load', 'Open...'),
            ('scene.save', 'Save'),
            ('scene.save rename', 'Save As...'),
            ('scene.save export', 'Export...'),
            ('preset.do', 'Preset Do'),
        ]
        
    def values_list_type(self):
        return 'popup'
        
    def basic_Enable(self, msg):
        return True

class LineInsertQuietClass(LineInsertClass):
    """Same as `replay.lineInsert`, except it isn't undoable and doesn't show up
    in macros and command history. Used for adding lines during recording."""

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_QUIET
        
    def basic_Enable(self, msg):
        return True

class UndoLineInsert(lxifc.Undo):
    def __init__(self, script, buttonName, path):
        self.m_script = script
        self.m_buttonName = buttonName
        self.m_path = path
        self.m_added_commands = []
        self.m_selection = []
        self.m_primary = None

    def finalize_command(self, macro):
        """Does common command finalizing operations"""
        macro.rebuild_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        macro = replay.Macro()
        
        del self.m_added_commands[:]
            
        path = list(self.m_path)
        for line in self.m_script.split('\n'):
            self.m_added_commands.append(macro.add_command(command = line, path = path, ButtonName = self.m_buttonName))
            macro.unsaved_changes = True
            path[-1] += 1
            
        self.m_selection = macro.root.selected_descendants
        
        self.m_primary = macro.primary

        path[-1] -= 1
        macro.select(path)

        self.finalize_command(macro)

    def undo_Reverse(self):
        macro = replay.Macro()

        for command in self.m_added_commands:
            command.delete()
            
        macro.root.deselect_descendants()

        for command in self.m_selection:
            command.selected = True
            
        if self.m_primary is not None:
            self.m_primary.selected = True
        
        macro.unsaved_changes = True

        self.finalize_command(macro)

lx.bless(LineInsertClass, 'replay.lineInsert')
lx.bless(LineInsertSpecialClass, 'replay.lineInsertSpecial')
lx.bless(LineInsertQuietClass, 'replay.lineInsertQuiet')
