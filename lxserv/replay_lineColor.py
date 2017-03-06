import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Sets the row color for the currently-selected macro command(s)."""
    def commander_arguments(self):
        return [
            {
                'name': 'color_name',
                'datatype': 'string',
                'default': 'none',
                'values_list_type': 'popup',
                'values_list': [
                    'none',
                    'red',
                    'magenta',
                    'pink',
                    'brown',
                    'orange',
                    'yellow',
                    'green',
                    'light_g',
                    'cyan',
                    'blue',
                    'light_blue',
                    'ultrama',
                    'purple',
                    'light_pu',
                    'dark_grey',
                    'grey',
                    'white'
                ]
            }
        ]

    def commander_execute(self, msg, flags):
        color_name = self.commander_arg_value(0, 'none')

        for line in replay.Macro().selected_descendants:
            line.row_color = color_name

        replay.Macro().refresh_view()

lx.bless(CommandClass, 'replay.lineColor')
