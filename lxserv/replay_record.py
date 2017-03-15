import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

import lxifc, modo, lx

class CmdListener(lxifc.CmdSysListener):
    block_depth = 0
    total_depth = 0

    def __init__(self):
        self.svc_listen = lx.service.Listener()
        self.svc_listen.AddListener(self)
        self.armed = True
        self.state = False

    def cmdsysevent_ExecutePre(self,cmd,cmd_type,isSandboxed,isPostCmd):
        cmd = lx.object.Command(cmd)
        if not self.valid_for_record(cmd):
            return

        self.__class__.total_depth += 1

        if self.total_depth - self.block_depth == 1:
            svc_command = lx.service.Command()
            self.armed = False
            lx.eval("replay.lineInsert {%s}" % svc_command.ArgsAsStringLen(cmd, True))
            self.armed = True

    def cmdsysevent_ExecutePost(self,cmd,isSandboxed,isPostCmd):
        cmd = lx.object.Command(cmd)
        if not self.valid_for_record(cmd):
            return

        self.__class__.total_depth -= 1

    def cmdsysevent_BlockBegin(self, block, isSandboxed):
        self.__class__.block_depth += 1
        self.__class__.total_depth += 1

    def cmdsysevent_BlockEnd(self, block, isSandboxed, wasDiscarded):
        self.__class__.block_depth -= 1
        self.__class__.total_depth -= 1

    def cmdsysevent_RefireBegin(self):
        # we don't want a bunch of events when the user is
        # dragging a minislider or something like that,
        # so we disarm the listener on RefireBegin...
        self.armed = False

    def cmdsysevent_RefireEnd(self):
        # ... and rearm on RefireEnd
        self.armed = True

class RecordCommandClass(replay.commander.CommanderClass):
    """Start or stop Macro recording. The `mode` argument starts recording when
    `start`, stops recording when `stop`, and toggles recording when `toggle`.

    The `query` argument should be queried for toolbar highlighting.

    When recording stops, the resulting file will be saved to a temporary location
    inside the kit directory, then read and parsed using the `Macro().parse_LXM()`
    method and inserted after the current primary command."""

    # Whether or not we are currently recording.
    # TODO We currently track this manually, so enabling or disabling macro recording
    # in any other way will break this command. We should find a listener.
    _recording = False
    _cmd_listner = None

    def commander_arguments(self):
        """Command takes two arguments: `mode` and `query`.
        `mode` can be `start`, `stop`, or `toggle`."""
        return [
            {
                'name': 'mode',
                'datatype': 'string',
                'default': 'toggle',
                'values_list_type': 'popup',
                'values_list': ['toggle', 'start', 'stop'],
                'flags': ['optional']
            }, {
                'name': 'query',
                'datatype': 'boolean',
                'default': True,
                'flags': ['query', 'optional']
            }
        ]

    def commander_notifiers(self):
        # We need to update our values whenever the replay notifier fires for
        # selection state changes and tree updates.
        return [("replay.notifier", "")]

    @classmethod
    def set_state(cls, state):
        cls._recording = state

    @classmethod
    def set_lisnter(cls):
        if cls._cmd_listner is None:
            cls._cmd_listner = CmdListener()

    @classmethod
    def set_lisnter_state(cls, value):
        cls._cmd_listner.state = value

    def commander_execute(self, msg=None, flags=None):
        mode = self.commander_arg_value(0, 'toggle')

        self.set_lisnter()

        # Remember for next time
        # -----------

        if mode == 'start':
            state = True

        elif mode == 'stop':
            state = False

        else:
            state = False if self._recording else True

        self.set_state(state)

        # notify the button to update
        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)

        # Do the work
        # -----------

        self.set_lisnter_state(state)


    def commander_query(self, arg_index):
        if arg_index  == 1:
            return self._recording


lx.bless(RecordCommandClass, 'replay.record')
