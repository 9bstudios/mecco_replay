# python

import lx

class CommandNode(object):
    
    def __init__(self, **kwargs):
        self.command = kwargs.get('command', None)
        self.parent = kwargs.get('parent', None)
        self.children = []
        
    def children():
        def fget(self):
            return self._children
        def fset(self, value):
            self._children = value
        return locals()
        
    children = property(**children())
    
    def parent():
        def fget(self):
            return self._parent
        def fset(self, value):
            self._parent = value
        return locals()
        
    parent = property(**parent())
    
    def command():
        def fget(self):
            return self._command
        def fset(self, value):
            self._command = value
        return locals()
        
    command = property(**command())
    
    def add_command(self, cmd):
        self.children.append(CommandNode(command=cmd, parent=self))
        return self.children[-1]
        
    def add_block(self):
        self.children.append(CommandNode(command=None, parent=self))
        return self.children[-1]
        
    def is_block(self):
        return self.command is None
        
    def __repr__(self):
        doc = """For debugging"""
        if self.command is not None:
            return "Command " + self.command
        else:
            return "Block " + repr(self.children)
            
class RecordingCache(object):
    """Persistent object that holds block commands during block recording"""

    _root = None
    _current = None
    
    def beginBlock(self):
        lx.out("Begin block")
        if self.root is None:
            self.root = CommandNode()
            self.current = self.root
        else:
            block = self.current.add_block()
            self.current = block
        
    def endBlock(self):
        lx.out("End block")
        if self.current is None:
            raise Exception("Invalid end of block")
            
        self.current = self.current.parent
        
        if self.current is None:
            lx.out("Clearing")
            self.root = None

    def add_command(self, cmd):
        self.current.add_command(cmd)

    def commands():
        doc = """List of cached commands"""
        def fget(self):
            return self.__class__._root.children
        return locals()

    commands = property(**commands())
    
    def root():
        def fget(self):
            return self.__class__._root
        def fset(self, value):
            self.__class__._root = value
        return locals()

    root = property(**root())
    
    def current():
        def fget(self):
            return self.__class__._current
        def fset(self, value):
            self.__class__._current = value
        return locals()

    current = property(**current())
