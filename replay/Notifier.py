# python
'''
The Notifier module contains the Notifier class, which is used to fire
CommandEvents in modo
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
        '''
        return "replay.notifier"

    def noti_AddClient(self, event):
        '''
        Add event to masterlist???

        Args:
            event (???): event to be added

        Returns:
            None
        '''
        self.masterList[event.__peekobj__()] = event

    def noti_RemoveClient(self, event):
        '''
        Removes event from masterlist???

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
