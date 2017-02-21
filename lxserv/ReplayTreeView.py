# python

import lx
import mecco_replay
import lumberjack

class ReplayLumberjack(lumberjack.Lumberjack):
    pass

ReplayLumberjack().bless(
    viewport_type = 'vpapplication',
    nice_name = 'Replay',
    internal_name = 'replayTreeView',
    ident = 'RMTV',
    columns = [
        'enable',
        'name',
        'value'
    ]
    input_regions = [
        '(anywhere)', # 0 is reserved ".anywhere" region index
        'Command', #1
        'Playhead', #2
    ],
    notifiers = []
)
