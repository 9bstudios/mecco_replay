# python

import lx, lxu, traceback
import replay, replay.commander

class ChameleonCommandClass(replay.commander.CommanderClass):
    """Works in tandem with the `replay.Chameleon` class to display and return
    an arbitrary list of argument values in a command dialog.

    Instead of manually setting a fixed list of arguments, we draw them from the
    persistent data in the `replay.Chameleon().arguments` property. When we're done, we simply
    deposit the resulting values back into the `replay.Chameleon().results` propery."""

    def commander_arguments(self):
        return replay.Chameleon().arguments

    def commander_execute(self, msg, flags):
        replay.Chameleon().results = self.commander_args()

lx.bless(ChameleonCommandClass, 'replay.chameleon')
