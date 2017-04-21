# python

import lx, modo, replay, traceback, os, sys, filecmp
import tempfile
import pyperclip

import unittest
from unittest import TestCase, TextTestRunner, defaultTestLoader as loader
from cStringIO import StringIO

from replay_lineInsert import UndoLineInsert
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
        
    def test_lineInsertUndoRedo(self):
        lx.eval('replay.fileClose prompt_save:false')
        lineInsert1 = UndoLineInsert('tool.set preset:"prim.cube" mode:on', "BtnName1", [0])
        lineInsert2 = UndoLineInsert('tool.set preset:"prim.sphere" mode:on', "BtnName2", [1])
        lineInsert3 = UndoLineInsert('tool.set preset:"prim.cone" mode:on', "BtnName3", [2])
        lineInsert1.undo_Forward()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].name, "BtnName1")
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertTrue(macro.node_for_path([0]).selected)
        
        lineInsert2.undo_Forward()
        self.assertEqual(len(macro.children), 2)
        self.assertEqual(macro.children[0].name, "BtnName1")
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        self.assertEqual(macro.children[1].name, "BtnName2")
        self.assertEqual(len(macro.children[1].args), 5)
        self.assertEqual(macro.children[1].args[0].value, "prim.sphere")
        self.assertFalse(macro.node_for_path([0]).selected)
        self.assertTrue(macro.node_for_path([1]).selected)
        
        # Select all. first is primary
        macro.node_for_path([1]).selected = True
        macro.node_for_path([0]).selected = True
        
        lineInsert3.undo_Forward()
        self.assertEqual(len(macro.children), 3)
        self.assertEqual(macro.children[0].name, "BtnName1")
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        self.assertEqual(macro.children[1].name, "BtnName2")
        self.assertEqual(len(macro.children[1].args), 5)
        self.assertEqual(macro.children[1].args[0].value, "prim.sphere")
        
        self.assertEqual(macro.children[2].name, "BtnName3")
        self.assertEqual(len(macro.children[2].args), 5)
        self.assertEqual(macro.children[2].args[0].value, "prim.cone")
        self.assertFalse(macro.node_for_path([0]).selected)
        self.assertFalse(macro.node_for_path([1]).selected)
        self.assertTrue(macro.node_for_path([2]).selected)
        
        lineInsert3.undo_Reverse()
        self.assertEqual(len(macro.children), 2)
        self.assertEqual(macro.children[0].name, "BtnName1")
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        self.assertEqual(macro.children[1].name, "BtnName2")
        self.assertEqual(len(macro.children[1].args), 5)
        self.assertEqual(macro.children[1].args[0].value, "prim.sphere")
        self.assertTrue(macro.node_for_path([0]).selected)
        self.assertTrue(macro.node_for_path([1]).selected)
        
        lineInsert2.undo_Reverse()
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(macro.children[0].name, "BtnName1")
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        self.assertTrue(macro.node_for_path([0]).selected)

        lineInsert1.undo_Reverse()
        self.assertEqual(len(macro.children), 0)
        
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
        replay.RecordingCache().clear()
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
        
        
from replay_argEdit import UndoArgEdit
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
        
    def test_argEditUndoRedo(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineSelect 0;0')
        #x.eval('replay.argEdit argName:preset value:prim.sphere')
        argEdit = UndoArgEdit(False, "prim.sphere", [[0, 0]])
        argEdit.undo_Forward()
        
        macro = replay.Macro()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, " ")
        self.assertEqual(macro.children[0].args[0].value, "prim.sphere")
        
        argEdit.undo_Reverse()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, " ")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
        argEditAs1 = UndoArgEdit(True, "val1", [[0, 0]])
        argEditAs2 = UndoArgEdit(True, "val2", [[0, 0]])
        
        argEditAs1.undo_Forward()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, "%")
        self.assertEqual(macro.children[0].args[0].value, "val1")
        
        argEditAs2.undo_Forward()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, "%")
        self.assertEqual(macro.children[0].args[0].value, "val2")
        
        argEditAs2.undo_Reverse()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, "%")
        self.assertEqual(macro.children[0].args[0].value, "val1")
        
        argEditAs1.undo_Reverse()
        
        self.assertEqual(len(macro.children), 1)
        self.assertEqual(len(macro.children[0].args), 5)
        self.assertEqual(macro.children[0].args[0].display_prefix, " ")
        self.assertEqual(macro.children[0].args[0].value, "prim.cube")
        
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
        
class TestFileClose(unittest.TestCase):
    def test_fileClose(self):
        lx.eval('replay.fileClose prompt_save:false')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on}')
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 3)
        lx.eval('replay.fileClose prompt_save:false')
        self.assertEqual(len(macro.children), 0)
        
class TestFileExportOpen(unittest.TestCase):
    def test_fileExportOpenLXM(self):
        lx.eval('replay.fileClose prompt_save:false')
        file_path = os.path.join(tempfile.gettempdir(), "test.lxm")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileExport format:lxm destination:"%s"' % file_path)
        lx.eval('replay.fileClose prompt_save:false')
        
        lx.eval('replay.fileOpen path:"%s"' % file_path)
        os.remove(file_path)
        
        macro = replay.Macro()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 3)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Other Name")
        self.assertTrue(macro.children[0].direct_suppress)
        self.assertEqual(macro.children[0].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[0].row_color, "red")
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

        
        self.assertEqual(macro.children[1].columns['name'].value, "")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(len(macro.children[1].children), 2)
        
        self.assertEqual(macro.node_for_path([1, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([1, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([1, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([1, 0]).args), 5)
        self.assertEqual(macro.node_for_path([1, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([1, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([1, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([1, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([1, 1]).args), 5)
        self.assertEqual(macro.node_for_path([1, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[2].command, "tool.set")
        self.assertEqual(macro.children[2].name, "Set Tool")
        self.assertFalse(macro.children[2].direct_suppress)
        self.assertEqual(macro.children[2].user_comment_before, [])
        self.assertEqual(macro.children[2].row_color, "orange")
        self.assertEqual(len(macro.children[2].args), 5)
        self.assertEqual(macro.children[2].args[0].argName, "preset")
        self.assertEqual(macro.children[2].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[2].args[1].argName, "mode")
        self.assertEqual(macro.children[2].args[1].value, "off")
        self.assertEqual(macro.children[2].args[2].argName, "task")
        self.assertEqual(macro.children[2].args[2].value, None)
        self.assertEqual(macro.children[2].args[3].argName, "snap")
        self.assertEqual(macro.children[2].args[3].value, None)
        self.assertEqual(macro.children[2].args[4].argName, "rawquery")
        self.assertEqual(macro.children[2].args[4].value, None)
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_fileExportOpenPy(self):
        lx.eval('replay.fileClose prompt_save:false')
        file_path = os.path.join(tempfile.gettempdir(), "test.py")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileExport format:py destination:"%s"' % file_path)
        lx.eval('replay.fileClose prompt_save:false')
        
        lx.eval('replay.fileOpen path:"%s"' % file_path)
        os.remove(file_path)
        
        macro = replay.Macro()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 3)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Other Name")
        self.assertTrue(macro.children[0].direct_suppress)
        self.assertEqual(macro.children[0].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[0].row_color, "red")
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

        
        self.assertEqual(macro.children[1].columns['name'].value, "")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(len(macro.children[1].children), 2)
        
        self.assertEqual(macro.node_for_path([1, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([1, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([1, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([1, 0]).args), 5)
        self.assertEqual(macro.node_for_path([1, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([1, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([1, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([1, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([1, 1]).args), 5)
        self.assertEqual(macro.node_for_path([1, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[2].command, "tool.set")
        self.assertEqual(macro.children[2].name, "Set Tool")
        self.assertFalse(macro.children[2].direct_suppress)
        self.assertEqual(macro.children[2].user_comment_before, [])
        self.assertEqual(macro.children[2].row_color, "orange")
        self.assertEqual(len(macro.children[2].args), 5)
        self.assertEqual(macro.children[2].args[0].argName, "preset")
        self.assertEqual(macro.children[2].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[2].args[1].argName, "mode")
        self.assertEqual(macro.children[2].args[1].value, "off")
        self.assertEqual(macro.children[2].args[2].argName, "task")
        self.assertEqual(macro.children[2].args[2].value, None)
        self.assertEqual(macro.children[2].args[3].argName, "snap")
        self.assertEqual(macro.children[2].args[3].value, None)
        self.assertEqual(macro.children[2].args[4].argName, "rawquery")
        self.assertEqual(macro.children[2].args[4].value, None)
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_fileExportOpenJson(self):
        lx.eval('replay.fileClose prompt_save:false')
        file_path = os.path.join(tempfile.gettempdir(), "test.json")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileExport format:json destination:"%s"' % file_path)
        lx.eval('replay.fileClose prompt_save:false')
        
        lx.eval('replay.fileOpen path:"%s"' % file_path)
        os.remove(file_path)
        
        macro = replay.Macro()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 3)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Other Name")
        self.assertTrue(macro.children[0].direct_suppress)
        self.assertEqual(macro.children[0].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[0].row_color, "red")
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

        
        self.assertEqual(macro.children[1].columns['name'].value, "")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(len(macro.children[1].children), 2)
        
        self.assertEqual(macro.node_for_path([1, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([1, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([1, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([1, 0]).args), 5)
        self.assertEqual(macro.node_for_path([1, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([1, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([1, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([1, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([1, 1]).args), 5)
        self.assertEqual(macro.node_for_path([1, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[2].command, "tool.set")
        self.assertEqual(macro.children[2].name, "Set Tool")
        self.assertFalse(macro.children[2].direct_suppress)
        self.assertEqual(macro.children[2].user_comment_before, [])
        self.assertEqual(macro.children[2].row_color, "orange")
        self.assertEqual(len(macro.children[2].args), 5)
        self.assertEqual(macro.children[2].args[0].argName, "preset")
        self.assertEqual(macro.children[2].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[2].args[1].argName, "mode")
        self.assertEqual(macro.children[2].args[1].value, "off")
        self.assertEqual(macro.children[2].args[2].argName, "task")
        self.assertEqual(macro.children[2].args[2].value, None)
        self.assertEqual(macro.children[2].args[3].argName, "snap")
        self.assertEqual(macro.children[2].args[3].value, None)
        self.assertEqual(macro.children[2].args[4].argName, "rawquery")
        self.assertEqual(macro.children[2].args[4].value, None)
        
        lx.eval('replay.fileClose prompt_save:false')
        
class TestFileExportInsert(unittest.TestCase):
    def test_fileExportInsertLXM(self):
        lx.eval('replay.fileClose prompt_save:false')
        file_path = os.path.join(tempfile.gettempdir(), "test.lxm")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
     
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
                     
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileExport format:lxm destination:"%s"' % file_path)
        lx.eval('replay.fileClose prompt_save:false')
        
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        lx.eval('replay.lineSelect 0')
        
        lx.eval('replay.fileInsert path:"%s"' % file_path)
        os.remove(file_path)
        
        macro = replay.Macro()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 5)
        self.assertEqual(macro.children[1].command, "tool.set")
        self.assertEqual(macro.children[1].name, "Other Name")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(macro.children[1].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[1].row_color, "red")
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
        self.assertEqual(macro.children[1].args[4].value, None)

        
        self.assertEqual(macro.children[2].columns['name'].value, "")
        self.assertTrue(macro.children[2].direct_suppress)
        self.assertEqual(len(macro.children[2].children), 2)
        
        self.assertEqual(macro.node_for_path([2, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([2, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([2, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([2, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([2, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([2, 0]).args), 5)
        self.assertEqual(macro.node_for_path([2, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([2, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([2, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([2, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([2, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([2, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([2, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([2, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([2, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([2, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([2, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([2, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([2, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([2, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([2, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([2, 1]).args), 5)
        self.assertEqual(macro.node_for_path([2, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([2, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([2, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([2, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([2, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([2, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([2, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([2, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([2, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([2, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[3].command, "tool.set")
        self.assertEqual(macro.children[3].name, "Set Tool")
        self.assertFalse(macro.children[3].direct_suppress)
        self.assertEqual(macro.children[3].user_comment_before, [])
        self.assertEqual(macro.children[3].row_color, "orange")
        self.assertEqual(len(macro.children[3].args), 5)
        self.assertEqual(macro.children[3].args[0].argName, "preset")
        self.assertEqual(macro.children[3].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[3].args[1].argName, "mode")
        self.assertEqual(macro.children[3].args[1].value, "off")
        self.assertEqual(macro.children[3].args[2].argName, "task")
        self.assertEqual(macro.children[3].args[2].value, None)
        self.assertEqual(macro.children[3].args[3].argName, "snap")
        self.assertEqual(macro.children[3].args[3].value, None)
        self.assertEqual(macro.children[3].args[4].argName, "rawquery")
        self.assertEqual(macro.children[3].args[4].value, None)
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_fileExportInsertPy(self):
        lx.eval('replay.fileClose prompt_save:false')
        file_path = os.path.join(tempfile.gettempdir(), "test.py")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileExport format:py destination:"%s"' % file_path)
        lx.eval('replay.fileClose prompt_save:false')
        
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        lx.eval('replay.lineSelect 0')
        
        lx.eval('replay.fileInsert path:"%s"' % file_path)
        os.remove(file_path)
        
        macro = replay.Macro()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 5)
        self.assertEqual(macro.children[1].command, "tool.set")
        self.assertEqual(macro.children[1].name, "Other Name")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(macro.children[1].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[1].row_color, "red")
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
        self.assertEqual(macro.children[1].args[4].value, None)

        
        self.assertEqual(macro.children[2].columns['name'].value, "")
        self.assertTrue(macro.children[2].direct_suppress)
        self.assertEqual(len(macro.children[2].children), 2)
        
        self.assertEqual(macro.node_for_path([2, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([2, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([2, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([2, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([2, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([2, 0]).args), 5)
        self.assertEqual(macro.node_for_path([2, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([2, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([2, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([2, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([2, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([2, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([2, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([2, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([2, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([2, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([2, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([2, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([2, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([2, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([2, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([2, 1]).args), 5)
        self.assertEqual(macro.node_for_path([2, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([2, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([2, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([2, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([2, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([2, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([2, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([2, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([2, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([2, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[3].command, "tool.set")
        self.assertEqual(macro.children[3].name, "Set Tool")
        self.assertFalse(macro.children[3].direct_suppress)
        self.assertEqual(macro.children[3].user_comment_before, [])
        self.assertEqual(macro.children[3].row_color, "orange")
        self.assertEqual(len(macro.children[3].args), 5)
        self.assertEqual(macro.children[3].args[0].argName, "preset")
        self.assertEqual(macro.children[3].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[3].args[1].argName, "mode")
        self.assertEqual(macro.children[3].args[1].value, "off")
        self.assertEqual(macro.children[3].args[2].argName, "task")
        self.assertEqual(macro.children[3].args[2].value, None)
        self.assertEqual(macro.children[3].args[3].argName, "snap")
        self.assertEqual(macro.children[3].args[3].value, None)
        self.assertEqual(macro.children[3].args[4].argName, "rawquery")
        self.assertEqual(macro.children[3].args[4].value, None)
        
        lx.eval('replay.fileClose prompt_save:false')
        
    def test_fileExportInsertJson(self):
        lx.eval('replay.fileClose prompt_save:false')
        file_path = os.path.join(tempfile.gettempdir(), "test.json")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileExport format:json destination:"%s"' % file_path)
        lx.eval('replay.fileClose prompt_save:false')
        
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        lx.eval('replay.lineSelect 0')
        
        lx.eval('replay.fileInsert path:"%s"' % file_path)

        os.remove(file_path)
        
        macro = replay.Macro()
        
        macro = replay.Macro()
        self.assertEqual(len(macro.children), 5)
        self.assertEqual(macro.children[1].command, "tool.set")
        self.assertEqual(macro.children[1].name, "Other Name")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(macro.children[1].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[1].row_color, "red")
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
        self.assertEqual(macro.children[1].args[4].value, None)

        
        self.assertEqual(macro.children[2].columns['name'].value, "")
        self.assertTrue(macro.children[2].direct_suppress)
        self.assertEqual(len(macro.children[2].children), 2)
        
        self.assertEqual(macro.node_for_path([2, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([2, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([2, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([2, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([2, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([2, 0]).args), 5)
        self.assertEqual(macro.node_for_path([2, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([2, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([2, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([2, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([2, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([2, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([2, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([2, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([2, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([2, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([2, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([2, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([2, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([2, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([2, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([2, 1]).args), 5)
        self.assertEqual(macro.node_for_path([2, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([2, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([2, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([2, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([2, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([2, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([2, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([2, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([2, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([2, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[3].command, "tool.set")
        self.assertEqual(macro.children[3].name, "Set Tool")
        self.assertFalse(macro.children[3].direct_suppress)
        self.assertEqual(macro.children[3].user_comment_before, [])
        self.assertEqual(macro.children[3].row_color, "orange")
        self.assertEqual(len(macro.children[3].args), 5)
        self.assertEqual(macro.children[3].args[0].argName, "preset")
        self.assertEqual(macro.children[3].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[3].args[1].argName, "mode")
        self.assertEqual(macro.children[3].args[1].value, "off")
        self.assertEqual(macro.children[3].args[2].argName, "task")
        self.assertEqual(macro.children[3].args[2].value, None)
        self.assertEqual(macro.children[3].args[3].argName, "snap")
        self.assertEqual(macro.children[3].args[3].value, None)
        self.assertEqual(macro.children[3].args[4].argName, "rawquery")
        self.assertEqual(macro.children[3].args[4].value, None)
        
        lx.eval('replay.fileClose prompt_save:false')      

class TestFileSaveOpen(unittest.TestCase):
    def test_fileSaveOpen(self):
        macro = replay.Macro()
        macro.unsaved_changes = False
        lx.eval('replay.fileNew')
        file_path = os.path.join(tempfile.gettempdir(), "test.lxm")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.cube" mode:on} ButtonName:"Other Name"')
        replay.RecordingCache().clear()
        replay.RecordingCache().add_command('tool.set preset:"prim.cube" mode:on')
        replay.RecordingCache().add_command('tool.set preset:"prim.sphere" mode:off')
        lx.eval("replay.lastBlockInsert")
        lx.eval('replay.lineInsert command:{tool.set preset:"prim.sphere" mode:off}')
        
        lx.eval('replay.lineSelect 0')
        lx.eval('replay.lineComment "first"')
        lx.eval('replay.lineColor red')
        lx.eval('replay.lineComment "last"')
        lx.eval('replay.lineSuppress')
        
        lx.eval('replay.lineSelect 1;0')
        lx.eval('replay.lineComment "first1"')
        lx.eval('replay.lineColor magenta')
        lx.eval('replay.lineComment "last1"')
        lx.eval('replay.lineSuppress')
     
        lx.eval('replay.lineSelect 1')
        lx.eval('replay.lineSuppress')
                     
        lx.eval('replay.lineSelect 2')
        lx.eval('replay.lineColor orange')
        
        lx.eval('replay.fileSave path:"%s"' % file_path)
        macro.unsaved_changes = False
        lx.eval('replay.fileNew')
        
        lx.eval('replay.fileOpen path:"%s"' % file_path)
        os.remove(file_path)
        
        self.assertEqual(len(macro.children), 3)
        self.assertEqual(macro.children[0].command, "tool.set")
        self.assertEqual(macro.children[0].name, "Other Name")
        self.assertTrue(macro.children[0].direct_suppress)
        self.assertEqual(macro.children[0].user_comment_before, ["first", "last"])
        self.assertEqual(macro.children[0].row_color, "red")
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

        
        self.assertEqual(macro.children[1].columns['name'].value, "")
        self.assertTrue(macro.children[1].direct_suppress)
        self.assertEqual(len(macro.children[1].children), 2)
        
        self.assertEqual(macro.node_for_path([1, 0]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 0]).name, "Set Tool")
        self.assertTrue(macro.node_for_path([1, 0]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 0]).user_comment_before, ["first1", "last1"])
        self.assertEqual(macro.node_for_path([1, 0]).row_color, "magenta")
        self.assertEqual(len(macro.node_for_path([1, 0]).args), 5)
        self.assertEqual(macro.node_for_path([1, 0]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 0]).args[0].value, "prim.cube")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 0]).args[1].value, "on")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 0]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 0]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 0]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 0]).args[4].value, None)
        
        self.assertEqual(macro.node_for_path([1, 1]).command, "tool.set")
        self.assertEqual(macro.node_for_path([1, 1]).name, "Set Tool")
        self.assertFalse(macro.node_for_path([1, 1]).direct_suppress)
        self.assertEqual(macro.node_for_path([1, 1]).user_comment_before, [])
        self.assertEqual(macro.node_for_path([1, 1]).row_color, None)
        self.assertEqual(len(macro.node_for_path([1, 1]).args), 5)
        self.assertEqual(macro.node_for_path([1, 1]).args[0].argName, "preset")
        self.assertEqual(macro.node_for_path([1, 1]).args[0].value, "prim.sphere")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].argName, "mode")
        self.assertEqual(macro.node_for_path([1, 1]).args[1].value, "off")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].argName, "task")
        self.assertEqual(macro.node_for_path([1, 1]).args[2].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[3].argName, "snap")
        self.assertEqual(macro.node_for_path([1, 1]).args[3].value, None)
        self.assertEqual(macro.node_for_path([1, 1]).args[4].argName, "rawquery")
        self.assertEqual(macro.node_for_path([1, 1]).args[4].value, None)
        
        self.assertEqual(macro.children[2].command, "tool.set")
        self.assertEqual(macro.children[2].name, "Set Tool")
        self.assertFalse(macro.children[2].direct_suppress)
        self.assertEqual(macro.children[2].user_comment_before, [])
        self.assertEqual(macro.children[2].row_color, "orange")
        self.assertEqual(len(macro.children[2].args), 5)
        self.assertEqual(macro.children[2].args[0].argName, "preset")
        self.assertEqual(macro.children[2].args[0].value, "prim.sphere")
        self.assertEqual(macro.children[2].args[1].argName, "mode")
        self.assertEqual(macro.children[2].args[1].value, "off")
        self.assertEqual(macro.children[2].args[2].argName, "task")
        self.assertEqual(macro.children[2].args[2].value, None)
        self.assertEqual(macro.children[2].args[3].argName, "snap")
        self.assertEqual(macro.children[2].args[3].value, None)
        self.assertEqual(macro.children[2].args[4].argName, "rawquery")
        self.assertEqual(macro.children[2].args[4].value, None)
        
        macro.unsaved_changes = False
        lx.eval('replay.fileNew')
        
class TestFileOpenAddRecent(unittest.TestCase):
    def test_lineInsert(self):
        lx.eval('user.value mecco_replay_recent_files ""')
        lx.eval('replay.fileOpenAddRecent "path1"')
        
        existing_paths = lx.eval('user.value mecco_replay_recent_files ?')
        self.assertEqual(existing_paths, "path1;")
        
        lx.eval('replay.fileOpenAddRecent "path2"')
        existing_paths = lx.eval('user.value mecco_replay_recent_files ?')
        self.assertEqual(existing_paths, "path2;path1;")
        
def runUnitTest():
    moc_stdout = StringIO()
        
    runner = unittest.TextTestRunner(moc_stdout)
    suite = loader.loadTestsFromTestCase(TestLineInsert)
    suite.addTests(loader.loadTestsFromTestCase(TestLineDelete))
    suite.addTests(loader.loadTestsFromTestCase(TestArgClear))
    suite.addTests(loader.loadTestsFromTestCase(TestArgEdit))
    suite.addTests(loader.loadTestsFromTestCase(TestArgEditFCL))
    suite.addTests(loader.loadTestsFromTestCase(TestClipboardCopy))
    suite.addTests(loader.loadTestsFromTestCase(TestClipboardCut))
    suite.addTests(loader.loadTestsFromTestCase(TestClipboardPast))
    suite.addTests(loader.loadTestsFromTestCase(TestDelete))
    suite.addTests(loader.loadTestsFromTestCase(TestFileClose))
    suite.addTests(loader.loadTestsFromTestCase(TestFileExportOpen))
    suite.addTests(loader.loadTestsFromTestCase(TestFileExportInsert))
    suite.addTests(loader.loadTestsFromTestCase(TestFileSaveOpen))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOpenAddRecent))
    runner.run(suite)
    lx.out(moc_stdout.getvalue())
    
if __name__ == '__main__':
    runUnitTest()
    