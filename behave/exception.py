# -*- coding: UTF-8 -*-
"""
Behave exception classes.

.. versionadded:: 1.2.7
"""


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
class FileNotFoundError(LookupError):
    """Used if a specified file was not found."""


class InvalidFileLocationError(LookupError):
    """Used if a :class:`behave.model_core.FileLocation` is invalid.
    This occurs if the file location is no exactly correct and
    strict checking is enabled.
    """


class InvalidFilenameError(ValueError):
    """Used if a filename does not have the expected file extension, etc."""


