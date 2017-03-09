# python

# import lx, lxu, traceback
# import replay, replay.commander
#
# class ChameleonCommandClass(replay.commander.CommanderClass):
#     """DEPRICATED - Don't use this unless you know what you're doing.
#
#     Works in tandem with the `replay.Chameleon` class to display and return
#     an arbitrary list of argument values in a command dialog.
#
#     Instead of manually setting a fixed list of arguments, we draw them from the
#     persistent data in the `replay.Chameleon().arguments` property. When we're done, we simply
#     deposit the resulting values back into the `replay.Chameleon().results` propery."""
#
#     def commander_arguments(self):
#         return replay.Chameleon().arguments
#
#     def commander_execute(self, msg, flags):
#         # Note that we use the `commander_argStrings` method rather than the
#         # typical `commander_args` because we don't want to alter the strings
#         # before sending them to the parser.
#         replay.Chameleon().results = self.commander_argStrings()
#
# lx.bless(ChameleonCommandClass, 'replay.chameleon')
