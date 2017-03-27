import lx, re

class ArgAttributes(object):
    def __init__(self, idx, command, attributes, value_parsed):
        self.m_index = idx
        self.m_command = command
        self.m_attributes = attributes
        self.m_value_parsed = value_parsed

    def type_name(self, default = None):
        res = default
        try:
            if self.m_attributes is not None:
                res = self.m_attributes.TypeName(self.m_index)

                if res is None:
                    lookup = [
                        lx.symbol.sTYPE_STRING, # generic object
                        lx.symbol.sTYPE_INTEGER,
                        lx.symbol.sTYPE_FLOAT,
                        lx.symbol.sTYPE_STRING
                    ]
                    res = lookup[self.m_attributes.Type(self.m_index)]
        except:
            res = default

        return res

    def type(self, default = None):
        res = default
        try:
            if self.m_attributes is not None:
                res = self.m_attributes.Type(self.m_index)

        except:
            res = default

        return res

    def value_string(self, default = None):
        """Returns string representation of value as it appears in command line. Hint and bool conversion is done"""
        res = default

        if self.m_value_parsed:
            try:
                if self.m_attributes is not None:
                    type = self.type(lx.symbol.i_TYPE_STRING)
                    if type == lx.symbol.i_TYPE_FLOAT:
                        res = repr(self.m_attributes.GetFlt(self.m_index))
                    elif type == lx.symbol.i_TYPE_INTEGER:
                        res = self.m_attributes.GetInt(self.m_index)
                        if self.m_attributes.TypeName(self.m_index) == lx.symbol.sTYPE_BOOLEAN:
                            res = "true" if res != 0 else 'false'
                        else:
                            for ival, name in self.m_attributes.Hints(self.m_index):
                                if ival == res:
                                    res = name
                                    break
                        res = str(res)
                    elif type is not None:
                        # type == lx.symbol.i_TYPE_STRING: and more
                        res = self.m_attributes.GetString(self.m_index)
            except Exception as err:
                res = default

        return res

    def value_as_string(self, default = None):
        """Returns comand value as Python string. No any hint conversion or bool conversion is done
           For bool this will return "0"/"1". """
        res = default

        if self.m_value_parsed:
            try:
                if self.m_attributes is not None:
                    type = self.type(None)
                    # Handling float to not loose precision when converting to string
                    if type == lx.symbol.i_TYPE_FLOAT:
                        res = repr(self.m_attributes.GetFlt(self.m_index))
                    elif type is not None:
                        res = self.m_attributes.GetString(self.m_index)

            except:
                res = default

        return res

    def value_as_float(self, default = None):
        res = default

        if self.m_value_parsed:
            try:
                if self.m_attributes is not None:
                    res = self.m_attributes.GetFlt(self.m_index)
            except:
                res = default

        return res

    def value_as_integer(self, default = None):
        res = default

        if self.m_value_parsed:
            try:
                if self.m_attributes is not None:
                    res = self.m_attributes.GetInt(self.m_index)
            except:
                res = default

        return res

    def hints(self, default = None):
        res = default
        try:
            if self.m_attributes is not None:
                type_name = self.type_name(None)
                if type_name == lx.symbol.sTYPE_INTEGER:
                    res = self.m_attributes.Hints(self.m_index)
                    if len(res) == 0:
                        res = default
        except:
            res = default

        return res

    def name(self, default = None):
        res = default
        try:
            if self.m_attributes is not None:
                res = self.m_attributes.Name(self.m_index)
        except:
            res = default

        return res

    def test_flag(self, flag, default = None):
        res = default

        try:
            if self.m_command is not None:
                res = (self.m_command.ArgFlags(self.m_index) & flag != 0)
        except:
            res = default

        return res

    def is_variable(self, default = None):
        return self.test_flag(lx.symbol.fCMDARG_VARIABLE)

    def is_value_set(self, default = None):
        return self.test_flag(lx.symbol.fCMDARG_VALUE_SET)

    def is_hidden(self, default = None):
        return self.test_flag(lx.symbol.fCMDARG_HIDDEN)

# Class provides interface for accessing command and argument attributes
# All methods are taking default values that will be used if command and attributes
# interfaces are not constructed successfully.
class CommandAttributes(object):
    def __init__(self, **kwargs):

        self.m_value_parsed = True
        if 'string' in kwargs:
            command = kwargs['string']

            svc = lx.service.Command()
            try:
                # Insert `!!` to beginning of command string to keep command
                # from throwing ugly dialogs in case of error.
                command_with_prefix = re.sub(r"(^[!?+]*)(.*)", r"!!\2", command)
                x, y, cmd = svc.SpawnFromString(command_with_prefix)
            except:
                # If this fail then command cannot be successfully executed at this state
                # In this case we will use meta information which will provide almost the same
                # Data except information about variable arguments

                # Spawn is not parsing values
                self.m_value_parsed = False
                try:
                    cmd = svc.Spawn(0, command)
                except:
                    # This is not expected to fail if command name is correct
                    # Anyway handling this
                    self.m_command = None
                    self.m_attributes = None
                    return
        elif 'object' in kwargs:
            cmd = kwargs['object']

        self.m_command = lx.object.Command(cmd)
        self.m_attributes = lx.object.Attributes(cmd)


    def arg_count(self, default = None):
        """Return count of arguments"""
        if self.m_attributes is not None:
            return self.m_attributes.Count()
        else:
            return default

    def arg(self, idx):
        """Returns ArgAttributes for argument with index idx"""
        assert idx < self.arg_count(0)
        return ArgAttributes(idx, self.m_command, self.m_attributes, self.m_value_parsed)

    def prefix(self, default = None):
        res = default
        try:
            if self.m_command is not None:
                svc = lx.service.Command()
                res = svc.ExecFlagsAsPrefixString(self.m_command.PostExecBehaviorFlags())
        except:
            res = default

        return res

    def name(self, default = None):
        res = default
        try:
            if self.m_command is not None:
                res = self.m_command.Name()
        except:
            res = default

        return res
