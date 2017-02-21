# python

import replay_lumberjack

class ReplayLumberjack(replay_lumberjack.Lumberjack):
    """Our own Replay-specific subclass of the Lumberjack treeview class. This
    class will be instantiated any time MODO wants to use it, which can be
    pretty often. Most of its methods are class-wide, so we don't need to
    store a specific instance of the class, but rather work with the class itself.

    Examples:
    """
    pass
