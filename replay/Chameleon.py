# python

class Chameleon(object):
    """The Chameleon class stores all of the arguments for the `replay.chameleon` command.
    When `replay.chameleon` fires, it will always request and return values for each
    of the arguments provided. In practice, we can use chameleon like this:

    ```
    replay.Chameleon().arguments = [...]
    lx.eval('replay.chameleon')
    results_dict = replay.Chameleon().results
    ```

    This effectively allows us to ape the behavior of most other MODO commands."""

    _arguments = []
    _results = {}

    def arguments():
        doc = """A list of dictionaries, one for each argument to be displayed in the
        command dialog. Syntax should be identical to `Commander.commander_arguments()`
        definitions, see https://github.com/adamohern/commander"""
        def fget(self):
            return self._arguments
        def fset(self, value):
            self._arguments = value
        return locals()

    arguments = property(**arguments())

    def results():
        doc = """A dictionary with one value for each argument in the `arguments` property.
        All argument values default to `None` unless set by a previous `replay.chameleon` command.

        Dictionary is identical to `self.commander_args()` in a `Commander` class.
        See https://github.com/adamohern/commander"""
        def fget(self):
            return self._results
        def fset(self, value):
            self._results = value
        return locals()

    results = property(**results())
