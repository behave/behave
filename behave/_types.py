# -*- coding: UTF-8 -*-
"""Basic types (helper classes)."""
from __future__ import absolute_import, print_function, division
import types


# -----------------------------------------------------------------------------
# BASIC TYPES:
# -----------------------------------------------------------------------------
class Unknown(object):
    """
    Placeholder for unknown/missing information, distinguishable from None.

    .. code-block:: python

        data = {}
        value = data.get("name", Unknown)
        if value is Unknown:
            # -- DO SOMETHING
            ...
    """


# -- SINCE: Python 3.10 -- types.NoneType
NoneType = getattr(types, "NoneType", Unknown)
if NoneType is Unknown:
    NoneType = type(None)


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------------------------
def parse_bool(text):
    """Parses a boolean text and converts it into boolean value (if possible).
    Supported truth string values:

      * true:   "true", "yes", "on", "1"
      * false:  "false", "no", "off", "0"

    :raises: ValueError, if text is invalid
    """
    # -- BASED ON: distutils.util.strtobool (deprecated; removed in Python 3.12)
    text = text.lower().strip()
    if text in ("yes", "true", "on", "1"):
        return True
    elif text in ("no", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value: %r" % (text,))


def require_type(value, expected_type, message=None):
    if isinstance(value, expected_type):
        return True  # -- SUPPORT USE: In boolean expressions

    # -- CASE: FAILED
    if message is None:
        message = "{} (expected: {})".format(
            type(value).__name__,
            expected_type.__name__)
    raise TypeError(message)

def require_not_type(value, unexpected_type, message=None):
    if not isinstance(value, unexpected_type):
        return True  # -- SUPPORT USE: In boolean expressions

    # -- CASE: FAILED
    if message is None:
        message = "{} (not-expected: {})".format(
            type(value).__name__,
            unexpected_type.__name__)
    raise TypeError(message)

def require_callable(func, message=None):
    if callable(func):
        return True

    if message is None:
        message = "{!r} (expected: callable)".format(func)
    raise TypeError(message)


def require_not_none(value, name=None, message=None):
    if value is not None:
        return True

    if message is None:
        message = "expected: not None"
        if name:
            message = "{name} is None (expected: not None)".format(name=name)
    raise RuntimeError(message)
