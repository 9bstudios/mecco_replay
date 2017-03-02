import lx, modo, replay_commander, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class RecordCommandClass(replay_commander.CommanderClass):
    """Start or stop Macro recording. The `mode` argument starts recording when
    `True` (or empty), stops recording when `False`, and toggles recording when queried.

    When recording stops, the resulting file will be saved to a temporary location
    inside the kit directory, then read and parsed using the `ReplayMacro().parse_LXM()`
    method. The user will then be prompted to save the file using `replay.fileSave`."""

    def commander_arguments(self):
        return [
            {
                'name': 'mode',
                'datatype': 'boolean',
                'default': True,
                'flags': ['query', 'optional']
            }
        ]

    def commander_execute(self, msg, flags):
        pass


lx.bless(RecordCommandClass, 'replay.record')
