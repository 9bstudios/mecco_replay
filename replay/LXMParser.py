# python

import re
import lx


class LXMBuilder:
    def buildType(self, type):
        pass

    def buildCommand(self, line, suppress):
        pass

    def buildBlockStart(self, block, suppress):
        pass

    def buildBlockEnd(self, block):
        pass

    def buildMeta(self, name, value):
        pass

    def buildComment(self, comment):
        pass

class LXMError(Exception):

    def __init__(self, **kwargs):

        self.line = kwargs.get('line', -1)
        self.file = kwargs.get('file', None)
        self.message = kwargs.get('message', None)

    def __str__(self):
        return "Error in file {file}:{line}: {msg}".format(file=self.file, line=self.line, msg=self.message)

class LXMParser(object):

    def __init__(self):
        self.builder = None

    def parseString(self, string, builder):
        try:
            self.parseStream(string.split("\n"), builder)
        except LXMError as err:
            raise LXMError(file=file_name, line=err.line, message=err.message)

    def parse(self, file_name, builder):
        file = open(file_name, 'r')
        try:
            self.parseStream(file, builder)
        except LXMError as err:
            raise LXMError(file=file_name, line=err.line, message=err.message)
        finally:
            file.close()

    def parseStream(self, file, builder):
        self.initParser(builder)

        # Check shabang
        self.readShabang(file)

        self.readLines(file)

    def initParser(self, builder):
        self.builder = builder
        self.line_index = 1
        self.type = None
        self.expecting_comment_level = 0
        # in suppress command should stay True only for next line.
        # next handleLine myst clear this flag
        self.in_suppress = False
        self.in_suppress_counter = 0
        self.block_stack = []
        self.skip_next_comments = True

    def readShabang(self, file):
        if isinstance(file, list):
            line = file[0]
            file.pop(0)
        else:
            line = file.readline()

        if line.startswith("#LXMacro#"):
            self.type = "LXM"
        elif re.search("#\s*python\s*", line) is not None:
            self.type = "PY"
        else:
            lx.out("Missing shabang")
            self.type = "LXM"
        self.builder.buildType(self.type)
        self.skip_next_comments = True

    def readLines(self, file):
        for line in file:
            self.line_index += 1
            self.parseLine(line)
            if self.in_suppress_counter != 0:
                self.in_suppress_counter -= 1
                if self.in_suppress_counter == 0:
                    self.in_suppress = False

    def parseLine(self, line):
        line = self.stripLine(line)

        if len(line) == 0:
            self.skip_next_comments = False
            return

        if line[0] == '#':
            self.handleCommentLine(line)
        else:
            self.handleNonCommentLine(line)
            self.skip_next_comments = False

    def isBlockStart(self, input_line):
        block = re.search(r'^#\s*Command Block Begin:\s*(\S*)\s*$', input_line)

        if block is None:
            return None

        return block.group(1)

    def isBlockEnd(self, input_line):
        block = re.search(r'^#\s*Command Block End:\s*(\S*)\s*$', input_line)

        if block is None:
            return None

        return block.group(1)

    def isSuppress(self, input_line):
        block = re.search(r'^#\s*replay suppress:\s*$', input_line)

        if block is None:
            return False

        return True

    def isMeta(self, input_line):
        meta = re.search(r'^\#\s*replay\s+(\S+):(\S+|\S+.*\S+)\s*$', input_line)
        if meta is not None:
            return (meta.group(1), meta.group(2))
        else:
            return None

    def handleSuppress(self, line):
        if self.isSuppress(line):
            self.in_suppress = True
            # This garantees thant in_suppress will be cleared after next line
            self.in_suppress_counter = 2
            return True
        return False

    def handleMeta(self, line):
        meta = self.isMeta(line)
        if meta is not None:
            (name, value) = meta
            self.builder.buildMeta(name, value)
            return True
        return False

    def handleBlockStart(self, line):
        block_name = self.isBlockStart(line)
        if block_name is not None:
            self.block_stack.append((block_name, self.in_suppress))

            self.builder.buildBlockStart(tuple(self.block_stack), self.in_suppress)
            if self.in_suppress:
                self.expecting_comment_level += 1
                self.in_suppress = False
            return True
        return False

    def handleBlockEnd(self, line):
        block_name = self.isBlockEnd(line)
        if block_name is not None:
            name = self.block_stack[-1][0]
            if name != block_name:
                raise LXMError(line=self.line_index, message="Unexpected end of block '%s' must be '%s'" % (block_name, name))

            self.builder.buildBlockEnd(tuple(self.block_stack))

            if self.block_stack[-1][1]:
                self.expecting_comment_level -= 1

            self.block_stack.pop()
            return True
        return False

    def handleCommentLine(self, line):
        if self.handleSuppress(line):
            return

        if self.handleMeta(line):
            return

        if self.handleBlockStart(line):
            return

        if self.handleBlockEnd(line):
            return

        if self.skip_next_comments:
            return

        line = line.strip()
        if (len(line) > 0) and line[0] == '#':
            line = line[1:]
        if (len(line) > 0) and line[0] == ' ':
            line = line[1:]
        self.builder.buildComment(line)

    def handleNonCommentLine(self, line):
        if self.type == "LXM":
            self.builder.buildCommand(line, self.in_suppress)
        else:
            store_lx_eval = None
            cmd = None
            try:
                store_lx_eval = lx.eval

                def return_cmd(cmd):
                    return cmd

                lx.eval = return_cmd

                cmd = eval(line)
            except:
                raise LXMError(line=self.line_index, message="Wrong python command")
            finally:
                lx.eval = store_lx_eval

            if cmd is not None:
                self.builder.buildCommand(cmd, self.in_suppress)

    def commentsToSkip(self):
        return self.expecting_comment_level + (1 if self.in_suppress else 0)

    def uncomment(self, line):
        if len(line) == 0:
            return (line, False)
        elif line[0] != '#':
            return (line, False)
        else:
            return (line[1:].strip(), True)

    def stripLine(self, orig_line):
        line = orig_line.strip()

        for idx in range(0, self.commentsToSkip()):
            line, cont = self.uncomment(line)
            if not cont:
                break

        return line
