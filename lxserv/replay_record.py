import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""

import lxifc, modo, lx

# The hardest part is going to be dealing with undos.  If the user executes 2 commands,
# undoes one, and then executes another command, presumably you don't want to record
# the undone command.  And you can't execute app.undo (or app.redo -- really, any command
# with the UNDOSPECIAL flag set) from within a macro, so you'll want to skip that as well.
# There doesn't appear to be an undo listener, so you can't monitor that, unfortunately.
# And you can't just listen to app.undo commands and step back one, because of the
# post commands used by the tool system.  That said, if you do use app.undo to detect
# undos and you detect a post command (by checking its command flags), you can skip
# the post command.  I think there might be some other special cases, though.

class CmdListener(lxifc.CmdSysListener):

    def __init__(self):
        self.svc_listen = lx.service.Listener()
        self.svc_listen.AddListener(self)
        self.armed = True
        self.refiring = False

        self.refire_order = []
        self.refire_last = {}

        self.state = False
        self.block_depth = 0
        self.total_depth = 0
        self.tool_doApply = False

        self.debug_path = []

    def valid_for_record(self, cmd, isResult = False):
        if not self.state:
            return False

        if not self.armed:
            return False

        if (cmd.Flags() & lx.symbol.fCMD_QUIET):
            self.debug_path_print(cmd.Name() + " - Quiet command. Ignore.")
            return False

        if cmd.Name().startswith("replay."):
            self.debug_path_print(cmd.Name() + " - Replay command. Ignore.")
            return False

        if cmd.Name() in ['tool.attr','tool.noChange']:
            self.debug_path_print(cmd.Name() + " - Black list. Ignore.")
            return False

        if cmd.Name() in ['app.undo', 'app.redo']:
            modo.dialogs.alert("Undo during recording", "'%s' cannot be recorded in a macro at this time. Recording will stop." % cmd.Name())
            lx.eval('replay.record stop')
            return False

        if cmd.Name() in ['select.paint', 'select.lasso']:
            if isResult:
                modo.dialogs.alert("Interactive during recording", "'%s' cannot be recorded in a macro at this time. Recording will stop." % cmd.Name())
                lx.eval('replay.record stop')
            return False

        return True

    def cmdsysevent_ExecutePre(self,cmd,cmd_type,isSandboxed,isPostCmd):
        # lx.out("ExecutePre", lx.object.Command(cmd).Name(), cmd_type,isSandboxed,isPostCmd)

        cmd = lx.object.Command(cmd)
        if not self.valid_for_record(cmd):
            return

        # Must happen AFTER we validate.
        self.total_depth += 1
        self.debug_path.append(cmd.Name())

    def cmdsysevent_ExecuteResult(self, cmd, type, isSandboxed, isPostCmd, wasSuccessful):
        # lx.out("ExecuteResult", lx.object.Command(cmd).Name(), type, isSandboxed, isPostCmd, wasSuccessful)

        cmd = lx.object.Command(cmd)
        if not self.valid_for_record(cmd, True):
            return

        # Must happen AFTER we validate.
        self.total_depth -= 1

        # Only record base-level commands
        if self.total_depth - self.block_depth == 0:

            if self.refiring:
                self.debug_path_print("Refiring.")
                if cmd.Name() not in self.refire_order:
                    self.refire_order.append(cmd.Name())
                self.refire_last[cmd.Name()] = cmd

            else:
                self.debug_path_print("Adding to macro.")
                self.replay_lineInsert(cmd)

        else:
            self.debug_path_print("- Wrong depth (%s), ignore." % (self.total_depth - self.block_depth))

        del self.debug_path[-1]

    def cmdsysevent_ExecutePost(self,cmd,isSandboxed,isPostCmd):
        # lx.out("ExecutePost", lx.object.Command(cmd).Name(), isSandboxed,isPostCmd)
        cmd = lx.object.Command(cmd)
        # if cmd.Name() == 'tool.doApply':
        #     lx.eval('replay.lineInsertQuiet {tool.doApply}')

    def cmdsysevent_BlockBegin(self, block, isSandboxed):
        self.debug_path_print("Block Begin")
        self.block_depth += 1
        self.total_depth += 1
        self.debug_path.append("Block")
        pass

    def cmdsysevent_BlockEnd(self, block, isSandboxed, wasDiscarded):
        self.block_depth -= 1
        self.total_depth -= 1
        del self.debug_path[-1]
        self.debug_path_print("Block End")
        pass

    def cmdsysevent_RefireBegin(self):
        # we don't want a bunch of events when the user is
        # dragging a minislider or something like that,
        # so we disarm the listener on RefireBegin...
        self.debug_path_print("Refire Begin vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        self.refiring = True
        self.refire_order = []
        self.refire_last = {}

    def cmdsysevent_RefireEnd(self):
        # ... and rearm on RefireEnd
        self.debug_path_print("Refire End ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        self.refiring = False

        for cmd_name in self.refire_order:
            if cmd_name == 'tool.doApply':
                continue
            lx.out("Adding", cmd_name)
            self.replay_lineInsert(self.refire_last[cmd_name])
        if 'tool.doApply' in self.refire_order:
            self.replay_lineInsert(self.refire_last['tool.doApply'])

    def replay_lineInsert(self, cmd):
        svc_command = lx.service.Command()
        self.armed = False
        lx.eval("replay.lineInsertQuiet {%s}" % svc_command.ArgsAsStringLen(cmd, True))
        self.armed = True

    def debug_path_print(self, msg):
        lx.out(" > ".join(self.debug_path), msg)

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
