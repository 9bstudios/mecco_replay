# python

import lx
import re
import lumberjack

class MacroBaseCommand(lumberjack.TreeNode):
    """Common part of MacroCommand and MacroBlockCommand"""

    _suppress = False
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
        # self.columns['name'].icon_resource = 'uiicon_replay.suppress'

        if kwargs.get('suppress') != None:
            self.direct_suppress = kwargs.get('suppress')

        self.user_comment_before = []
        if bool(kwargs.get('comment')):
            self.user_comment_before = kwargs.get('comment')

    def draggable(self):
        return True

    def canEval(self):
        return not self.suppress

    def canAcceptDrop(self, source_nodes):
        return True

    def can_change_suppress(self):
        if hasattr(self.parent, 'suppress'):
            return not self.parent.suppress
        else:
            return True

    def update_suppress_for_node_and_descendants(self):
        if hasattr(self, 'suppress'):
            if not self.suppress:
                # If not suppressed, display a checkmark and store True
                self.columns['enable'].value = True
                self.columns['enable'].display_value = ''
                # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
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
        doc = "Boolean. True if command suppressed directly not by suppressing block."
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
        doc = "Boolean. Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            if hasattr(self.parent, 'suppress'):
                return self._suppress or self.parent.suppress
            return self._suppress

        return locals()

    suppress = property(**suppress())

    def parse_meta(self, line):
        meta = re.search(r'^\# replay\s+(\S+):(.+)$', line)
        if meta is not None:
            return (meta.group(1), meta.group(2))
        else:
            return None

    def render_meta(self, name, val):
        return "# replay {n}:{v}".format(n=name, v=val)

    def comment_before():
        doc = """String to be added as comment text before the command. Long strings
        will automatically be broken into lines of 80 characters or less. Appropriate
        comment syntax will be rendered at export time. Include only the raw string."""
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
        doc = """String to be added as comment text before the command. Long strings
        will automatically be broken into lines of 80 characters or less. Appropriate
        comment syntax will be rendered at export time. Include only the raw string."""
        def fget(self):
            return self._user_comment_before
        def fset(self, value):
            self._user_comment_before = value
        return locals()

    user_comment_before = property(**user_comment_before())
