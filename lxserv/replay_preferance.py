# python

import lx, lxifc, modo, replay

class CommandClass(replay.commander.CommanderClass):
    def commander_arguments(self):
        return [
                {
                    'name': 'value',
                    'datatype': 'string',
                    'default': "",
                    'flags': ['variable', 'query'],
                }, {
                    'name': 'name',
                    'datatype': 'string',
                    'flags': ['reqforvariable'],
                }
            ]

    def commander_execute(self, msg, flags):
        value = self.commander_arg_value(0)
        name = self.commander_arg_value(1)

        lx.eval("user.value %s %s" % (name, value))

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)
        
    def basic_Enable(self, msg):
        if lx.eval('replay.record query:?'):
            return False
        name = self.commander_arg_value(1)
        if name == "replay_record_layoutCreateOrClose":
            return not lx.eval("user.value replay_use_built_in_recorder ?")
        return True

    def cmd_Query(self, index, vaQuery):
        name = self.commander_arg_value(1)

        # Create the ValueArray object
        va = lx.object.ValueArray()
        va.set(vaQuery)

        va.AddInt(lx.eval("user.value %s ?" % name))
        
        return lx.result.OK
        
    def basic_ArgType(self, argIndex):
        return 'boolean'

    def commander_notifiers(self):
        return [("replay.notifier", "")]

lx.bless(CommandClass, "replay.preferance")
