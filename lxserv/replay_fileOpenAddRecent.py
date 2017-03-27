# python

import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class CommandClass(replay.commander.CommanderClass):
    """Adds a file to the list of recently-opened macro files. Stored in a user
    value for persistence between sessions."""

    def commander_arguments(self):
        return [
               {
                   'name': 'path',
                   'datatype': 'string',
                   'flags': ['optional']
               }
           ]

    def remove_duplicates(self, seq):
        """Removes duplicate list items while maintaining list order."""
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x.lower() in seen or seen_add(x.lower()))]

    def commander_execute(self, msg, flags):
        path = self.commander_args()['path']

        existing_paths = lx.eval('user.value mecco_replay_recent_files ?')
        paths_list = existing_paths.split(';')

        paths = [path] + paths_list
        paths = self.remove_duplicates(paths)
        paths = paths[:10]

        paths_concat = ';'.join(paths)

        lx.eval('user.value mecco_replay_recent_files {%s}' % paths_concat)


lx.bless(CommandClass, 'replay.fileOpenAddRecent')
