# -*- coding: utf-8 -*-
# pylint: disable=C0103,R0201,W0401,W0614,W0621
#   C0103   Invalid name (setUp(), ...)
#   R0201   Method could be a function
#   W0401   Wildcard import
#   W0614   Unused import ... from wildcard import
#   W0621   Redefining name ... from outer scope

from __future__ import absolute_import
from nose import tools
from behave.formatter import ansi_escapes
import unittest
from six.moves import range

class StripEscapesTest(unittest.TestCase):
    ALL_COLORS = list(ansi_escapes.colors.keys())
    CURSOR_UPS = [ ansi_escapes.up(count)  for count in range(10) ]
    TEXTS = [
        u"lorem ipsum",
        u"Alice\nBob\nCharly\nDennis",
    ]

    @classmethod
    def colorize(cls, text, color):
        color_escape = ""
        if color:
            color_escape = ansi_escapes.colors[color]
        return color_escape + text + ansi_escapes.escapes["reset"]

    @classmethod
    def colorize_text(cls, text, colors=None):
        if not colors:
            colors = []
        colors_size = len(colors)
        color_index = 0
        colored_chars = []
        for char in text:
            color = colors[color_index]
            colored_chars.append(cls.colorize(char, color))
            color_index += 1
            if color_index >= colors_size:
                color_index = 0
        return "".join(colored_chars)

    def test_should_return_same_text_without_escapes(self):
        for text in self.TEXTS:
            tools.eq_(text, ansi_escapes.strip_escapes(text))

    def test_should_return_empty_string_for_any_ansi_escape(self):
        # XXX-JE-CHECK-PY23: If list() is really needed.
        for text in list(ansi_escapes.colors.values()):
            tools.eq_("", ansi_escapes.strip_escapes(text))
        for text in list(ansi_escapes.escapes.values()):
            tools.eq_("", ansi_escapes.strip_escapes(text))


    def test_should_strip_color_escapes_from_text(self):
        for text in self.TEXTS:
            colored_text = self.colorize_text(text, self.ALL_COLORS)
            tools.eq_(text, ansi_escapes.strip_escapes(colored_text))
            self.assertNotEqual(text, colored_text)

            for color in self.ALL_COLORS:
                colored_text = self.colorize(text, color)
                tools.eq_(text, ansi_escapes.strip_escapes(colored_text))
                self.assertNotEqual(text, colored_text)

    def test_should_strip_cursor_up_escapes_from_text(self):
        for text in self.TEXTS:
            for cursor_up in self.CURSOR_UPS:
                colored_text = cursor_up + text + ansi_escapes.escapes["reset"]
                tools.eq_(text, ansi_escapes.strip_escapes(colored_text))
                self.assertNotEqual(text, colored_text)
