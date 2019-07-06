# -*- coding: utf-8 -*-
# pylint: disable=C0103,R0201,W0401,W0614,W0621
#   C0103   Invalid name (setUp(), ...)
#   R0201   Method could be a function
#   W0401   Wildcard import
#   W0614   Unused import ... from wildcard import
#   W0621   Redefining name ... from outer scope

from __future__ import absolute_import
import pytest
from behave.formatter import ansi_escapes
from six.moves import range


# --------------------------------------------------------------------------
# TEST SUPPORT and TEST DATA
# --------------------------------------------------------------------------
TEXTS = [
    u"lorem ipsum",
    u"Alice and Bob",
    u"Alice\nBob",
]
ALL_COLORS = list(ansi_escapes.colors.keys())
CURSOR_UPS = [ansi_escapes.up(count) for count in range(10)]


def colorize(text, color):
    color_escape = ""
    if color:
        color_escape = ansi_escapes.colors[color]
    return color_escape + text + ansi_escapes.escapes["reset"]


def colorize_text(text, colors=None):
    if not colors:
        colors = []
    colors_size = len(colors)
    color_index = 0
    colored_chars = []
    for char in text:
        color = colors[color_index]
        colored_chars.append(colorize(char, color))
        color_index += 1
        if color_index >= colors_size:
            color_index = 0
    return "".join(colored_chars)


# --------------------------------------------------------------------------
# TEST SUITE
# --------------------------------------------------------------------------
def test_module_setup():
    """Ensure that the module setup (aliases, escapes) occured."""
    # colors_count = len(ansi_escapes.colors)
    aliases_count = len(ansi_escapes.aliases)
    escapes_count = len(ansi_escapes.escapes)
    assert escapes_count >= (2 + aliases_count + aliases_count)


class TestStripEscapes(object):

    @pytest.mark.parametrize("text", TEXTS)
    def test_should_return_same_text_without_escapes(self, text):
        assert text == ansi_escapes.strip_escapes(text)

    @pytest.mark.parametrize("text", ansi_escapes.colors.values())
    def test_should_return_empty_string_for_any_ansi_escape_color(self, text):
        assert "" == ansi_escapes.strip_escapes(text)

    @pytest.mark.parametrize("text", ansi_escapes.escapes.values())
    def test_should_return_empty_string_for_any_ansi_escape(self, text):
        assert "" == ansi_escapes.strip_escapes(text)

    @pytest.mark.parametrize("text", TEXTS)
    def test_should_strip_color_escapes_from_all_colored_text(self, text):
        colored_text = colorize_text(text, ALL_COLORS)
        assert text == ansi_escapes.strip_escapes(colored_text)
        assert text != colored_text

    @pytest.mark.parametrize("text", TEXTS)
    @pytest.mark.parametrize("color", ALL_COLORS)
    def test_should_strip_color_escapes_from_text(self, text, color):
        colored_text = colorize(text, color)
        assert text == ansi_escapes.strip_escapes(colored_text)
        assert text != colored_text

        colored_text2 = colorize(text, color) + text
        text2 = text + text
        assert text2 == ansi_escapes.strip_escapes(colored_text2)
        assert text2 != colored_text2

    @pytest.mark.parametrize("text", TEXTS)
    @pytest.mark.parametrize("cursor_up", CURSOR_UPS)
    def test_should_strip_cursor_up_escapes_from_text(self, text, cursor_up):
        colored_text = cursor_up + text + ansi_escapes.escapes["reset"]
        assert text == ansi_escapes.strip_escapes(colored_text)
        assert text != colored_text
