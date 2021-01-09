# -*- coding: UTF-8 -*-
"""
Provides a knowledge database if some Python features are supported
in the current python version.
"""

from __future__ import absolute_import
import sys
import six
from behave.tag_matcher import bool_to_string


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
PYTHON_VERSION = sys.version_info[:2]


# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class PythonFeature(object):

    @staticmethod
    def has_asyncio_coroutine_decorator():
        """Indicates if python supports ``@asyncio.coroutine`` decorator.

        EXAMPLE::

            import asyncio
            @asyncio.coroutine
            def async_waits_seconds(duration):
                yield from asyncio.sleep(duration)

        :returns: True, if this python version supports this feature.

        .. since:: Python >= 3.4
        .. deprecated:: Since Python 3.8 (use async-function instead)
        """
        # -- NOTE: @asyncio.coroutine is deprecated in py3.8, removed in py3.10
        return (3, 4) <= PYTHON_VERSION < (3, 10)

    @staticmethod
    def has_async_function():
        """Indicates if python supports async-functions / async-keyword.

        EXAMPLE::

            import asyncio
            async def async_waits_seconds(duration):
                yield from asyncio.sleep(duration)

        :returns: True, if this python version supports this feature.
        .. since:: Python >= 3.5
        """
        return (3, 5) <= PYTHON_VERSION

    @classmethod
    def has_coroutine(cls):
        return cls.has_async_function() or cls.has_asyncio_coroutine_decorator()


# -----------------------------------------------------------------------------
# SUPPORTED: ACTIVE-TAGS
# -----------------------------------------------------------------------------
PYTHON_HAS_ASYNCIO_COROUTINE_DECORATOR = PythonFeature.has_asyncio_coroutine_decorator()
PYTHON_HAS_ASYNC_FUNCTION = PythonFeature.has_async_function()
PYTHON_HAS_COROUTINE = PythonFeature.has_coroutine()
ACTIVE_TAG_VALUE_PROVIDER = {
    "python2": bool_to_string(six.PY2),
    "python3": bool_to_string(six.PY3),
    "python.version": "%s.%s" % PYTHON_VERSION,
    "os":      sys.platform.lower(),

    # -- PYTHON FEATURE, like: @use.with_py.feature_asyncio.coroutine
    "python_has_coroutine": bool_to_string(PYTHON_HAS_COROUTINE),
    "python_has_asyncio.coroutine_decorator":
        bool_to_string(PYTHON_HAS_ASYNCIO_COROUTINE_DECORATOR),
    "python_has_async_function": bool_to_string(PYTHON_HAS_ASYNC_FUNCTION),
    "python_has_async_keyword": bool_to_string(PYTHON_HAS_ASYNC_FUNCTION),
}
