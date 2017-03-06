import lx, modo, replay
from replay import commander

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class FCLClass(commander.CommanderClass):
    """Renders a Form Command List (FCL) that is rendered in the MODO modes tail."""

    def commander_arguments(self):
        return [
            {
                'name': 'query',
                'datatype': 'boolean',
                'values_list_type': 'fcl',
                'values_list': self.list_commands
            }
        ]

    def list_commands(self):
        """Returns a list of commands to append to the MODO modes tail (see
        forms_userFCL.cfg). Must return a list of _valid_ MODO commands. If any
        command is invalid, MODO will crash.

        Retrieves a list stored by `replay.AddToModesTail` below."""
        return ['noop']

lx.bless(FCLClass, 'replay.ModesTailFCL')


class CommandClass(commander.CommanderClass):
    """Appends an FCL in the modes tail with the supplied command."""

    # def commander_arguments(self):
    #     return [
    #         {
    #             'name': 'command',
    #             'datatype': 'string'
    #         }
    #     ]

    def commander_execute(self, msg, flags):
        modo.dialogs.alert("Not Implemented.", "Command not yet implemented.")

    def append_to_fcl(self):
        # appends a list of commands that is available to FCLClass.list_commands(),
        # and is also stored between sessions (probably using user values)
        pass

    def basic_Enable(self, msg):
        return False


lx.bless(CommandClass, 'replay.addToModesTail')
