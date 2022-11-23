# -*- coding: UTF-8 -*-
# pylint: disable=redefined-builtin,unused-import
"""
Provides some Python3 exception classes for Python2 and early Python3 versions.
"""

from __future__ import absolute_import
import errno as _errno
from six.moves import builtins as _builtins


# -----------------------------------------------------------------------------
# EXCEPTION CLASSES:
# -----------------------------------------------------------------------------
FileNotFoundError = getattr(_builtins, "FileNotFoundError", None)
if not FileNotFoundError:
    class FileNotFoundError(OSError):
        """Provided since Python >= 3.3"""
        errno = _errno.ENOENT


ModuleNotFoundError = getattr(_builtins, "ModuleNotFoundError", None)
if not ModuleNotFoundError:
    class ModuleNotFoundError(ImportError):
        """Provided since Python >= 3.6"""
