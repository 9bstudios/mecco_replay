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
        self.assertEqual(macro.children[0].prefix, ' ')
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "on")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        self.assertEqual(macro.children[0].args[4].value, None)
        
    def test_lineInsertPrefix(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{!tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].prefix, "!")
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "on")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        self.assertEqual(macro.children[0].args[4].value, None)
        
from replay_lineDelete import UndoLineDelete
class TestLineDelete(unittest.TestCase):
    def test_lineDelete(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineDelete')
        self.assertEqual(len(macro.children), 0)
        
    def test_lineDeleteUndoRedo(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)

        # Cannot use app.undo app.redo here. Have to do it manually
        lineDelete = UndoLineDelete([[0]])
        lineDelete.undo_Forward()
        self.assertEqual(len(macro.children), 0)
        
        lineDelete.undo_Reverse()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].prefix, ' ')
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "on")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        self.assertEqual(macro.children[0].args[4].value, None)
        
        lineDelete.undo_Forward()
        self.assertEqual(len(macro.children), 0)

        
def runUnitTest():
    moc_stdout = StringIO()
    runner = unittest.TextTestRunner(moc_stdout)
    suite = loader.loadTestsFromTestCase(TestLineInsert)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestLineDelete)
    runner.run(suite)
    lx.out(moc_stdout.getvalue())
    
if __name__ == '__main__':
    runUnitTest()
    