# python

# Possible alternative approach from Joe:
# We do have a "confirm quit" event, which we send over the internal application
# port.  You can get to this from ILxSessionListener::CheckQuitUI().
# If you return LXe_FALSE from CheckQuitUI(), the app won't quit.

import lxifc, modo, lx
svc_listen = lx.service.Listener()

class CmdListener(lxifc.CmdSysListener):
    def __init__(self):
        svc_listen.AddListener(self)
        self.armed = True

    def cmdsysevent_ExecutePre(self,cmd,type,isSandboxed,isPostCmd):
        if self.armed:
            cmd = lx.object.Command(cmd)
            # lx.out("'%s' will fire shortly" % cmd.Name())
            if cmd.Name() == "app.quit":
                lx.eval('replay.fileClose')

    def cmdsysevent_ExecutePost(self,cmd,isSandboxed,isPostCmd):
        # if self.armed:
        #     cmd = lx.object.Command(cmd)
        #     lx.out("'%s' has finished" % cmd.Name())
        pass

    def cmdsysevent_RefireBegin(self):
        # we don't want a bunch of events when the user is
        # dragging a minislider or something like that,
        # so we disarm the listener on RefireBegin...
        self.armed = False

    def cmdsysevent_RefireEnd(self):
        # ... and rearm on RefireEnd
        self.armed = True

cmdListener1 = CmdListener()
