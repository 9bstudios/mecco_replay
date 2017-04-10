# python

import lx, lxifc, modo, replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

class CommandClass(replay.commander.CommanderClass):
    """Selects the first command or block node in the Macro."""
    
    def commander_arguments(self):
        return [
            {
                'name': 'path',
                'datatype': 'string',
                'default': '0',
                'flags':[]
            }, {
                'name': 'add',
                'label': "Add To Selection",
                'datatype': 'boolean',
                'default': 'false',
                'flags': ['optional']
            }
        ]
        
    def commander_execute(self, msg, flags):
    
        path = self.commander_args()['path']
        path = [int(idx) for idx in path.split(';')]
        add = self.commander_args()['add']
        
        macro = replay.Macro()
        
        if not add:
            macro.clear_selection()
    
        try:
            macro.node_for_path(path).selected = True
        except:
            pass
            
        macro.rebuild_view()
        macro.unsaved_changes = True

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)


lx.bless(CommandClass, 'replay.lineSelect')
