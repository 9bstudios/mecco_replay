# python

import lx, modo, replay, os

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Lists recently-opened macro files stored in a custom user value."""

    def commander_arguments(self):
        return [
            {
                'name': 'query',
                'label': 'Open Recent',
                'datatype': 'string',
                'values_list_type': 'popup',
                'values_list': self.list_commands,
                'flags': ['query']
            }
        ]

    def commander_notifiers(self):
        return [("replay.notifier", "")]

    def commander_execute(self, msg, flags):
        path = self.commander_args()['query']
        lx.eval('replay.fileOpen {%s}' % path)

    def list_commands(self):
        existing_paths = lx.eval('user.value mecco_replay_recent_files ?')

        if not existing_paths:
            return []

        paths_list = existing_paths.split(';')
        paths_list = [n for n in paths_list if n]

        commands_list = []
        for path in paths_list:
            commands_list.append((path, os.path.basename(path)))

        return commands_list



lx.bless(CommandClass, 'replay.fileOpenRecentPop')
