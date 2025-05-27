# -*- coding: UTF-8 -*-
# ruff: noqa: F401
# pylint: disable=redefined-builtin,unused-import
"""
Behave exception classes.

.. versionadded:: 1.2.7
"""

from __future__ import absolute_import, print_function
# -- RE-EXPORT: Exception class(es) here (provided in other places).
#   USE MODERN EXCEPTION CLASSES: FileNotFoundError, ModuleNotFoundError
#   COMPATIBILITY: Emulated if not supported yet by Python version.
from behave.compat.exceptions import (FileNotFoundError, ModuleNotFoundError)  # noqa: F401
from behave.tag_expression.parser import TagExpressionError


__all__ = [
    "ClassNotFoundError",
    "CleanupError",
    "ConfigError",
    "ConfigParamTypeError",
    "ConstraintError",
    "FileNotFoundError",
    "InvalidClassError",
    "InvalidFileLocationError",
    "InvalidFilenameError",
    "ModuleNotFoundError",
    "NotSupportedWarning",
    "ObjectNotFoundError",
    "PendingStepError",
    "ResourceExistsError",
    "StepNotImplementedError",
    "StepFunctionTypeError",
    "TagExpressionError",
]


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES:
# ---------------------------------------------------------------------------
class ConstraintError(RuntimeError):
    """
    Used if a constraint/precondition is not fulfilled at runtime.

    .. versionadded:: 1.2.7
    """

class ResourceExistsError(ConstraintError):
    """
    Used if you try to register a resource and another exists already
    with the same name.

    .. versionadded:: 1.2.7
    """

class ConfigError(Exception):
    """Used if the configuration is (partially) invalid."""

class ConfigParamTypeError(ConfigError):
    """Used if a config-param has the wrong type."""


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES: Related to Steps
# ---------------------------------------------------------------------------
class StepNotImplementedError(NotImplementedError):
    """Should be raised if a step is not implemented yet."""

class StepFunctionTypeError(TypeError):
    """Wrong step function type is used."""

class PendingStepError(StepNotImplementedError):
    """Alternative to StepNotImplementedError for a pending step."""


class CleanupError(RuntimeError):
    """Used if exception is raised during cleanup/cleanup-function."""


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


class ObjectNotFoundError(ImportError):
    """Used if module to import exists, but object with this name does not exist."""


class InvalidClassError(TypeError):
    """Used if the specified class has the wrong type:

    * not a class
    * not subclass of a required class
    """

class NotSupportedWarning(Warning):
    """
    Used if a certain functionality is not supported.

    .. versionadded:: 1.2.7
    """
