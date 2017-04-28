# python
'''
The MacroBlockCommand module contains the MacroBlockCommand class, which is used
for encapsulating multiple commands as though they were one
'''
import lx
import lxifc
import re
import json
import lumberjack
from MacroCommandArg import MacroCommandArg
from MacroBaseCommand import MacroBaseCommand
from MacroCommand import MacroCommand


class MacroBlockCommand(MacroBaseCommand):
    '''
    Abstraction class for treating multiple commands as one

    Contains everything necessary to read, construct, write, and translate a
    modo command for use in macros or python scripts. Note that if the command
    property is None, the comment_before property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)

    Args:
        \**kwargs: varkwargs

    Returns:
        MacroBlockCommand
    '''
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # Create default command value object and set formatting
        self.columns['command'] = lumberjack.TreeValue()
        self.columns['command'].display_value = ''
        self.columns['command'].input_region = None

        self.columns['enable'].input_region = 'MacroCommandEnable'
        self.columns['name'].input_region = 'MacroCommandBlock'

        self.name = kwargs.get('name', "")

        if kwargs.get('block_json'):
            self.parse_json(kwargs.get('block_json'), **kwargs)
        elif kwargs.get('block'):
            self.add_commands(**kwargs)

    def add_commands(self, **kwargs):
        '''
        Add MacroCommands as children

        Args:
            \**kwargs: varkwargs

        Returns:
            locals???
        '''
        idx = 0
        for cmd in kwargs.get('block'):
            self.children.append(MacroCommand(parent=self, command = cmd, index = idx))
            idx = idx + 1

    def name():
        doc = '''
        Gets and sets name of block

        Args:
            None

        Returns:
            locals???
        '''
        def fget(self):
            return self.columns['name'].value
        def fset(self, value):
            self.columns['name'].value = value
            if not value:
                value = "\x03(c:4113)\x03(f:FONT_ITALIC)<untitled>"
            self.columns['name'].display_value = "Block: " + value
        return locals()

    name = property(**name())

    def render_LXM_Python(self, renderName):
        '''
        Construct modo command string from stored internal parts and adds comments

        Args:
            renderName (str): renderName attribute of command

        Returns:
            list: list of python lx.eval commands

        Raises:
            AssertionError
        '''
        res = self.render_comments()
        if self.direct_suppress:
            res.append("# replay suppress:")
        res.append(("# " if self.direct_suppress else "") + "# Command Block Begin: %s" % self.name)

        for command in self.children:
            render = getattr(command, renderName)
            assert(render != None)
            lines = render()
            for line in lines:
                if line.startswith('#'):
                    res.append(("# " if self.direct_suppress else "") + line)
                else:
                    res.append(("# " if self.direct_suppress else "") + ' '*4 + line)

        res.append(("# " if self.direct_suppress else "") + "# Command Block End: %s" % self.name)
        return res

    def render_LXM_if_selected(self):
        '''
        Render selected commands as LXM

        Args:
            None

        Returns:
            list: rendered commands
        '''
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
        '''
        Renders python with render_LXM renderName

        Args:
            None

        Returns:
            list: rendered python commands

        .. todo:
            - my guess is that this is a typo and should render lxm not python
        '''
        return self.render_LXM_Python('render_LXM')

    def render_Python(self):
        '''
        Renders python with render_Python renderName

        Args:
            None

        Returns:
            list: rendered python commands
        '''
        return self.render_LXM_Python('render_Python')

    def render_json(self):
        '''
        Construct modo command string in json format for each nested command.


        Args:
            None

        Returns:
            dict: command dict
        '''
        commands = list()
        for command in self.children:
            command = command.render_json()
            commands.append(command)

        return {"command block" : {"name" : self.name, "suppress": self.direct_suppress, "comment" : self.comment_before, "commands": commands}}

    def parse_json(self, json_struct, **kwargs):
        '''
        Parses json command structure

        Args:
            json_struct (dict): json command structure
            \**kwargs: varkwargs

        Returns:
            None

        .. todo::
            - method expects type, command_json, block_json and path to be in
              kwargs, so those should be declared explicitly
        '''
        attributes = json_struct['command block']
        self.name = attributes['name']
        self.direct_suppress = attributes['suppress']
        self.comment_before = attributes['comment']

        kwargs.pop('type', None)
        kwargs.pop('command_json', None)
        kwargs.pop('block_json', None)
        kwargs.pop('path', None)

        index = 0
        for command in attributes['commands']:
            kwargs['index'] = index
            kwargs['parent'] = self
            if 'command' in command:
                self._controller.add_command(command_json = command, **kwargs)
            else:
                self._controller.add_block(block_json = command, **kwargs)
            index += 1

    def run(self):
        '''
        Runs the command.

        Args:
            None

        Returns:
            None
        '''
        if self.suppress:
            return

        for command in self.children:
            command.run()
