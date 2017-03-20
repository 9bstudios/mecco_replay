# python

import lx
import lxifc
import re
import json
import lumberjack
from MacroCommandArg import MacroCommandArg
from MacroCommand import MacroCommand

class MacroBlockCommand(lumberjack.TreeNode):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts. Note that if the `command`
    property is `None`, the `comment_before` property will still be rendered, but
    the command will be ignored. (This way you can add comment-only lines.)"""

    _args = {}
    _suppress = False
    _user_comment_before = []

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        self._user_comment_before = []

        # Create default command value object and set formatting
        self.columns['command'] = lumberjack.TreeValue()
        self.columns['command'].display_value = ''
        self.columns['command'].input_region = None
        
        # Create default enable value object and set formatting
        self.columns['enable'] = lumberjack.TreeValue()
        # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
        self.columns['enable'].display_value = ''
        self.columns['enable'].input_region = 'MacroCommandEnable'
        self.columns['enable'].color.special_by_name('gray')

        # Create default dialogs value object and set formatting
        self.columns['prefix'] = lumberjack.TreeValue()
        self.columns['prefix'].input_region = 'MacroCommandPrefix'

        # Create default name value object
        self.columns['name'] = lumberjack.TreeValue()
        self.columns['name'].input_region = 'MacroCommandBlock'
        # self.columns['name'].icon_resource = 'uiicon_replay.suppress'

        if kwargs.get('suppress') != None:
            self.suppress = kwargs.get('suppress')

        # If a command string (it's actually a list of strings) has been passed in, parse it:
   # TODO DELETE
   #     if bool(kwargs.get('command_string')) and \
   #         all(isinstance(elem, basestring) for elem in kwargs.get('command_string')):
   #         self.parse_string(kwargs.get('command_string'))
   #     elif bool(kwargs.get('command_json')):
   #         self.parse_json(kwargs.get('command_json'))

  #  def command():
  #      doc = "The base MODO command, e.g. `item.name`."
  #      def fget(self):
  #          command = self.columns.get('command')
  #          if command:
  #              return command.value
  #          else:
  #              return None
  #      def fset(self, value):
  #          self.columns['command'].value = value
  #          self.retreive_args()
  #          self.columns['name'].value = self.command_meta()['username']
  #      return locals()

  #  command = property(**command())

  #  def args():
  #      doc = """The `MacroCommand` node's arguments, which should all be
  #      of class `MacroCommandArg`."""
  #      def fget(self):
  #          return self.children
  #      def fset(self, value):
  #          self.children = value
  #      return locals()

  #  args = property(**args())

    def suppress():
        doc = "Boolean. Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            return self._suppress
        def fset(self, is_suppressed):
            # Set the internal _suppress value. This value is used when we do things
            # like render to LXM, etc.
            self._suppress = is_suppressed

            # Set the `enable` column display. This is purely visual.

            if not is_suppressed:
                # If not suppressed, display a checkmark and store True
                self.columns['enable'].value = True
                self.columns['enable'].display_value = ''
                # self.columns['enable'].icon_resource = 'MIMG_CHECKMARK'
                self.columns['name'].color.special_by_name('default')
                self.columns['prefix'].color.special_by_name('default')
            elif is_suppressed:
                # If it is suppressed, display nothing and store False
                self.columns['enable'].value = False
                self.columns['enable'].display_value = '#'
                # self.columns['enable'].icon_resource = None
                self.columns['name'].color.special_by_name('gray')
                self.columns['prefix'].color.special_by_name('gray')

        return locals()

    suppress = property(**suppress())

   # def parse_meta(self, line):
#	meta = re.search(r'^\# replay\s+(\S+):(.+)$', line)
#	if meta is not None:
#            return (meta.group(1), meta.group(2))
#	else:
#            return None

#    def render_meta(self, name, val):
#	return "# replay {n}:{v}".format(n=name, v=val)

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

#    def run(self):
#        """Runs the command."""
#
#        # Build the MODO command string:
#        command = self.render_LXM_without_comment()

        # Run the command:
#        lx.eval(command)
