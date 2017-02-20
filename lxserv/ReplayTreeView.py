# python

import lx
import mecco_replay
import lumberjack

class ReplayLumberjack(lumberjack.Lumberjack):

    def blessing_parameters(self):
        return {
            lumberjack.VPTYPE: 'vpapplication',
            lumberjack.NICE_NAME: 'Replay',
            lumberjack.INTERNAL_NAME: 'replayTreeView',
            lumberjack.ID4: 'RMTV',
            lumberjack.REGIONS: [
                '(anywhere)', # 0 is reserved ".anywhere" region index
                'Command', #1
                'Playhead', #2
            ],
            lumberjack.NOTIFIERS: [
                ("select.event", "polygon +ldt"),
                ("select.event", "item +ldt")
            ]
        }

ReplayLumberjack().bless()

###################
# Static test data:
###################

ReplayLumberjack().rebuild({
    'columns': [
        {
            'internal-name': 'enable',
            'width': 20,
            'icon-resource': 'myIconResource'
        }, {
            'internal-name': 'name',
            'width': -1,
            'primary': True
        }, {
            'internal-name': 'value',
            'width': -3
        }
    ]
    'data': [
        {
            'id': 1,
            'values': {
                'enable': { 'value': True },
                'name': { 'value': 'A' },
                'value': { 'value': 1.0 }
            }
        }
    ]
})
