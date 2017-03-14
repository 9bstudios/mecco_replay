import lx, modo, replay, os

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Insetrs one or many lines after primary node."""

    def commander_arguments(self):   
        return [
            {
                'name': 'c',
                'datatype': 'string',
                'default': '',
                'flags': ['optional']
            }
        ]

    def commander_execute(self, msg, flags):
        # Get script
        script = self.commander_arg_value(0)
        
        macro = replay.Macro()
        
        idx = -1
        if macro.primary is None:
            # If there's no primary node, insert at zero
            idx = len(macro.children)
        else:
            # If there's a primary node, insert right after it
            idx = macro.primary.index + 1
        
        for line in script.split('\n'):
            macro.add_command(command_string = [(line + "\n")], index = idx)
            idx += 1
            
        macro.select(idx - 1)
            
        macro.rebuild_view()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

lx.bless(CommandClass, 'replay.lineInsert')
