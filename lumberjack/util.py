#python

from var import *

def markup(pre, string):
    """
    By Adam O'Hern for Mechanical Color

    Returns a formatting string for modo treeview objects.
    Requires a prefix (usually "c" or "f" for colors and fonts respectively),
    followed by a string.

    Colors are done with "\03(c:color)", where "color" is a string representing a
    decimal integer computed with 0x01000000 | ((r << 16) | (g << 8) | b).
    Italics and bold are done with "\03(c:font)", where "font" is the string
    FONT_DEFAULT, FONT_NORMAL, FONT_BOLD or FONT_ITALIC.

    \03(c:4113) is a special case gray color specifically for treeview text.
    """
    return '\03({}:{})'.format(pre, string)


def bitwise_rgb(r, g, b):
    """
    By Adam O'Hern for Mechanical Color

    Input R, G, and B values (0-255), and get a bitwise RGB in return.
    (Used for colored text in treeviews.)
    """
    return str(0x01000000 | ((r << 16) | (g << 8 | b)))


def bitwise_hex(h):
    """
    By Adam O'Hern for Mechanical Color

    Input an HTML color hex (#ffffff), and get a bitwise RGB in return.
    (Used for colored text in treeviews.)
    """
    h = h.strip()
    if h[0] == '#':
        h = h[1:]
    r, g, b = h[:2], h[2:4], h[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return bitwise_rgb(r, g, b)
