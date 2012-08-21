# -*- coding: utf-8 -*-
"""
BaseTerminal (Output/Writer) abstraction to improve platform independence
for formatters.
"""

from __future__ import print_function
from behave.terminal import get_terminal_for
import sys

__all__ = [ "print_", "setup_print_styles", "style_registry" ]

# -----------------------------------------------------------------------------
# LOCAL DATA:
# -----------------------------------------------------------------------------
style_registry = None

# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_print_styles(config=None):
    # pylint: disable=W0603
    global style_registry
    stream  = sys.stdout
    colored = None
    if config:
        stream  = config.output
        colored = config.color
    style_registry = get_terminal_for(stream, colored=colored)

def print_(text, style=None, end="\n", file=None):
    """
    Convenience function for styled prints.
    Based on standard print() function (since Python2.7, Python3).
    """
    # pylint: disable=W0622
    #   W0622   Redefining built-in 'file'
    __pychecker__ = "no-shadowbuiltin"
    if not file:
        file = sys.stdout

    if not style:
        # -- NORMAL PRINT: Without style.
        print(text, end=end, file=file)
        return

    # -- STYLED PRINT:
    if not style_registry:
        setup_print_styles()
    if end:
        text += end
    textstyle = style_registry.styles[style]
    textstyle.write(text, stream=file)

