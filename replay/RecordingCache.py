# python

import lx

class RecordingCache(object):
    """Persistent object that holds block commands during block recording"""
    
    _commands = []
    
    def clear(self):
        del self.commands[:]
    
    def add_command(self, cmd):
        self.commands.append(cmd)
        
    def commands():
        doc = """List of cached commands"""
        def fget(self):
            return self.__class__._commands
        def fset(self, value):
            self.__class__._commands = value
        return locals()

    commands = property(**commands())
