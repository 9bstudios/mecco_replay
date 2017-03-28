# python

import sys
import unittest
from unittest import TestCase, TextTestRunner, defaultTestLoader as loader
from cStringIO import StringIO
import lx, modo, replay
from mock import MagicMock
from mock import patch
from mock import call


class TestMacroCommand(unittest.TestCase):
    def test_render_LXM_no_prefix_no_args(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        self.assertEqual(cmd.render_LXM(), "layout.createOrClose")

    def test_render_LXM_no_args(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose")

    def test_render_LXM_one_simple_arg(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500'})]
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose width:500")

    def test_render_LXM_one_arg_with_space(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500 500'})]
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose width:\"500 500\"")

    def test_render_LXM_many_args(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500'}), dict({'argNames': 'height', 'argValues': '300'})]
        self.assertEqual(cmd.render_LXM(), "!layout.createOrClose width:500 height:300")

    def test_render_Python_no_prefix_no_args(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        self.assertEqual(cmd.render_Python(), "lx.eval(\'layout.createOrClose\')")

    def test_render_Python_no_args(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        self.assertEqual(cmd.render_Python(), "lx.eval(\'!layout.createOrClose\')")

    def test_render_Python_one_simple_arg(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500'})]
        self.assertEqual(cmd.render_Python(), "lx.eval(\'!layout.createOrClose width:500\')")

    def test_render_Python_one_arg_with_space(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500 500'})]
        self.assertEqual(cmd.render_Python(), 'lx.eval(\'!layout.createOrClose width:"500 500"\')')

    def test_render_Python_many_args(self):
        cmd = replay.MacroCommand()
        cmd.command = "layout.createOrClose" 
        cmd.prefix = "!"
        cmd.args = [dict({'argNames': 'width', 'argValues': '500'}), dict({'argNames': 'height', 'argValues': '300'})]
        self.assertEqual(cmd.render_Python(), "lx.eval(\'!layout.createOrClose width:500 height:300\')")

class ParserTest(unittest.TestCase):

    @patch.object(LXMParser, 'parseStream')
    @patch('%s.open' % __name__)
    def test_parse(self, fopen, parseStream):
        parser = LXMParser()

        parser.parse("foo.txt", "builder")
        fopen.assert_called_once_with("foo.txt", 'r')
        file = fopen.return_value
        parseStream.assert_called_once_with(file, "builder")
        file.close.assert_called_once_with()

    @patch.object(LXMParser, 'parseStream')
    @patch('%s.open' % __name__)
    def test_parseFail(self, fopen, parseStream):
        parser = LXMParser()
        parseStream.side_effect = LXMError(line=18, message="Some Error")

        with self.assertRaisesRegexp(LXMError, "Error in file foo.txt:18: Some Error"):
            parser.parse("foo.txt", "builder")
        fopen.assert_called_once_with("foo.txt", 'r')
        file = fopen.return_value
        parseStream.assert_called_once_with(file, "builder")
        file.close.assert_called_once_with()

    def test_commentsToSkip(self):
        parser = LXMParser()

        parser.in_suppress = False
        parser.expecting_comment_level = 7
        self.assertEqual(parser.commentsToSkip(), 7)

        parser.in_suppress = True
        parser.expecting_comment_level = 7
        self.assertEqual(parser.commentsToSkip(), 8)

    def test_uncomment(self):
        parser = LXMParser()

        self.assertEqual(parser.uncomment(""), ("", False))
        self.assertEqual(parser.uncomment(" \t\n\r"), (" \t\n\r", False))
        self.assertEqual(parser.uncomment("#"), ("", True))
        self.assertEqual(parser.uncomment("##"), ("#", True))
        self.assertEqual(parser.uncomment("# \t\n"), ("", True))
        self.assertEqual(parser.uncomment("#ab"), ("ab", True))
        self.assertEqual(parser.uncomment("# \t\nab"), ("ab", True))
        self.assertEqual(parser.uncomment("# \t\nab \t\n"), ("ab", True))
        self.assertEqual(parser.uncomment("# \t\n#ab \t\n"), ("#ab", True))
        self.assertEqual(parser.uncomment("# \t\n#\t\n ab \t\n"), ("#\t\n ab", True))

    @patch.object(LXMParser, 'uncomment')
    @patch.object(LXMParser, 'commentsToSkip')
    def test_stripLine(self, commentsToSkip, uncomment):
        parser = LXMParser()

        uncomment.side_effect = [('a', True), ('b', True), ('c', True), ('d', True), ('e', True)]
        commentsToSkip.return_value = 5
        str = MagicMock()
        str.strip = MagicMock(return_value="aa")
        self.assertEqual(parser.stripLine(str), 'e')
        str.strip.assert_called_once_with()
        commentsToSkip.assert_called_once_with()
        self.assertEqual(uncomment.call_args_list, [call('aa'), call('a'), call('b'), call('c'), call('d')])

        uncomment.reset_mock()
        commentsToSkip.reset_mock()
        uncomment.side_effect = [('a', True), ('b', True), ('c', False), ('d', True), ('e', True)]
        commentsToSkip.return_value = 5
        str = MagicMock()
        str.strip = MagicMock(return_value="aa")
        self.assertEqual(parser.stripLine(str), 'c')
        str.strip.assert_called_once_with()
        commentsToSkip.assert_called_once_with()
        self.assertEqual(uncomment.call_args_list, [call('aa'), call('a'), call('b')])

    def test_handleNonCommentLine(self):
        parser = LXMParser()

        parser.type = "LXM"
        parser.in_suppress = False
        parser.builder = MagicMock()
        parser.handleNonCommentLine("kuku")
        parser.builder.buildCommand.assert_called_once_with("kuku", False)

        parser.type = "LXM"
        parser.in_suppress = True
        parser.builder = MagicMock()
        parser.handleNonCommentLine("kuku")
        parser.builder.buildCommand.assert_called_once_with("kuku", True)

        parser.type = "PY"
        parser.in_suppress = False
        parser.builder = MagicMock()
        parser.handleNonCommentLine("lx.eval(\"kuku\")")
        parser.builder.buildCommand.assert_called_once_with("kuku", False)

        parser.type = "PY"
        parser.in_suppress = True
        parser.builder = MagicMock()
        parser.handleNonCommentLine("lx.eval(\"kuku\")")
        parser.builder.buildCommand.assert_called_once_with("kuku", True)

        parser.type = "PY"
        parser.line_index = 18
        parser.in_suppress = True
        parser.builder = MagicMock()
        with self.assertRaisesRegexp(LXMError, "Error in file None:18: Wrong python command") as err:
            parser.handleNonCommentLine("error lx.eval(\"kuku\")")
        parser.builder.buildCommand.assert_not_called()

    def test_isBlockStart(self):
        parser = LXMParser()

        self.assertIsNone(parser.isBlockStart(""))
        self.assertIsNone(parser.isBlockStart("#"))
        self.assertIsNone(parser.isBlockStart(" \t\r\n"))
        self.assertEqual(parser.isBlockStart("#Command Block Begin:<unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockStart("# Command Block Begin:<unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockStart("#  Command Block Begin:<unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockStart("#  Command Block Begin: <unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockStart("#  Command Block Begin:  <unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockStart("#  Command Block Begin:  <unnamed> "), "<unnamed>")
        self.assertEqual(parser.isBlockStart("#  Command Block Begin:  <unnamed>  "), "<unnamed>")
        self.assertEqual(parser.isBlockStart("#  Command Block Begin:  Tool Adjustment  "), "Tool Adjustment")
        self.assertIsNone(parser.isBlockStart("#  Command Block  Begin:  Tool Adjustment  "))
        self.assertIsNone(parser.isBlockStart("##  Command Block Begin:  Tool Adjustment  "))
        self.assertIsNone(parser.isBlockStart("# #  Command Block Begin:  Tool Adjustment  "))

    def test_isBlockEnd(self):
        parser = LXMParser()

        self.assertIsNone(parser.isBlockEnd(""))
        self.assertIsNone(parser.isBlockEnd("#"))
        self.assertIsNone(parser.isBlockEnd(" \t\r\n"))
        self.assertEqual(parser.isBlockEnd("#Command Block End:<unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("# Command Block End:<unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("#  Command Block End:<unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("#  Command Block End: <unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("#  Command Block End:  <unnamed>"), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("#  Command Block End:  <unnamed> "), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("#  Command Block End:  <unnamed>  "), "<unnamed>")
        self.assertEqual(parser.isBlockEnd("#  Command Block End:  Tool Adjustment  "), "Tool Adjustment")
        self.assertIsNone(parser.isBlockEnd("#  Command Block  End:  Tool Adjustment  "))
        self.assertIsNone(parser.isBlockEnd("##  Command Block End:  Tool Adjustment  "))
        self.assertIsNone(parser.isBlockEnd("# #  Command Block End:  Tool Adjustment  "))

    def test_isSuppress(self):
        parser = LXMParser()

        self.assertFalse(parser.isSuppress(""))
        self.assertFalse(parser.isSuppress("#"))
        self.assertFalse(parser.isSuppress(" \t\r\n"))
        self.assertFalse(parser.isSuppress("replay suppress"))
        self.assertFalse(parser.isSuppress(" replay suppress"))
        self.assertFalse(parser.isSuppress("#replay suppress"))
        self.assertTrue(parser.isSuppress("#replay suppress:"))
        self.assertFalse(parser.isSuppress("#replay suppress :"))
        self.assertTrue(parser.isSuppress("# replay suppress: "))
        self.assertTrue(parser.isSuppress("#  replay suppress: "))
        self.assertTrue(parser.isSuppress("#  replay suppress:  "))
        self.assertFalse(parser.isSuppress("#  replay  suppress:  "))
        self.assertFalse(parser.isSuppress(" #  replay suppress:  "))

    def test_isMeta(self):
        parser = LXMParser()

        self.assertIsNone(parser.isMeta(""))
        self.assertIsNone(parser.isMeta("#"))
        self.assertIsNone(parser.isMeta(" \t\r\n"))
        self.assertIsNone(parser.isMeta("replay"))
        self.assertIsNone(parser.isMeta("replay a:b"))
        self.assertIsNone(parser.isMeta("#replay a :b"))
        self.assertEqual(parser.isMeta("#replay a:b"), ('a', 'b'))
        self.assertEqual(parser.isMeta("#replay a:b b"), ('a', 'b b'))
        self.assertEqual(parser.isMeta("#replay a:b b "), ('a', 'b b'))
        self.assertIsNone(parser.isMeta("#replaya:b b "))
        self.assertIsNone(parser.isMeta("# replay a: b b "))
        self.assertEqual(parser.isMeta("#  replay a:b b "), ('a', 'b b'))
        self.assertEqual(parser.isMeta("#  replay a:\"b b\" "), ('a', '"b b"'))
        self.assertEqual(parser.isMeta("#  replay a:\"b b b\" "), ('a', '"b b b"'))

    @patch.object(LXMParser, 'isSuppress')
    def test_handleSuppress(self, isSuppress):
        parser = LXMParser()

        isSuppress.return_value = True
        parser.in_suppress = None
        parser.in_suppress_counter = None
        self.assertTrue(parser.handleSuppress("ggg"))
        self.assertTrue(parser.in_suppress)
        self.assertEqual(parser.in_suppress_counter, 2)
        isSuppress.assert_called_once_with("ggg")

        isSuppress.reset_mock()
        isSuppress.return_value = False
        parser.in_suppress = None
        parser.in_suppress_counter = None
        self.assertFalse(parser.handleSuppress("ggg"))
        self.assertIsNone(parser.in_suppress)
        self.assertIsNone(parser.in_suppress_counter)
        isSuppress.assert_called_once_with("ggg")

    @patch.object(LXMParser, 'isMeta')
    def test_handleMeta(self, isMeta):
        parser = LXMParser()

        parser.builder = MagicMock()
        parser.builder.buildMeta = MagicMock()
        isMeta.return_value = ("a", "b")
        self.assertTrue(parser.handleMeta("ggg"))
        isMeta.assert_called_once_with("ggg")
        parser.builder.buildMeta.assert_called_once_with("a", "b")

        parser.builder.buildMeta.reset_mock()
        isMeta.reset_mock()
        isMeta.return_value = None
        self.assertFalse(parser.handleMeta("ggg"))
        isMeta.assert_called_once_with("ggg")
        parser.builder.buildMeta.assert_not_called()

    @patch.object(LXMParser, 'isBlockStart')
    def test_handleBlockStart(self, isBlockStart):
        parser = LXMParser()

        parser.builder = MagicMock()
        parser.builder.buildBlockStart = MagicMock()
        parser.block_stack = [('l1', True), ('l2', False)]
        parser.in_suppress = True
        isBlockStart.return_value = 'l3'
        parser.expecting_comment_level = 11
        self.assertTrue(parser.handleBlockStart("ggg"))
        isBlockStart.assert_called_once_with("ggg")
        parser.builder.buildBlockStart.assert_called_once_with((('l1', True), ('l2', False), ('l3', True)), True)
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False), ('l3', True)])
        self.assertFalse(parser.in_suppress)
        self.assertEqual(parser.expecting_comment_level, 12)

        parser.builder.buildBlockStart.reset_mock()
        parser.block_stack = [('l1', True), ('l2', False)]
        parser.in_suppress = False
        isBlockStart.reset_mock()
        parser.expecting_comment_level = 11
        self.assertTrue(parser.handleBlockStart("ggg"))
        isBlockStart.assert_called_once_with("ggg")
        parser.builder.buildBlockStart.assert_called_once_with((('l1', True), ('l2', False), ('l3', False)), False)
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False), ('l3', False)])
        self.assertFalse(parser.in_suppress)
        self.assertEqual(parser.expecting_comment_level, 11)

        parser.builder.buildBlockStart.reset_mock()
        parser.block_stack = [('l1', True), ('l2', False)]
        parser.in_suppress = False
        isBlockStart.reset_mock()
        isBlockStart.return_value = None
        parser.expecting_comment_level = 11
        self.assertFalse(parser.handleBlockStart("ggg"))
        isBlockStart.assert_called_once_with("ggg")
        parser.builder.buildBlockStart.assert_not_called()
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False)])
        self.assertFalse(parser.in_suppress)
        self.assertEqual(parser.expecting_comment_level, 11)

    @patch.object(LXMParser, 'isBlockEnd')
    def test_handleBlockEnd(self, isBlockEnd):
        parser = LXMParser()

        parser.builder = MagicMock()
        parser.builder.buildBlockEnd = MagicMock()
        parser.block_stack = [('l1', True), ('l2', False), ('l3', True)]
        isBlockEnd.return_value = 'l3'
        parser.expecting_comment_level = 11
        self.assertTrue(parser.handleBlockEnd("ggg"))
        isBlockEnd.assert_called_once_with("ggg")
        parser.builder.buildBlockEnd.assert_called_once_with((('l1', True), ('l2', False), ('l3', True)))
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False)])
        self.assertEqual(parser.expecting_comment_level, 10)

        parser.builder.buildBlockEnd.reset_mock()
        parser.block_stack = [('l1', True), ('l2', False), ('l3', True)]
        isBlockEnd.reset_mock()
        parser.expecting_comment_level = 11
        self.assertTrue(parser.handleBlockEnd("ggg"))
        isBlockEnd.assert_called_once_with("ggg")
        parser.builder.buildBlockEnd.assert_called_once_with((('l1', True), ('l2', False), ('l3', True)))
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False)])
        self.assertEqual(parser.expecting_comment_level, 10)

        parser.builder.buildBlockEnd.reset_mock()
        parser.block_stack = [('l1', True), ('l2', False), ('l3', True)]
        isBlockEnd.reset_mock()
        isBlockEnd.return_value = 'l4'
        parser.expecting_comment_level = 11
        parser.line_index = 99
        with self.assertRaisesRegexp(LXMError, "Error in file None:99: Unexpected end of block 'l4' must be 'l3'"):
            parser.handleBlockEnd("ggg")
        isBlockEnd.assert_called_once_with("ggg")
        parser.builder.buildBlockEnd.assert_not_called()
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False), ('l3', True)])
        self.assertEqual(parser.expecting_comment_level, 11)

        parser.builder.buildBlockEnd.reset_mock()
        parser.block_stack = [('l1', True), ('l2', False), ('l3', True)]
        isBlockEnd.reset_mock()
        isBlockEnd.return_value = None
        parser.expecting_comment_level = 11
        self.assertFalse(parser.handleBlockEnd("ggg"))
        isBlockEnd.assert_called_once_with("ggg")
        parser.builder.buildBlockEnd.assert_not_called()
        self.assertEqual(parser.block_stack, [('l1', True), ('l2', False), ('l3', True)])
        self.assertEqual(parser.expecting_comment_level, 11)


    @patch.object(LXMParser, 'handleSuppress')
    @patch.object(LXMParser, 'handleMeta')
    @patch.object(LXMParser, 'handleBlockStart')
    @patch.object(LXMParser, 'handleBlockEnd')
    def test_handleCommentLine(self, handleBlockEnd, handleBlockStart, handleMeta, handleSuppress):
        parser = LXMParser()

        handleBlockEnd.return_value = True
        handleBlockStart.return_value = True
        handleMeta.return_value = True
        handleSuppress.return_value = True
        parser.builder = MagicMock()
        parser.builder.buildComment = MagicMock()
        parser.handleCommentLine("lll")
        handleSuppress.assert_called_once_with("lll")
        handleSuppress.reset_mock()
        handleMeta.assert_not_called()
        handleBlockStart.assert_not_called()
        handleBlockEnd.assert_not_called()
        parser.builder.buildComment.assert_not_called()

        handleBlockEnd.return_value = True
        handleBlockStart.return_value = True
        handleMeta.return_value = True
        handleSuppress.return_value = False
        parser.builder = MagicMock()
        parser.builder.buildComment = MagicMock()
        parser.handleCommentLine("lll")
        handleSuppress.assert_called_once_with("lll")
        handleSuppress.reset_mock()
        handleMeta.assert_called_once_with("lll")
        handleMeta.reset_mock()
        handleBlockStart.assert_not_called()
        handleBlockEnd.assert_not_called()
        parser.builder.buildComment.assert_not_called()

        handleBlockEnd.return_value = True
        handleBlockStart.return_value = True
        handleMeta.return_value = False
        handleSuppress.return_value = False
        parser.builder = MagicMock()
        parser.builder.buildComment = MagicMock()
        parser.handleCommentLine("lll")
        handleSuppress.assert_called_once_with("lll")
        handleSuppress.reset_mock()
        handleMeta.assert_called_once_with("lll")
        handleMeta.reset_mock()
        handleBlockStart.assert_called_once_with("lll")
        handleBlockStart.reset_mock()
        handleBlockEnd.assert_not_called()
        parser.builder.buildComment.assert_not_called()

        handleBlockEnd.return_value = True
        handleBlockStart.return_value = False
        handleMeta.return_value = False
        handleSuppress.return_value = False
        parser.builder = MagicMock()
        parser.builder.buildComment = MagicMock()
        parser.handleCommentLine("lll")
        handleSuppress.assert_called_once_with("lll")
        handleSuppress.reset_mock()
        handleMeta.assert_called_once_with("lll")
        handleMeta.reset_mock()
        handleBlockStart.assert_called_once_with("lll")
        handleBlockStart.reset_mock()
        handleBlockEnd.assert_called_once_with("lll")
        handleBlockEnd.reset_mock()
        parser.builder.buildComment.assert_not_called()

        handleBlockEnd.return_value = False
        handleBlockStart.return_value = False
        handleMeta.return_value = False
        handleSuppress.return_value = False
        parser.builder = MagicMock()
        parser.builder.buildComment = MagicMock()
        parser.handleCommentLine("lll")
        handleSuppress.assert_called_once_with("lll")
        handleMeta.assert_called_once_with("lll")
        handleBlockStart.assert_called_once_with("lll")
        handleBlockEnd.assert_called_once_with("lll")
        parser.builder.buildComment.assert_called_once_with("lll")


    @patch.object(LXMParser, 'handleNonCommentLine')
    @patch.object(LXMParser, 'handleCommentLine')
    @patch.object(LXMParser, 'stripLine')
    def test_parseLine(self, stripLine, handleCommentLine, handleNonCommentLine):
        parser = LXMParser()

        stripLine.return_value = "bbb"
        parser.parseLine("aaa")
        stripLine.assert_called_with("aaa")
        stripLine.reset_mock()
        handleCommentLine.assert_not_called()
        handleNonCommentLine.assert_called_once_with("bbb")
        handleNonCommentLine.reset_mock()

        stripLine.return_value = "#bbb"
        parser.parseLine("aaa")
        stripLine.assert_called_with("aaa")
        handleNonCommentLine.assert_not_called()
        handleCommentLine.assert_called_once_with("#bbb")

    @patch.object(LXMParser, 'parseLine')
    def test_readLines(self, parseLine):
        parser = LXMParser()

        parser.line_index = 1
        parser.in_suppress_counter = 4
        parser.in_suppress = True
        parser.readLines(["a", "b"])
        self.assertEqual(parser.line_index, 3)
        self.assertEqual(parser.in_suppress_counter, 2)
        self.assertTrue(parser.in_suppress)
        self.assertEqual(parseLine.call_args_list, [call('a'), call('b')])

        parseLine.reset_mock()
        parser.line_index = 1
        parser.in_suppress_counter = 3
        parser.in_suppress = True
        parser.readLines(["a", "b", "c"])
        self.assertEqual(parser.line_index, 4)
        self.assertEqual(parser.in_suppress_counter, 0)
        self.assertFalse(parser.in_suppress)
        self.assertEqual(parseLine.call_args_list, [call('a'), call('b'), call('c')])

    def test_readShabang(self):
        parser = LXMParser()

        file = MagicMock()
        file.readline = MagicMock(return_value="#LXMacro#")
        parser.builder = MagicMock()
        parser.builder.buildType = MagicMock()
        parser.readShabang(file)
        self.assertEqual(parser.type, "LXM")
        file.readline.assert_called_once_with()
        file.readline.reset_mock()
        parser.builder.buildType.assert_called_once_with("LXM")
        parser.builder.buildType.reset_mock()

        file.readline.return_value="# python"
        parser.builder = MagicMock()
        parser.builder.buildType = MagicMock()
        parser.readShabang(file)
        self.assertEqual(parser.type, "PY")
        file.readline.assert_called_once_with()
        file.readline.reset_mock()
        parser.builder.buildType.assert_called_once_with("PY")
        parser.builder.buildType.reset_mock()

        lx.out = MagicMock()
        file.readline.return_value="ELSE"
        parser.builder = MagicMock()
        parser.builder.buildType = MagicMock()
        parser.readShabang(file)
        self.assertEqual(parser.type, "LXM")
        file.readline.assert_called_once_with()
        file.readline.reset_mock()
        parser.builder.buildType.assert_called_once_with("LXM")
        parser.builder.buildType.reset_mock()
        lx.out.assert_called_once_with("Missing shabang")

    def test_initParser(self):
        parser = LXMParser()
        parser.initParser("kkk")

        self.assertEqual(parser.builder, "kkk")
        self.assertEqual(parser.line_index, 1)
        self.assertEqual(parser.type, None)
        self.assertEqual(parser.expecting_comment_level, 0)
        self.assertEqual(parser.in_suppress, False)
        self.assertEqual(parser.in_suppress_counter, 0)
        self.assertEqual(parser.block_stack, [])

    @patch.object(LXMParser, 'readLines')
    @patch.object(LXMParser, 'readShabang')
    @patch.object(LXMParser, 'initParser')
    def test_parseStream(self, initParser, readShabang, readLines):
        parser = LXMParser()
        parser.parseStream("file", "builder")

        initParser.assert_called_once_with("builder")
        readShabang.assert_called_once_with("file")
        readLines.assert_called_once_with("file")

def runUnitTest():
    moc_stdout = StringIO()
    runner = unittest.TextTestRunner(moc_stdout)
    suite = loader.loadTestsFromTestCase(TestMacroCommand)
    runner.run(suite)
    suite = loader.loadTestsFromTestCase(ParserTest)
    runner.run(suite)
    lx.out(moc_stdout.getvalue())

if __name__ == '__main__':
    runUnitTest()
