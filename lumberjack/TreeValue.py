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
    _font_weight = None
    _font-style = None
    _tooltip = None

    def value():
        doc = "The value property."
        def fget(self):
            return self._value
        def fset(self, value):
            self._value = value
        def fdel(self):
            del self._value
        return locals()

    value = property(**value())

    def datatype():
        doc = "The datatype property."
        def fget(self):
            return self._datatype
        def fset(self, value):
            self._datatype = value
        def fdel(self):
            del self._datatype
        return locals()

    datatype = property(**datatype())

    def display_value():
        doc = "The display_value property."
        def fget(self):
            return self._display_value
        def fset(self, value):
            self._display_value = value
        def fdel(self):
            del self._display_value
        return locals()

    display_value = property(**display_value())

    def intput_region():
        doc = "The intput_region property."
        def fget(self):
            return self._intput_region
        def fset(self, value):
            self._intput_region = value
        def fdel(self):
            del self._intput_region
        return locals()

    intput_region = property(**intput_region())

    def color():
        doc = "The color property."
        def fget(self):
            return self._color
        def fset(self, value):
            self._color = value
        def fdel(self):
            del self._color
        return locals()

    color = property(**color())

    def font_weight():
        doc = "The font_weight property."
        def fget(self):
            return self._font_weight
        def fset(self, value):
            self._font_weight = value
        def fdel(self):
            del self._font_weight
        return locals()

    font_weight = property(**font_weight())

    def font_style():
        doc = "The font_style property."
        def fget(self):
            return self._font_style
        def fset(self, value):
            self._font_style = value
        def fdel(self):
            del self._font_style
        return locals()

    font_style = property(**font_style())

    def tooltip():
        doc = "The tooltip property."
        def fget(self):
            return self._tooltip
        def fset(self, value):
            self._tooltip = value
        def fdel(self):
            del self._tooltip
        return locals()

    tooltip = property(**tooltip())
