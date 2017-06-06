# python
'''
The MacroBaseCommand contains the MacroBaseCommand class, which is an abstract
class used to control rendering and display properties of commands
'''
import lx
import re
import json
import lumberjack

class MacroBaseCommand(lumberjack.TreeNode):
    '''
    Abstract class inherited by MacroCommand and MacroBlockCommand

    Args:
        \**kwargs: varkwargs

    Returns:
        MacroBaseCommand
    '''
    _suppress = False
    _temporary = False
    _user_comment_before = []

    def __init__(self, **kwargs):
        super(MacroBaseCommand, self).__init__(**kwargs)

        self._user_comment_before = []

        # Create default enable value object and set formatting
        self.columns['enable'] = lumberjack.TreeValue()
        # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
        self.columns['enable'].display_value = ''
        self.columns['enable'].color.special_by_name('gray')

        # Create default dialogs value object and set formatting
        self.columns['prefix'] = lumberjack.TreeValue()

        # Create default name value object
        self.columns['name'] = lumberjack.TreeValue()
        if kwargs['temporary']:
            self.columns['name'].font.set_italic()
            self.columns['name'].color.special_by_name('gray')
            
        self._temporary = kwargs['temporary']

        # self.columns['name'].icon_resource = 'uiicon_replay.suppress'

        if kwargs.get('suppress') != None:
            self.direct_suppress = kwargs.get('suppress')

        self.user_comment_before = []
        if bool(kwargs.get('comment')):
            self.user_comment_before = kwargs.get('comment')

    def draggable(self):
        '''
        Whether this command is draggable in the UI

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def canEval(self):
        '''
        Whether this command can be evaluated

        Args:
            None

        Returns:
            bool: opposite of suppress
        '''
        return not self.suppress

    def canAcceptDrop(self, source_nodes):
        '''
        Whether this command accepts drag'n'drop actions

        Args:
            source_nodes (list): sources nodes to be tested

        Returns:
            bool: True
        '''
        return True

    def tooltip(self, columnIndex):
        '''
        Whether this command is draggable in the UI

        Args:
            columnIndex (int): an argument that does nothing

        Returns:
            str: command tooltip
        '''
        return '\n'.join(self.user_comment_before)

    def can_change_suppress(self):
        '''
        Whether the supression of the command can be changed

        Args:
            None

        Returns:
            bool: supression changeability
        '''
        if hasattr(self.parent, 'suppress'):
            return not self.parent.suppress
        else:
            return True

    def can_change_color(self):
        '''
        Whether the command UI can change color

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def can_add_command(self):
        '''
        Whether the command can be added

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def can_add_to_block(self):
        '''
        Whether the command can be added to a block

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def can_copy(self):
        '''
        Whether the command can be copied

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def can_insert_after(self):
        '''
        Whether the command UI can be inserted after

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def can_delete(self):
        '''
        Whether the command can be deleted

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def can_change_name(self):
        '''
        Whether the command name can be changed

        Args:
            None

        Returns:
            bool: True
        '''
        return True

    def update_suppress_for_node_and_descendants(self):
        '''
        Updates supression status for node and its children

        Args:
            None

        Returns:
            None
        '''
        if hasattr(self, 'suppress'):
            if not self.suppress:
                # If not suppressed, display a checkmark and store True
                self.columns['enable'].value = True
                self.columns['enable'].display_value = ''
                # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
                if not self._temporary:
                    self.columns['name'].color.special_by_name('default')
                    self.columns['prefix'].color.special_by_name('default')
            elif self.suppress:
                # If it is suppressed, display nothing and store False
                self.columns['enable'].value = False
                self.columns['enable'].display_value = '#'
                # self.columns['enable'].icon_resource = None
                self.columns['name'].color.special_by_name('gray')
                self.columns['prefix'].color.special_by_name('gray')

        for child in self.children:
            if hasattr(child, 'suppress'):
                child.update_suppress_for_node_and_descendants()

    def direct_suppress():
        doc = '''
        bool: True if command suppressed directly not by suppressing block.
        Gets and sets whether a command is directly suppressed (not by
        supressing block)
        '''
        def fget(self):
            return self._suppress

        def fset(self, is_suppressed):
            # Set the internal _suppress value. This value is used when we do things
            # like render to LXM, etc.
            self._suppress = is_suppressed

            # Set the `enable` column display. This is purely visual.
            self.update_suppress_for_node_and_descendants()

        return locals()

    direct_suppress = property(**direct_suppress())

    def suppress():
        doc = '''
        bool: supression state
        Gets and sets whether a command is directly suppressed (not by supressing block)
        Suppresses (comments) the command by appending a "#" before it.
        '''
        def fget(self):
            if hasattr(self.parent, 'suppress'):
                return self._suppress or self.parent.suppress
            return self._suppress

        return locals()

    suppress = property(**suppress())

    def parse_meta(self, line):
        '''
        Parse line of metadata

        Args:
            line: (str): metadata line

        Returns:
            tuple: name, value
        '''
        meta = re.search(r'^replay\s+(\S+):(.+)$', line)
        if meta is not None:
            return (meta.group(1), json.loads(meta.group(2)))
        else:
            return None

    def render_meta(self, name, val):
        '''
        Renders a line of metadata

        Args:
            name (str): name of metadata
            val (dict): metadata object to be dumped to json

        Returns:
            str: metadata line
        '''
        return "replay {n}:{v}".format(n=name, v=json.dumps(val))

    def render_comments(self):
        '''
        Renders comments

        Args:
            None

        Returns:
            list: commented lines
        '''
        res = []
        for comment in self.comment_before:
            res.append("# " + comment)
        return res

    def comment_before():
        doc = '''
        dict: local context
        Gets and sets comment before the command.

        Long strings will automatically be broken into lines of 80 characters or
        less. Appropriate comment syntax will be rendered at export time.
        Include only the raw string.
        '''
        def fget(self):
            res = list(self._user_comment_before)
            for key, val in self.meta.iteritems():
                if val != None:
                    res.append(self.render_meta(key, val))
            return res
        def fset(self, value):
            del self._user_comment_before[:]
            for line in value:
                meta = self.parse_meta(line)
                if meta is None:
                    self._user_comment_before.append(line)
                else:
                    (name, val) = meta
                    self.meta[name] = val
        return locals()

    comment_before = property(**comment_before())

    def user_comment_before():
        doc = '''
        dict: local context
        Gets and sets user comment before the command.
        '''
        def fget(self):
            return self._user_comment_before
        def fset(self, value):
            self._user_comment_before = value
        return locals()

    user_comment_before = property(**user_comment_before())
