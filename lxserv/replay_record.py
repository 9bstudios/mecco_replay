import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class RecordCommandClass(replay.commander.CommanderClass):
    """Start or stop Macro recording. The `mode` argument starts recording when
    `True` (or empty), stops recording when `False`, and toggles recording when queried.

    When recording stops, the resulting file will be saved to a temporary location
    inside the kit directory, then read and parsed using the `Macro().parse_LXM()`
    method. The user will then be prompted to save the file using `replay.fileSave`."""

    _recording = False

    def commander_arguments(self):
        return [
            {
                'name': 'mode',
                'datatype': 'string',
                'default': 'toggle',
                'values_list_type': 'popup',
                'values_list': ['toggle', 'start', 'stop'],
                'flags': ['optional']
            }, {
                'name': 'status',
                'datatype': 'boolean',
                'default': True,
                'flags': ['query', 'optional']
            }
        ]

    def commander_execute(self, msg=None, flags=None):
        mode = self.commander_arg_value(0, 'toggle')
        state = self.__class__._recording

        lx.out(mode)
        if mode == 'toggle':
            state = False if state else True
        elif mode == 'start':
            state = True
        elif mode == 'stop':
            state = False
        #
        # if mode:
        #     # In case it's already recording, start over.
        #     lx.eval('macro.record false')
        #
        #     # Start recording.
        #     lx.eval('macro.record true')
        #
        # elif not mode:
        #     try:
        #         # Store the temp file in the root kit directory.
        #         temp_file_path = lx.eval('query platformservice alias ? "kit_mecco_replay:tmp.LXM"')
        #
        #         # Try saving the file.
        #         lx.eval('macro.saveRecorded {%s}' % temp_file_path)
        #
        #         # Open the saved macro for editing.
        #         lx.eval('replay.fileOpen {%s}' % temp_file_path)
        #
        #     except:
        #         # The Macro recording was probably empty.
        #         pass

    def cmd_Query(self,index,vaQuery):
        # Fires whenever any argument is queried.

        va = lx.object.ValueArray()
        va.set(vaQuery)

        # args = self.commander_arguments()
        #
        # if index < len(args):
        #     is_query = 'query' in args[index].get(FLAGS, [])
        #     is_not_fcl = args[index].get(VALUES_LIST_TYPE) != FCL
        #     has_recent_value = self._commander_stored_values[index]
        #
        #     if is_query and is_not_fcl and has_recent_value:
        #         va.AddString(has_recent_value)

        lx.out('queried', int(self._recording))

        va.AddInt(int(self._recording))

        return lx.result.OK


lx.bless(RecordCommandClass, 'replay.record')
