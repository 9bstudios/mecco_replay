# python

import lx, modo, replay, traceback, os, sys, filecmp
import tempfile

import unittest
from unittest import TestCase, TextTestRunner, defaultTestLoader as loader
from cStringIO import StringIO

class TestLineInsert(unittest.TestCase):
    def test_lineInsert(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].prefix, None)
        self.assertEqual(len(macro.children[0].args), 5)
        
def runUnitTest():
    moc_stdout = StringIO()
    runner = unittest.TextTestRunner(moc_stdout)
    suite = loader.loadTestsFromTestCase(TestLineInsert)
    runner.run(suite)
    lx.out(moc_stdout.getvalue())
    
if __name__ == '__main__':
    runUnitTest()
    