import lx, modo, replay
from replay import message as message

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

        # Sometimes multiple commands are in refire mode at the same time.
        # We need to remember both the order in which they were initially fired
        # and the most recent version of the refired command.
        self.refire_order = []
        self.refire_last = {}

        self.state = False
        self.block_depth = 0
        self.total_depth = 0
        self.tool_doApply = False
        self.record_in_block = False

        # A list of sub-commands and blocks for debug printing.
        self.debug_path = []

    def valid_for_record(self, cmd, isResult = False):

        # Recording is disabled by user.
        if not self.state:
            return False

        # Recording is disarmed for internal reasons.
        if not self.armed:
            return False

        # Never record "quiet" commands.
        if (cmd.Flags() & lx.symbol.fCMD_QUIET):
            self.debug_path_print(cmd.Name() + " - Quiet command. Ignore.")
            return False

        # Never record replay commands.
        if cmd.Name().startswith("replay."):
            self.debug_path_print(cmd.Name() + " - Replay command. Ignore.")
            return False

        # Certain commands can be safely ignored. These can be added here.
        # Note that any ignored command's sub-commands _will_ be recorded.
        if cmd.Name() in ['tool.attr','tool.noChange']:
            self.debug_path_print(cmd.Name() + " - Black list. Ignore.")
            return False

        # We cannot record undo/redo. There is no reliable method of doing so.
        # Instead, we simply stop recording.
        if cmd.Name() in ['app.undo', 'app.redo']:
            modo.dialogs.alert(message("MECCO_REPLAY", "UNDO_DURING_RECORDING"), message("MECCO_REPLAY", "CANNOT_RECORD_MSG", cmd.Name()))
            lx.eval('replay.record stop')
            return False

        # We cannot record interactive selections (i.e. clicking in the viewport to select).
        # Instead, we simply warn the user and stop recording.
        # NOTE: This can cause crashes. Be careful.
        if cmd.Name() in ['select.paint', 'select.lasso']:
            if isResult:
                modo.dialogs.alert(message("MECCO_REPLAY", "INTERACTIVE_DURING_RECORDING"), message("MECCO_REPLAY", "CANNOT_RECORD_MSG", cmd.Name()))
                lx.eval('replay.record stop')
            return False

        # If we pass all of the above tests, we're good to record.
        return True

    def cmdsysevent_ExecutePre(self,cmd,cmd_type,isSandboxed,isPostCmd):
        # lx.out("ExecutePre", lx.object.Command(cmd).Name(), cmd_type,isSandboxed,isPostCmd)

        cmd = lx.object.Command(cmd)
        if self.valid_for_record(cmd):
            self.total_depth += 1
            self.debug_path.append(cmd.Name())

    def callId(self, cmd):
        cmd = lx.object.Command(cmd)
        attrs = lx.object.Attributes(cmd)

        res = [cmd.Name()]

        for idx in xrange(0, attrs.Count()):
            if cmd.ArgFlags(idx) & lx.symbol.fCMDARG_VARIABLE == 0:
                res.append(attrs.GetString(idx))

        return tuple(res)

    def cmdsysevent_ExecuteResult(self, command, type, isSandboxed, isPostCmd, wasSuccessful):
        # lx.out("ExecuteResult", lx.object.Command(cmd).Name(), type, isSandboxed, isPostCmd, wasSuccessful)

        cmd = lx.object.Command(command)
        if self.valid_for_record(cmd, True):
            self.total_depth -= 1

            # Only record base-level commands
            if self.total_depth - self.block_depth == 0:

                # We don't record things during refire,
                # but we do need to keep track of them.
                if self.refiring:
                    self.debug_path_print("Refiring.")

                    # Keep track of the order of operations.
                    id = self.callId(command)
                    if id not in self.refire_order:
                        self.refire_order.append(id)

                    # Store latest iteration of refired command.
                    self.refire_last[id] = cmd

                else:

                    # All good. Add to macro.
                    self.debug_path_print("Adding to macro.")
                    self.sendCommand(cmd)

            # Command is a sub-command. Ignore it.
            else:
                self.debug_path_print("- Wrong depth (%s), ignore." % (self.total_depth - self.block_depth))

            # We're done here. Pop back a level in our debug printout.
            del self.debug_path[-1]

    def cmdsysevent_ExecutePost(self,cmd,isSandboxed,isPostCmd):
        # lx.out("ExecutePost", lx.object.Command(cmd).Name(), isSandboxed,isPostCmd)
        pass

    def cmdsysevent_BlockBegin(self, block, isSandboxed):
        # NOTE: Blocks are not the same as sub-commands. Block are arbitrary groupings
        # of commands, while sub-commands are any command that takes plice while another
        # is still running. Not all sub-commands are grouped into blocks, and not all
        # blocks are comprised of sub-commands.

        if self.block_depth == 0:
            # RecordingCache should be clear at this point. Just in any case clear it again
            replay.RecordingCache().clear()
            self.record_in_block = True
            self.debug_path_print("Begin Recorded Block")
        else:
            self.debug_path_print("Begin Ignored Block")

        self.block_depth += 1
        self.total_depth += 1

        self.debug_path.append("Block")

    def cmdsysevent_BlockEnd(self, block, isSandboxed, wasDiscarded):
        self.block_depth -= 1
        self.total_depth -= 1

        del self.debug_path[-1]

        if self.block_depth == 0:
            self.debug_path_print("End Recorded Block")
            # If refiring, wait to end block until we get to cmdsysevent_RefireEnd()
            if not self.refiring:
                self.closeBlock()
        else:
            self.debug_path_print("End Ignored Block")

    def cmdsysevent_RefireBegin(self):
        # we don't want a bunch of events when the user is
        # dragging a minislider or something like that,
        # so we disarm the listener on RefireBegin...
        self.debug_path_print("Refire Begin")
        self.refiring = True

        # Reset our refire tracking vars.
        self.refire_order = []
        self.refire_last = {}

    def cmdsysevent_RefireEnd(self):
        # ... and rearm on RefireEnd
        self.debug_path_print("Refire End")
        self.refiring = False

        # Sometimes `tool.doApply` is added at the wrong time. It should always
        # be added last. As a special case, we manually make sure it's last in
        # the list.
        svc_ = lx.service.Command()
        x, y, applyCmd = svc_.SpawnFromString('tool.doApply')
        applyId = self.callId(applyCmd)
        if applyId in self.refire_order:
            self.refire_order.remove(applyId)
            self.refire_order.append(applyId)

        # Now that refire is over, we can add our commands to the macro in the
        # order in which they were first fired.
        for cmd_id in self.refire_order:
            self.debug_print("Adding refired: " + str(cmd_id))
            self.sendCommand(self.refire_last[cmd_id])

        # In case we're inside a block (see `BlockEnd` above), end it.
        if self.record_in_block:
            self.closeBlock()

    def closeBlock(self):
        self.record_in_block = False
        if replay.RecordingCache().commands:
            lx.eval("replay.lastBlockInsert")
            replay.RecordingCache().clear()

    def sendCommand(self, cmd):
        if self.record_in_block:
            svc_command = lx.service.Command()
            replay.RecordingCache().add_command(svc_command.ArgsAsStringLen(cmd, True))
        else:
            self.replay_lineInsert(cmd)

    def replay_lineInsert(self, cmd):
        svc_command = lx.service.Command()
        self.armed = False

        try:
            button_name = " {%s}" % cmd.ButtonName()
        except:
            button_name = ""

        lx.eval("replay.lineInsertQuiet {%s}%s" % (svc_command.ArgsAsStringLen(cmd, True), button_name))
        self.armed = True

    def debug_path_print(self, msg):
        return
        self.debug_print(" > ".join(self.debug_path) + " " + msg)

    def debug_print(self, msg):
        return
        lx.out(msg)

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

    def cmd_Flags(self):
        """Set command flags. This method can be overridden if special flags
        are needed."""
        return lx.symbol.fCMD_UI | lx.symbol.fCMD_QUIET

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
