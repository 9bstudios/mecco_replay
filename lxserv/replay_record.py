import lx, modo, replay

"""A simple example of a blessed MODO command using the commander module.
https://github.com/adamohern/commander for details"""


class RecordCommandClass(replay.commander.CommanderClass):
    """Start or stop Macro recording. The `mode` argument starts recording when
    `True` (or empty), stops recording when `False`, and toggles recording when queried.

    When recording stops, the resulting file will be saved to a temporary location
    inside the kit directory, then read and parsed using the `Macro().parse_LXM()`
    method. The user will then be prompted to save the file using `replay.fileSave`."""

    def commander_arguments(self):
        return [
            {
                'name': 'mode',
                'datatype': 'boolean',
                'default': True,
                'flags': ['query', 'optional']
            }
        ]

    def commander_execute(self, msg=None, flags=None):
        mode = self.commander_arg_value(0, True)

        if mode:
            # In case it's already recording, start over.
            lx.eval('macro.record false')

            # Start recording.
            lx.eval('macro.record true')

        elif not mode:
            try:
                # Store the temp file in the root kit directory.
                temp_file_path = lx.eval('query platformservice alias ? "kit_mecco_replay:tmp.LXM"')

                # Try saving the file.
                lx.eval('macro.saveRecorded {%s}' % temp_file_path)

                # Open the saved macro for editing.
                lx.eval('replay.fileOpen {%s}' % temp_file_path)

            except:
                # The Macro recording was probably empty.
                pass

    def cmd_Query(self,index,vaQuery):
        """Hack."""
        mode = self.commander_arg_value(0, True)

        # Invert the value
        mode = False if mode else True

        self.commander_execute()

        # va = lx.object.ValueArray()
        # va.set(vaQuery)
        #
        # args = self.commander_arguments()
        #
        # if index < len(args):
        #     is_query = 'query' in args[index].get(FLAGS, [])
        #     is_not_fcl = args[index].get(VALUES_LIST_TYPE) != FCL
        #     has_recent_value = self._commander_stored_values[index]
        #
        #     if is_query and is_not_fcl and has_recent_value:
        #         va.AddString(has_recent_value)

        return lx.result.OK


lx.bless(RecordCommandClass, 'replay.record')
