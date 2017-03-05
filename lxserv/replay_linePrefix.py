import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

PREFIXES = [
    ('',   'None'),
    ('!',  '!  Suppress dialogs.'),
    ('!!', '!! Suppress all dialogs.'),
    ('+',  '+  Show dialogs.'),
    ('++', '++ Show all dialogs.'),
    ('?',  '?  Show command dialog.')
]

class CommandClass(replay.commander.CommanderClass):
    """Sets the prefix for the currently selected command(s) to one of the standard
    dialog prefixes:

        `'!'`   - Suppress dialogs.
        `'!!'`  - Suppress all dialogs.
        `'+'`   - Show dialogs.
        `'++'`  - Show all dialogs.
        `'?'`   - Show command dialog.

    See http://sdk.luxology.com/wiki/Command_System:_Executing#Special_Prefixes"""

    def commander_arguments(self):
        return [
            {
                'name': 'command_prefix',
                'datatype': 'string',
                'default': prefixes[0][0],
                'values_list_type': 'popup',
                'values_list': PREFIXES,
                'flags': ['optional']
            }
        ]

    def commander_execute(self, msg, flags):
        prefix = self.commander_arg_value(0, '')

        for command in replay.Macro().selected_descendants:
            command.prefix = prefix

        replay.Macro().refresh()

lx.bless(CommandClass, 'replay.linePrefix')
