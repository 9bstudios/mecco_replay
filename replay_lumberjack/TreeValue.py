# python

class TreeValue(object):
    """Contains all of the necessary properties for a TreeView
    cell value, including internal value, display value, and metadata
    like color and font information."""

    _value = None
    _datatype = None
    _display_value = None
    _input_region = None
    _color = None
    _font = None
    _tooltip = None

    def __init__(self, **kwargs):
        self._value = value if value in kwargs else None
        self._datatype = datatype if datatype in kwargs else None
        self._display_value = display_value if display_value in kwargs else None
        self._input_region = input_region if input_region in kwargs else None
        self._color = color if color in kwargs else None
        self._font = font if font in kwargs else None
        self._tooltip = tooltip if tooltip in kwargs else None

    def __set__(self, instance, value):
        self._value = value

    def __get__(self, instance, owner):
        return self._value

    def value():
        doc = """The actual cell value. Note that this can be overridden by
        `display_value()` when displayed in a TreeView."""
        def fget(self):
            return self._value
        def fset(self, value):
            self._value = value
        return locals()

    value = property(**value())

    def datatype():
        doc = """The datatype for the value. Can be any of the normal MODO value
        display types expressed as lowercase strings: 'acceleration', 'angle',
        'angle3', 'axis', 'boolean', 'color', 'color1', 'date', 'datetime',
        'filepath', 'float', 'float3', 'force', 'integer', 'light', 'mass',
        'percent', 'percent3', 'speed', 'string', 'time', 'uvcoord', 'vertmapname'"""
        def fget(self):
            return self._datatype
        def fset(self, value):
            self._datatype = value
        return locals()

    datatype = property(**datatype())

    def display_value():
        doc = """The value as it will be used in the treeview, including any formatting,
        fonts, colors, etc.

        MODO uses a "rich text" system to encode color and font information:
        Colors are done with "\03(c:color)", where "color" is a string representing a
        decimal integer computed with 0x01000000 | ((r << 16) | (g << 8) | b).
        Italics and bold are done with "\03(c:font)", where "font" is the string
        FONT_DEFAULT, FONT_NORMAL, FONT_BOLD or FONT_ITALIC.

        All of this should be handled internally by the value object unless explicitly
        overridden.

        Setting this value sets a literal string to be displayed
        in the cell regardless of the actual cell value. Automatically prepends the
        `Value` object's color and font markup as appropriate."""
        def fget(self):
            display_string = self._display_value if self._display_value else self.value
            markup = self._font.markup() if self._font else ''
            markup += self._color.markup() if self._color else ''
            return display_string
        def fset(self, value):
            self._display_value = value
        return locals()

    display_value = property(**display_value())

    def intput_region():
        doc = """Region for input-mapping. Must correspond to one of the input_region
        strings provided during the `Lumberjack().bless()` operation."""
        def fget(self):
            return self._intput_region
        def fset(self, value):
            self._intput_region = value
        return locals()

    intput_region = property(**intput_region())

    def color():
        doc = "Should be a Lumberjack `Color()` object. Default: None"
        def fget(self):
            return self._color
        def fset(self, value):
            self._color = value
        return locals()

    color = property(**color())

    def font():
        doc = "Should be a Lumberjack `Font()` object. Default: None"
        def fget(self):
            return self._font
        def fset(self, value):
            self._font = value
        return locals()

    font = property(**font())

    def tooltip():
        doc = """Tooltip to display for the cell. Should be a message table lookup
        if at all possible. (e.g. @table@message@)"""
        def fget(self):
            return self._tooltip
        def fset(self, value):
            self._tooltip = value
        return locals()

    tooltip = property(**tooltip())
