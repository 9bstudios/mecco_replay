import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Inserts a comment-only command object into the `Macro().commands` list."""

    def commander_arguments(self):
        return [
            {
                'name': 'comment',
                'datatype': 'string'
            }
        ]

    def commander_execute(self, msg, flags):
        comment = self.commander_arg_value(0)
        macro = replay.Macro()

        try:
            macro.insert_comment_before_current_command(comment)
        except Exception as e:
            modo.dialogs.alert("Warning", str(e), dtype='warning')
            return

        macro.rebuild_view()

lx.bless(CommandClass, 'replay.insertComment')
