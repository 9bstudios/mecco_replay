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
        self.refire_last = None
        self.state = False
        self.block_depth = 0
        self.total_depth = 1 # We are starting listner from command so we will listen one ExecutePost without ExecutePre

    def valid_for_record(self, cmd):
        if not self.state:
            return False

        if not self.armed:
            return False

        if (cmd.Flags() & lx.symbol.fCMD_QUIET):
            return False

        if cmd.Name().startswith("replay."):
            return False

        if cmd.Name() in ['app.undo', 'app.redo']:
            modo.dialogs.alert("Undo during recording", "'Undo' cannot be recorded in a macro at this time. Recording will stop.")
            lx.eval('replay.record stop')
            return False

        return True

    def cmdsysevent_ExecutePre(self,cmd,cmd_type,isSandboxed,isPostCmd):
#        lx.out("ExecutePre", lx.object.Command(cmd).Name(), cmd_type,isSandboxed,isPostCmd)
        self.total_depth += 1
        
        cmd = lx.object.Command(cmd)
        
        if not self.valid_for_record(cmd):
            return
            
    def cmdsysevent_ExecuteResult(self, cmd, type, isSandboxed, isPostCmd, wasSuccessful):
 #       lx.out("ExecuteResult", lx.object.Command(cmd).Name(), type, isSandboxed, isPostCmd, wasSuccessful)
        self.total_depth -= 1

    def cmdsysevent_ExecutePost(self,cmd,isSandboxed,isPostCmd):
#        lx.out("ExecutePost", lx.object.Command(cmd).Name(), isSandboxed,isPostCmd)
        cmd = lx.object.Command(cmd)
        if not self.valid_for_record(cmd):
            return
            
        if self.total_depth - self.block_depth == 0: # Result alreade decreased total_depth
            if self.refiring:
                self.refire_last = cmd
            else:
                svc_command = lx.service.Command()
                self.armed = False
                lx.eval("replay.lineInsertQuiet {%s}" % svc_command.ArgsAsStringLen(cmd, True))
                self.armed = True

    def cmdsysevent_BlockBegin(self, block, isSandboxed):
        self.block_depth += 1
        self.total_depth += 1

    def cmdsysevent_BlockEnd(self, block, isSandboxed, wasDiscarded):
        self.block_depth -= 1
        self.total_depth -= 1

    def cmdsysevent_RefireBegin(self):
        # we don't want a bunch of events when the user is
        # dragging a minislider or something like that,
        # so we disarm the listener on RefireBegin...
        self.refiring = True
        self.refire_last = None

    def cmdsysevent_RefireEnd(self):
        # ... and rearm on RefireEnd
        self.refiring = False

        if self.refire_last is not None:
            cmd = self.refire_last
            svc_command = lx.service.Command()

            self.armed = False
            lx.eval("replay.lineInsertQuiet {%s}" % svc_command.ArgsAsStringLen(cmd, True))
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
