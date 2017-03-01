# python

class ReplayMacroCommand(object):
    """Contains everything necessary to read, construct, write, and translate a
    MODO command for use in macros or Python scripts."""

    _command = None
    _args = {}
    _suppress = False
    _comment_before = None

    def __init__(self, command_string=None):
        if command_string is not None:
            self.parse_string(command_string)

    def command():
        doc = "The base MODO command, e.g. `item.name`."
        def fget(self):
            return self._command
        def fset(self, value):
            self._command = value
        return locals()

    command = property(**command())

    def args():
        doc = "A dictionary of arguments and their values."
        def fget(self):
            return self._args
        def fset(self, value):
            self._args = value
        return locals()

    args = property(**args())

    def suppress():
        doc = "Boolean. Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            return self._suppress
        def fset(self, value):
            self._suppress = value
        return locals()

    suppress = property(**suppress())

    def comment_before():
        doc = """String to be added as comment text before the command. Long strings
        will automatically be broken into lines of 80 characters or less. Appropriate
        comment syntax will be rendered at export time. Include only the raw string."""
        def fget(self):
            return self._comment_before
        def fset(self, value):
            self._comment_before = value
        return locals()

    comment_before = property(**comment_before())

    def meta():
        doc = "Suppresses (comments) the command by appending a `#` before it."
        def fget(self):
            return self._meta
        def fset(self, value):
            self._meta = value
        return locals()

    meta = property(**meta())

    def parse_string(command_string):
        """Parse a normal MODO command string into its constituent parts, and
        stores those in the `command` and `args` properties for the object."""
        pass


class ReplayMacro(object):
    """Contains everything necessary to store, manage, and save a MODO maco or
    script using Replay. All macro management commands make use of this object class.

    To work around the lack of a gloal namespace in MODO, `ReplayMacro()` objects
    work entirely with class variables and classmethods."""

    _commands = []

    def __init__(self):
        pass

    def commands():
        doc = """The list of `ReplayMacroCommand()` objects for the macro, in
        order from first to last."""
        def fget(self):
            return self._commands
        def fset(self, value):
            self._commands = value
        return locals()

    commands = property(**commands())

    def render_LXM(self):
        """Generates an LXM string for export."""
        pass

    def render_Python(self):
        """Generates a Python string for export."""
        pass

    def render_json(self):
        """Generates a json string for export."""
        pass
