# python

import lx, modo, replay, traceback, os, sys, filecmp
import tempfile
import pyperclip

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
        self.assertEqual(macro.children[0].display_prefix, ' ')
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
        
        lx.eval('replay.fileClose prompt_save:false')
        
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
        
        lx.eval('replay.fileClose prompt_save:false')
        
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
        
        lx.eval('replay.fileClose prompt_save:false')
        
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
        self.assertEqual(macro.children[0].display_prefix, ' ')
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
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_lineDeleteUndoRedo_bug_114(self):
        lx.eval('replay.fileClose prompt_save:false')
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        lx.eval("replay.lastBlockInsert")
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)

        # Cannot use app.undo app.redo here. Have to do it manually
        lineDelete = UndoLineDelete([[0]])
        lineDelete.undo_Forward()
        self.assertEqual(len(macro.children), 0)
        
        lineDelete.undo_Reverse()
        self.assertEqual(len(macro.children), 1)
        
        lineDelete.undo_Forward()
        self.assertEqual(len(macro.children), 0)
        
        lx.eval('replay.fileClose prompt_save:false')

from replay_argClear import UndoArgClear
class TestArgClear(unittest.TestCase):
    def test_argClear(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        lx.eval('replay.lineSelect 0;0')
        lx.eval('replay.argClear')
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, None)
        
    def test_argClearUndoRedo(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        argClear = UndoArgClear([[0, 0]])
        argClear.undo_Forward()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, None)
    
        argClear.undo_Reverse()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        argClear.undo_Forward()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, None)
           
        lx.eval('replay.fileClose prompt_save:false')
        
        
class TestArgEdit(unittest.TestCase):
    def test_argEditArgument(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0;0')
        lx.eval('replay.argEdit argName:preset value:prim.sphere')
        
        macro = replay.Macro()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, " ")
        self.assertEqual(macro.children[0].args[0].value, "prim.sphere")
        
        lx.eval('replay.argEditAsString argName:preset value:prim.something')
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, "%")
        self.assertEqual(macro.children[0].args[0].value, "prim.something")
        
        val = lx.eval('replay.argEditAsString argName:preset ?')
        self.assertEqual(val, "prim.something")
        
        lx.eval('replay.fileClose prompt_save:false')

from replay_argEditFCL import CommandClass as ArgEditFCL
class TestArgEditFCL(unittest.TestCase):
    def test_argEditFCL(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0;0')
        
        argEditFCL = ArgEditFCL()
        self.assertEqual(argEditFCL.list_commands(), ["replay.argEdit preset ?"])
        
        lx.eval('replay.lineSelect 0')
        res = ["replay.argEdit preset ?", "replay.argEdit mode ?", "replay.argEdit task ?",
               "replay.argEdit snap ?", "replay.argEdit rawquery ?"]
        self.assertEqual(argEditFCL.list_commands(), res)
        
        lx.eval('replay.fileClose prompt_save:false')
       
class TestClipboardCopy(unittest.TestCase):
    def test_copy(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.clipboardCopy')
        
        self.assertEqual(pyperclip.paste(), '#LXMacro#\r\n# Made with Replay\r\n# mechanicalcolor.com\r\n\r\ntool.set preset:"prim.cube" mode:on\r\n')
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_copy_neg(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0;0')
        with self.assertRaises(Exception):
            lx.eval('!replay.clipboardCopy')

class TestClipboardCut(unittest.TestCase):
    def test_cut(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.clipboardCut')
        
        self.assertEqual(pyperclip.paste(), '#LXMacro#\r\n# Made with Replay\r\n# mechanicalcolor.com\r\n\r\ntool.set preset:"prim.cube" mode:on\r\n')
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 0)
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_cut_neg(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0;0')
        with self.assertRaises(Exception):
            lx.eval('!replay.clipboardCut')
      
from replay_clipboardPaste import UndoPaste
class TestClipboardPast(unittest.TestCase):
    def test_past(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:off}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 1')
        
        lx.eval('replay.clipboardCut')
        self.assertEqual(pyperclip.paste(), '#LXMacro#\r\n# Made with Replay\r\n# mechanicalcolor.com\r\n\r\ntool.set preset:"prim.cube" mode:on\r\n')
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)
       
        lx.eval('replay.clipboardPaste')
        self.assertEqual(len(macro.children), 2)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].display_prefix, ' ')
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
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_undo_redo(self):
        macro = replay.Macro()
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:off}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.clipboardCut')
        lx.eval('replay.lineSelect 0')

        paste = UndoPaste(pyperclip.paste(), [1], [0])
        
        paste.undo_Forward()
        self.assertEqual(len(macro.children), 2)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].display_prefix, ' ')
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "off")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        
        self.assertEqual(macro.children[1].command, "tool.set")
        self.assertEqual(macro.children[1].name, "Set Tool")
        self.assertEqual(macro.children[1].display_prefix, ' ')
        self.assertEqual(len(macro.children[1].args), 5)
        self.assertEqual(macro.children[1].args[0].argName, "preset")
        self.assertEqual(macro.children[1].args[0].value, "prim.cube")
        self.assertEqual(macro.children[1].args[1].argName, "mode")
        self.assertEqual(macro.children[1].args[1].value, "on")
        self.assertEqual(macro.children[1].args[2].argName, "task")
        self.assertEqual(macro.children[1].args[2].value, None)
        self.assertEqual(macro.children[1].args[3].argName, "snap")
        self.assertEqual(macro.children[1].args[3].value, None)
        self.assertEqual(macro.children[1].args[4].argName, "rawquery")
        
        paste.undo_Reverse()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].display_prefix, ' ')
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "off")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        
        paste.undo_Forward()
        self.assertEqual(len(macro.children), 2)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].display_prefix, ' ')
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "off")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        
        self.assertEqual(macro.children[1].command, "tool.set")
        self.assertEqual(macro.children[1].name, "Set Tool")
        self.assertEqual(macro.children[1].display_prefix, ' ')
        self.assertEqual(len(macro.children[1].args), 5)
        self.assertEqual(macro.children[1].args[0].argName, "preset")
        self.assertEqual(macro.children[1].args[0].value, "prim.cube")
        self.assertEqual(macro.children[1].args[1].argName, "mode")
        self.assertEqual(macro.children[1].args[1].value, "on")
        self.assertEqual(macro.children[1].args[2].argName, "task")
        self.assertEqual(macro.children[1].args[2].value, None)
        self.assertEqual(macro.children[1].args[3].argName, "snap")
        self.assertEqual(macro.children[1].args[3].value, None)
        self.assertEqual(macro.children[1].args[4].argName, "rawquery")
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_past_neg(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0;0')
        with self.assertRaises(Exception):
            lx.eval('!replay.clipboardPaste')
        
class TestDelete(unittest.TestCase):
    def test_delete(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)
        lx.eval('replay.lineSelect 0;0')
        lx.eval('replay.delete')
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Set Tool")
        self.assertEqual(macro.children[0].display_prefix, ' ')
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].argName, "preset")
        self.assertEqual(macro.children[0].args[0].value, None)
        self.assertEqual(macro.children[0].args[1].argName, "mode")
        self.assertEqual(macro.children[0].args[1].value, "on")
        self.assertEqual(macro.children[0].args[2].argName, "task")
        self.assertEqual(macro.children[0].args[2].value, None)
        self.assertEqual(macro.children[0].args[3].argName, "snap")
        self.assertEqual(macro.children[0].args[3].value, None)
        self.assertEqual(macro.children[0].args[4].argName, "rawquery")
        self.assertEqual(macro.children[0].args[4].value, None)

        lx.eval('replay.lineSelect 0')
        lx.eval('replay.delete')        
        self.assertEqual(len(macro.children), 0)
        
        lx.eval('replay.fileClose prompt_save:false')
        
        
def runUnitTest():
    moc_stdout = StringIO()
        
    runner = unittest.TextTestRunner(moc_stdout)
    suite = loader.loadTestsFromTestCase(TestLineInsert)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestLineDelete)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestArgClear)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestArgEdit)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestArgEditFCL)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestClipboardCopy)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestClipboardCut)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestClipboardPast)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(TestDelete)
    runner.run(suite)
    lx.out(moc_stdout.getvalue())
    
if __name__ == '__main__':
    runUnitTest()
    