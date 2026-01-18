"""
Behave exception classes.

.. versionadded:: 1.2.7
"""

from behave.tag_expression.parser import TagExpressionError


__all__ = [
    "ClassNotFoundError",
    "CleanupError",
    "ConfigError",
    "ConfigParamTypeError",
    "ConstraintError",
    "InvalidClassError",
    "InvalidFileLocationError",
    "InvalidFilenameError",
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
