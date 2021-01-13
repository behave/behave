# -*- coding: UTF-8 -*-
# pylint: disable=redefined-builtin,unused-import
"""
Behave exception classes.

.. versionadded:: 1.2.7
"""

from __future__ import absolute_import
from behave.compat.exceptions import FileNotFoundError, ModuleNotFoundError


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES:
# ---------------------------------------------------------------------------
class ConstraintError(RuntimeError):
    """Used if a constraint/precondition is not fulfilled at runtime.

    .. versionadded:: 1.2.7
    """


class ConfigError(Exception):
    """Used if the configuration is (partially) invalid."""


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES: Related to File Handling
# ---------------------------------------------------------------------------
# -- SINCE: Python 3.3 -- FileNotFoundError is built-in exception
# class FileNotFoundError(LookupError):
#    """Used if a specified file was not found."""
#
class InvalidFileLocationError(LookupError):
    """Used if a :class:`behave.model_core.FileLocation` is invalid.
    This occurs if the file location is no exactly correct and
    strict checking is enabled.
    """


class InvalidFilenameError(ValueError):
    """Used if a filename does not have the expected file extension, etc."""


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES: Related to Imported Plugins
# ---------------------------------------------------------------------------
# RELATED: class ModuleNotFoundError(ImportError): -- Since Python 3.6
class ClassNotFoundError(ImportError):
    """Used if module to import exists, but class with this name does not exist."""


class InvalidClassError(TypeError):
    """Used if the specified class has the wrong type:

    * not a class
    * not subclass of a required class
    """
