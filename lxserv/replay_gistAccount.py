# python

import base64
import lx, modo
import replay
from replay import message as message

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class GistAccountClass(replay.commander.CommanderClass):
    """Editor for command argument values. Accepts an argName and a value query.
    Designed specifically for use with `replay.argEditFCL`."""
    
    def commander_arguments(self):
        return [
            {
                'name': 'username',
                'label': 'User Name',
                'datatype': 'string',
                'flags': ['query']
            }, {
                'name': 'password',
                'label': 'Password',
                'datatype': 'string',
                'flags': ['query']
            }
        ]
        
    def cmd_DialogInit(self):
        self.attr_SetString(1, "")

    def commander_execute(self, msg, flags):
        """Fires whenever the value is updated in the form. Stores changes in the
        proper place."""
        username = self.commander_args()['username']
        password = self.commander_args()['password']

        # temporary using base64 instead of encryption
        # need to be figure out what library to use and encrypt instead
        password = base64.b64encode(password)
        
        lx.eval("user.value mecco_replay_gist_username {%s}" % username)
        lx.eval("user.value mecco_replay_gist_password {%s}" % password)
           
    def cmd_Query(self, index, vaQuery):
        """Fires whenever the value is displayed in the form. Should return the value(s)
        to be displayed in the edit field. If multiple values are provided, MODO will
        display "mixed..." in the edit field for batch editing."""

        # Create the ValueArray object
        va = lx.object.ValueArray()
        va.set(vaQuery)

        if index == 0:
            va.AddString(lx.eval("user.value mecco_replay_gist_username ?"))
        elif index == 1:
            password = lx.eval("user.value mecco_replay_gist_password ?")
            va.AddString('*' * len(password))
            
        return lx.result.OK
        
lx.bless(GistAccountClass, 'replay.gistAccount')
