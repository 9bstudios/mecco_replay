# python
'''
The RecordingCache module contains the RedordingCache class, which is used to
persist block commands during recording
'''
import lx


class RecordingCache(object):
    '''
    Persistent object that holds block commands during block recording

    Args:
        None

    Attributes:
        commands: class property of modo commands???

    Returns:
        None
    '''
    _commands = []

    def clear(self):
        '''
        Deletes commands from instance

        Args:
            None

        Returns:
            None
        '''
        del self.commands[:]

    def add_command(self, cmd):
        '''
        Adds a command to instance

        Args:
            cmd (???): command to be added

        Returns:
            None
        '''
        self.commands.append(cmd)

    def commands():
        '''
        Makes commands available to modo

        Args:
            None

        Returns:
            locals???
        '''
        doc = """List of cached commands"""
        def fget(self):
            return self.__class__._commands
        def fset(self, value):
            self.__class__._commands = value
        return locals()

    commands = property(**commands())
