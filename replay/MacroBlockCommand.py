# python

import lx
import lxifc
import re
import json
import lumberjack
from MacroCommandArg import MacroCommandArg
from MacroBaseCommand import MacroBaseCommand
from MacroCommand import MacroCommand


class MacroBlockCommand(MacroBaseCommand):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts. Note that if the `command`
    property is `None`, the `comment_before` property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)"""

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # Create default command value object and set formatting
        self.columns['command'] = lumberjack.TreeValue()
        self.columns['command'].display_value = ''
        self.columns['command'].input_region = None

        self.columns['enable'].input_region = 'MacroCommandEnable'
        self.columns['prefix'].input_region = 'MacroCommandPrefix'
        self.columns['name'].input_region = 'MacroCommandBlock'

        self.original_name = kwargs.get('name', "")

        if kwargs.get('block_json'):
            self.parse_json(kwargs.get('block_json'), **kwargs)
        elif kwargs.get('block'):
            self.add_commands(**kwargs)

    def add_commands(self, **kwargs):
        idx = 0
        for cmd in kwargs.get('block'):
            self.children.append(MacroCommand(parent=self, command = cmd, index = idx))
            idx = idx + 1

    def block_name():
        def fget(self):
            name = self.columns.get('name')
            if name:
                return name.value
            else:
                return None
        def fset(self, value):
            self.columns['name'].value = value

        return locals()

    block_name = property(**block_name())

    def original_name():
        def fget(self):
            return self._original_name
        def fset(self, value):
            self._original_name = value
            self.block_name = "Block: " + value

        return locals()

    original_name = property(**original_name())

    def render_LXM_Python(self, renderName):
        """Construct MODO command string from stored internal parts. Also adds comments"""
        res = self.render_comments()
        if self.direct_suppress:
            res.append("# replay suppress:")
        res.append(("# " if self.direct_suppress else "") + "# Command Block Begin: %s" % self.original_name)

        for command in self.children:
            render = getattr(command, renderName)
            assert(render != None)
            lines = render()
            for line in lines:
                res.append(("# " if self.direct_suppress else "") + ' '*4 + line)

        res.append(("# " if self.direct_suppress else "") + "# Command Block End: %s" % self.original_name)
        return res
        
    def render_LXM_if_selected(self):
        if self.selected:
            return self.render_LXM()
        else:
            res = []
            for command in self.children:
                lines = command.render_LXM_if_selected()
                for line in lines:
                    res.append(("# " if self.direct_suppress else "") + line)
                    
            return res

    def render_LXM(self):
        return self.render_LXM_Python('render_LXM')

    def render_Python(self):
        return self.render_LXM_Python('render_Python')

    def render_json(self):
        """Construct MODO command string in json format for each nested command."""
        commands = list()
        for command in self.children:
            command = command.render_json()
            commands.append(command)

        return {"command block" : {"name" : self.original_name, "suppress": self.direct_suppress, "comment" : self.comment_before, "commands": commands}}

    def parse_json(self, json_struct, **kwargs):
        attributes = json_struct['command block']
        self.original_name = attributes['name']
        self.direct_suppress = attributes['suppress']
        self.comment_before = attributes['comment']

        kwargs.pop('block', None)
        kwargs.pop('command_json', None)
        kwargs.pop('block_json', None)

        index = 0
        for command in attributes['commands']:
            kwargs['index'] = index
            kwargs['parent'] = self
            if 'command' in command:
                self._controller.add_child(command_json = command, **kwargs)
            else:
                self._controller.add_child(block = [], block_json = command, **kwargs)
            index += 1

    def run(self):
        """Runs the command."""

        if self.suppress:
            return

        for command in self.children:
            command.run()
