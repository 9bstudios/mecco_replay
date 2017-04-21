# python

import lx, lxifc, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

PREFIXES = [
    ('',   message("MECCO_REPLAY", "PREFIX_NONE")),
    ('!',  message("MECCO_REPLAY", "PREFIX_SUPPRESS_DIALOGS")),
    ('!!', message("MECCO_REPLAY", "PREFIX_SUPPRESS_ALL_DIALOGS")),
    ('+',  message("MECCO_REPLAY", "PREFIX_SHOW_DIALOGS")),
    ('++', message("MECCO_REPLAY", "PREFIX_SHOW_ALL_DIALOGS")),
    ('q',  message("MECCO_REPLAY", "PREFIX_SHOW_COMMAND_DIALOG"))
]

class CommandClass(replay.commander.CommanderClass):
    """Sets the prefix for the currently selected command(s) to one of the standard
    dialog prefixes:

        `'!'`   - Suppress dialogs.
        `'!!'`  - Suppress all dialogs.
        `'+'`   - Show dialogs.
        `'++'`  - Show all dialogs.
        `'?'`   - Show command dialog.

    NOTE: Since commands cannot accept `?` as an argument, use `q` for `?`.

    See http://sdk.luxology.com/wiki/Command_System:_Executing#Special_Prefixes"""

    def commander_arguments(self):
        return [
            {
                'name': 'command_prefix',
                'datatype': 'string',
                'default': PREFIXES[0][0],
                'values_list_type': 'popup',
                'values_list': PREFIXES,
                'flags': ['optional']
            }
        ]

    def commander_execute(self, msg, flags):
        prefix = self.commander_arg_value(0, '')

        # Since ? is reserved for queries in MODO, we use the letter q as a sub.
        prefix = "?" if prefix == 'q' else prefix

        # Add actions needed to undo and redo this command
        actionList = PrefixActionList()
        for line in replay.Macro().selected_descendants:
            actionList.append(line.path, line.prefix, prefix)

        # Register Undo object performing operation and apply it
        undo_svc = lx.service.Undo()
        if undo_svc.State() != lx.symbol.iUNDO_INVALID:
            undo_svc.Apply(UndoLinePrefix(actionList))

    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        return bool(replay.Macro().selected_descendants)

class PrefixActionList:
    def __init__(self):
        self.m_actions = list()

    def append(self, path, prev_prefix, new_prefix):
        """Add action in action list"""
        self.m_actions.append((path, prev_prefix, new_prefix))

    def iter_redo(self):
        """iterate actions for redo"""
        for path, prev_prefix, new_prefix in self.m_actions:
            yield (path, new_prefix)

    def iter_undo(self):
        """iterate actions for undo"""
        for path, prev_prefix, new_prefix in self.m_actions:
            yield (path, prev_prefix)

class UndoLinePrefix(lxifc.Undo):
    def __init__(self, actionList):
        self.m_actionList = actionList

    def apply(self, actions):
        """Change prefix for each item in actions"""
        macro = replay.Macro()

        # Change prefix of selected nodes
        for path, prefix in actions:
            macro.node_for_path(path).prefix = prefix

        # Rebuild view
        macro.rebuild_view()
        replay.Macro().unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

    def undo_Forward(self):
        self.apply(self.m_actionList.iter_redo())

    def undo_Reverse(self):
        self.apply(self.m_actionList.iter_undo())


lx.bless(CommandClass, 'replay.linePrefix')
