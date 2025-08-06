# -*- coding: utf-8 -*-
"""
Provides ANSI escape sequences for coloring/formatting output in ANSI terminals.
"""

from __future__ import absolute_import
import os
import re

# ---------------------------------------------------------------------------
# MODULE DATA
# ---------------------------------------------------------------------------
colors = {
    "black":        "\x1b[30m",
    "red":          "\x1b[31m",
    "green":        "\x1b[32m",
    "yellow":       "\x1b[33m",
    "blue":         "\x1b[34m",
    "magenta":      "\x1b[35m",
    "cyan":         "\x1b[36m",
    "white":        "\x1b[37m",
    "grey":         "\x1b[90m",
    "bold":         "\x1b[1m",
}

aliases = {
    "untested":     "cyan",         # SAME-COLOR AS: skipped
    "untested_pending": "cyan",     # SAME-COLOR AS: skipped
    "untested_undefined": "cyan",   # SAME-COLOR AS: skipped
    "executing":    "grey",
    "undefined":    "yellow",
    "pending":      "yellow",
    "pending_warn": "yellow",
    "passed":       "green",
    "failed":       "red",
    "error":        "red",
    "hook_error":   "red",
    "outline":      "cyan",
    "skipped":      "cyan",
    "comments":     "grey",
    "tag":          "cyan",
}

escapes = {
    "reset":        "\x1b[0m",
    "up":           "\x1b[1A",
}


# -- NEEDED-FOR: strip_escapes(), ...
_ANSI_ESCAPE_PATTERN = re.compile("\x1b\\[\\d+[mA]", re.UNICODE)



# ---------------------------------------------------------------------------
# MODULE SETUP
# ---------------------------------------------------------------------------
def _setup_module():
    """Setup the remaining ANSI color aliases and ANSI escape sequences.

    .. note:: May modify/extend the module attributes:

        * :attr:`aliases`
        * :attr:`escapes`
    """
    # MAYBE: global aliases, escapes
    if "GHERKIN_COLORS" in os.environ:
        new_aliases = [p.split("=") for p in os.environ["GHERKIN_COLORS"].split(":")]
        aliases.update(dict(new_aliases))

    for alias in aliases:
        escapes[alias] = "".join([colors[c] for c in aliases[alias].split(",")])
        arg_alias = alias + "_arg"
        arg_seq = aliases.get(arg_alias, aliases[alias] + ",bold")
        escapes[arg_alias] = "".join([colors[c] for c in arg_seq.split(",")])


# -- ONCE: During module-import.
_setup_module()


# ---------------------------------------------------------------------------
# FUNCTIONS:
# ---------------------------------------------------------------------------
def up(n):
    return "\x1b[%dA" % n


def strip_escapes(text):
    """Removes ANSI escape sequences from text (if any are contained).

    :param text: Text that may or may not contain ANSI escape sequences.
    :return: Text without ANSI escape sequences.
    """
    return _ANSI_ESCAPE_PATTERN.sub("", text)


def use_ansi_escape_colorbold_composites():     # pragma: no cover
    """Patch for "sphinxcontrib-ansi" to process the following ANSI escapes
    correctly (set-color set-bold sequences):

        ESC[{color}mESC[1m  => ESC[{color};1m

    Reapply aliases to ANSI escapes mapping.
    """
    # NOT-NEEDED: global escapes
    color_codes = {}
    for color_name, color_escape in colors.items():
        color_code = color_escape.replace("\x1b[", "").replace("m", "")
        color_codes[color_name] = color_code

    # pylint: disable=redefined-outer-name
    for alias in aliases:
        parts = [color_codes[c] for c in aliases[alias].split(",")]
        composite_escape = "\x1b[{0}m".format(";".join(parts))
        escapes[alias] = composite_escape

        arg_alias = alias + "_arg"
        arg_seq = aliases.get(arg_alias, aliases[alias] + ",bold")
        parts = [color_codes[c] for c in arg_seq.split(",")]
        composite_escape = "\x1b[{0}m".format(";".join(parts))
        escapes[arg_alias] = composite_escape
