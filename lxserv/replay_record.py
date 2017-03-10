import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class RecordCommandClass(replay.commander.CommanderClass):
    """Start or stop Macro recording. The `mode` argument starts recording when
    `start`, stops recording when `stop`, and toggles recording when `toggle`.

    The `query` argument should be queried for toolbar highlighting.

    When recording stops, the resulting file will be saved to a temporary location
    inside the kit directory, then read and parsed using the `Macro().parse_LXM()`
    method and inserted after the current primary command."""

    # Whether or not we are currently recording.
    # TODO We currently track this manually, so enabling or disabling macro recording
    # in any other way will break this command. We should find a listener.
    _recording = False

    def commander_arguments(self):
        """Command takes two arguments: `mode` and `query`.
        `mode` can be `start`, `stop`, or `toggle`."""
        return [
            {
                'name': 'mode',
                'datatype': 'string',
                'default': 'toggle',
                'values_list_type': 'popup',
                'values_list': ['toggle', 'start', 'stop'],
                'flags': ['optional']
            }, {
                'name': 'query',
                'datatype': 'boolean',
                'default': True,
                'flags': ['query', 'optional']
            }
        ]

    @classmethod
    def set_state(cls, state):
        cls._recording = state

    def commander_execute(self, msg=None, flags=None):
        mode = self.commander_arg_value(0, 'toggle')

        # Remember for next time
        # -----------

        if mode == 'start':
            state = True

        elif mode == 'stop':
            state = False

        else:
            state = False if self._recording else True

        self.set_state(state)

        # Do the work
        # -----------

        if state:
            # In case it's already recording, start over.
            lx.eval('!!macro.record false')

            # Start recording.
            lx.eval('!!macro.record true')

        elif not state:
            try:
                # Store the temp file in the root kit directory.
                temp_file_path = lx.eval('query platformservice alias ? "kit_mecco_replay:tmp.LXM"')

                # Try saving the file.
                lx.eval('!!macro.saveRecorded {%s}' % temp_file_path)

            except:
                # The Macro recording was probably empty.
                raise Exception("Unable to save temp file.")

            try:
                # Open the saved macro for editing.
                lx.eval('!!replay.fileInsert {%s}' % temp_file_path)

            except:
                # The Macro recording was probably empty.
                raise Exception("Unable to load temp file.")

                import traceback
                traceback.print_exc()

        notifier = replay.Notifier()
        notifier.Notify(lx.symbol.fCMDNOTIFY_CHANGE_ALL)



    def commander_query(self, arg_index):
        if arg_index  == 1:
            return self._recording


lx.bless(RecordCommandClass, 'replay.record')
