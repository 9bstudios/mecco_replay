# python

import lx, modo, replay, os, traceback

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

def is_valid_script(path):
    if os.path.isfile(path) and os.path.splitext(path)[1].lower() in ['.py', '.lxm', '.pl']:
        return True
    return False


class CommandClass(replay.commander.CommanderClass):
    """Lists recently-opened macro files stored in a custom user value."""

    def commander_arguments(self):
        return [
            {
                'name': 'path',
                'datatype': 'string'
            }, {
                'name': 'query',
                'label': self.label,
                'datatype': 'string',
                'values_list_type': 'popup',
                'values_list': self.list_scripts,
                'flags': ['query']
            }
        ]

    def commander_notifiers(self):
        return [("replay.notifier", "")]

    def commander_execute(self, msg, flags):
        path = self.commander_arg_value(1)
        try:
            lx.eval('@{%s}' % path)
        except:
            traceback.print_exc()

    def list_scripts(self):
        path = lx.eval('query platformservice alias ? {%s}' % self.commander_arg_value(0))

        commands_list = []
        for sub in [f for f in os.listdir(path) if is_valid_script(os.path.join(path, f))]:
            commands_list.append((os.path.join(path, sub), os.path.basename(sub)))

        return commands_list

    def label(self):
        return "Run from " + os.path.basename(lx.eval('query platformservice alias ? {%s}' % self.commander_arg_value(0)))


lx.bless(CommandClass, 'replay.fileRunFromFolderPop')
