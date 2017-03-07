import lx, modo, replay
import replay.commander as commander

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Throws up a `replay.chameleon` dialog requesting all of the necessary values
    to edit a given command in the `Macro().commands` list."""
    def commander_execute(self, msg, flags):
        primary_node = replay.Macro().primary
        args = primary_node.args

        replay.Chameleon().arguments = []

        for arg in args:

            default = arg.value
            datatype = 'string'

            if arg.argTypeName in commander.DATATYPES:
                datatype = arg.argTypeName
            elif arg.argType == 1:
                datatype = 'integer'
            elif arg.argType == 2:
                datatype = 'float'

            replay.Chameleon().arguments.append({
                'name': arg.argName,
                'datatype': datatype,
                'default': default,
                'flags': ['optional']
            })


        lx.eval('?replay.chameleon')

        for arg in args:
            arg.value = replay.Chameleon().results.get(arg.argName)

        replay.Macro().refresh_view()

lx.bless(CommandClass, 'replay.lineEdit')
