# python

import sys
import unittest
from unittest import TestCase, TextTestRunner, defaultTestLoader as loader
from cStringIO import StringIO
import lx, modo, replay_commander, replay

class TestReplayMacroCommand(unittest.TestCase):
    def test_render_LXM_no_prefix_no_args(self):
        cmd = replay.ReplayMacroCommand(None)
        cmd.command = "layout.createOrClose" 
        self.assertEqual(cmd.render_LXM(), "layout.createOrClose")

    def test_render_LXM_no_args(self):
        cmd = replay.ReplayMacroCommand(None)
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose")

    def test_render_LXM_one_simple_arg(self):
        cmd = replay.ReplayMacroCommand(None)
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500'})]
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose width:500")

    def test_render_LXM_one_arg_with_space(self):
        cmd = replay.ReplayMacroCommand(None)
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500 500'})]
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose width:\"500 500\"")

    def test_render_LXM_many_args(self):
        cmd = replay.ReplayMacroCommand(None)
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500'}), dict({'argNames': 'height', 'argValues': '300'})]
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose width:500 height:300")

def runUnitTest():
    moc_stdout = StringIO()
    runner = unittest.TextTestRunner(moc_stdout)
    suite = loader.loadTestsFromTestCase(TestReplayMacroCommand)
    runner.run(suite)
    lx.out(moc_stdout.getvalue())

if __name__ == '__main__':
    runUnitTest()