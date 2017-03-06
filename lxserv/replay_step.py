import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Fires the next step in the macro, allowing you to fire each frame in a Macro
    one-by-one."""
    def commander_execute(self, msg, flags):
        replay.Macro().run_next_line()
        replay.Macro().refresh_view()


lx.bless(CommandClass, 'replay.step')
