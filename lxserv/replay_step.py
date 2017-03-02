import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay_commander.CommanderClass):
    """TODO: Fires the next step in the macro, allowing you to fire each frame in a Macro
    one-by-one."""
    def commander_execute(self, msg, flags):
        pass


# lx.bless(CommandClass, 'replay.step')
