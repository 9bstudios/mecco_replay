# python

class Task(object):
    def __init__(self):
        self._command = 'noop'
        self._arguments = {}
        self._comment = None
        self._meta = {}
        self._suppress_dialogs = True
        self._suppress = False

    def command():
        doc = """The command property."""
        def fget(self):
            return self._command
        def fset(self, command):
            self._command = command
        return locals()

    command = property(**command())

    def arguments():
        doc = """The arguments property."""
        def fget(self):
            return self._arguments
        def fset(self, arguments):
            self._arguments = arguments
        return locals()

    arguments = property(**arguments())

    def comment():
        doc = """The comment property."""
        def fget(self):
            return self._comment
        def fset(self, comment):
            self._comment = comment
        return locals()

    comment = property(**comment())

    def meta():
        doc = """The meta property."""
        def fget(self):
            return self._meta
        def fset(self, meta):
            self._meta = meta
        return locals()

    meta = property(**meta())

    def suppress_dialogs():
        doc = """The suppress_dialogs property."""
        def fget(self):
            return self._suppress_dialogs
        def fset(self, suppress_dialogs):
            self._suppress_dialogs = suppress_dialogs
        return locals()

    suppress_dialogs = property(**suppress_dialogs())

    def suppress():
        doc = """The suppress property."""
        def fget(self):
            return self._suppress
        def fset(self, suppress):
            self._suppress = suppress
        return locals()

    suppress = property(**suppress())
