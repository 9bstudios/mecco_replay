# python
'''
The Notifier module contains the Notifier class, which is used to fire
CommandEvents in modo

.. todo:
    - don't import modules using commas. use separate import lines.
    - name everything according to PEP 8 conventions, only classes should use
      UpCase all others should be snake_case, constants are UPPER_SNAKE_CASE.
'''
import lx, lxifc


class Notifier(lxifc.Notifier):
    '''
    An event notifier that hooks into modo's CommandEvent

    Args:
        None

    Returns:
        Notifier
    '''
    masterList = {}

    def noti_Name(self):
        '''
        Name of notification

        Args:
            None

        Returns:
            str: replay.notifier

        .. todo:
            - these methods occur in the class body of a class called Notifier.
              why do the method names need "noti_" prepended to them?
        '''
        return "replay.notifier"

    def noti_AddClient(self, event):
        '''
        Registers a client event with the masterlist???

        Args:
            event (???): event to be added

        Returns:
            None
        '''
        self.masterList[event.__peekobj__()] = event

    def noti_RemoveClient(self, event):
        '''
        Removes event from masterlist

        Args:
            event (???): event to be removed

        Returns:
            None
        '''
        del self.masterList[event.__peekobj__()]

    def Notify(self, flags):
        '''
        Fire each event in masterlist with given flags

        Args:
            flags (???): event flags

        Returns:
            None
        '''
        for event in self.masterList:
            evt = lx.object.CommandEvent(self.masterList[event])
            evt.Event(flags)

lx.bless(Notifier, "replay.notifier")
