# -*- coding: UTF-8 -*-
"""
Provides a knowledge database if some Python features are supported
in the current python version.
"""

from __future__ import absolute_import, print_function
import contextlib
import sys


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
PYTHON_VERSION = sys.version_info[:2]


# -----------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------
class PythonFeature(object):

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
    def has_async_keyword(cls):
        return cls.has_async_function()

    @classmethod
    def has_coroutine(cls):
        return cls.has_async_function()


class PythonLibraryFeature(PythonFeature):
    @staticmethod
    def has_asyncio_timeout():
        """
        Indicates if the following idioms are available:

        * :func:`asyncio.timeout()` is supported as async context-manager.
        * :class:`asyncio.Timeout` exists as async context-manager.

        EXAMPLE::

            import asyncio
            async with asyncio.timeout(10):
                await long_running_task()

        :returns: True, if this python version supports this feature.

        .. since:: Python >= 3.11
        .. seealso:: https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout
        """
        return PYTHON_VERSION >= (3, 11)

    @staticmethod
    def has_contextlib_asynccontextmanager():
        # -- SINCE: Python >= 3.7
        return hasattr(contextlib, "asynccontextmanager")
