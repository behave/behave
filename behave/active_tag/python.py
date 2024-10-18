# -*- coding: UTF-8 -*-
"""
Supports some active-tags for Python/Python version related functionality.
"""

from __future__ import absolute_import, print_function
import operator
from platform import python_implementation
import sys
import six
from behave.tag_matcher import ValueObject, BoolValueObject


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------
PYTHON_VERSION = sys.version_info[:2]
PYTHON_VERSION3 = sys.version_info[:3]


# -----------------------------------------------------------------------------
# HELPERS: ValueObjects
# -----------------------------------------------------------------------------
class VersionValueObject(ValueObject):
    """Provides a ValueObject for version comparisons with version-tuples
    (as: tuple of numbers).
    """

    def __int__(self, value, compare_func=None):
        if isinstance(value, six.string_types):
            value = self.to_version_tuple(value)
        super(VersionValueObject, self).__init__(value, compare_func)

    def matches(self, tag_value):
        try:
            tag_version = self.to_version_tuple(tag_value)
            return super(VersionValueObject, self).matches(tag_version)
        except (TypeError, ValueError) as e:
            self.on_type_conversion_error(tag_value, e)

    @staticmethod
    def to_version_tuple(version):
        if isinstance(version, tuple):
            # -- ASSUME: tuple of numbers
            return version
        elif isinstance(version, six.string_types):
            # -- CONVERT: string-to-tuple of numbers
            return tuple([int(x) for x in version.split(".")])

        # -- OTHERWISE:
        raise TypeError("Expect: string or tuple")


# -----------------------------------------------------------------------------
# ACTIVE-TAGS
# -----------------------------------------------------------------------------
# HINTS:
#   PYTHON_VERSION  = (3, 12)
#   PYTHON_VERSION3 = (3, 12, 7)
ACTIVE_TAG_VALUE_PROVIDER = {
    "python2": BoolValueObject(six.PY2),
    "python3": BoolValueObject(six.PY3),
    "python.version": "%s.%s" % PYTHON_VERSION,
    "python.min_version": VersionValueObject(PYTHON_VERSION, operator.ge),
    "python.max_version": VersionValueObject(PYTHON_VERSION, operator.le),

    "os": sys.platform.lower(),
    "platform": sys.platform,

    # -- python.implementation: cpython, pypy, jython, ironpython
    "python.implementation": python_implementation().lower(),
    "pypy": BoolValueObject("__pypy__" in sys.modules),
}
