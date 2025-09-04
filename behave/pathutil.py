"""
Provides path related utility functions.
"""

from __future__ import absolute_import, print_function
from .python_feature import PYTHON_VERSION
import os
import six
try:
    # -- SINCE: Python 3.5
    from os import scandir
except ImportError:
    # -- PYTHON-BACKPORT: os.scandir()
    from scandir import scandir

if PYTHON_VERSION < (3, 6):
    # -- SPECIAL CASE: Python2.7 -- pathlib2 provides better support for Path.
    from pathlib import Path as _OtherPath
    from pathlib2 import Path
    PATH_LIKE = (Path, _OtherPath)
else:
    # -- SINCE: Python 3.6 -- os.PathLike
    from pathlib import Path
    PATH_LIKE = os.PathLike


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------------------------
def select_subdirectories(directory, recursive=True):
    """
    Select/collects the subdirectories of a directory.

    :param directory: Directory to select subdirectories from.
    :param recursive: If true, recursively discover subdirectories.
    :return: List of subdirectories (as Path object).
    """
    if isinstance(directory, six.string_types):
        directory = Path(directory)
    elif not isinstance(directory, PATH_LIKE):
        raise TypeError("{!r} (expected: Path, str)".format(directory))
    if not directory.exists():
        return []
    if not directory.is_dir():
        raise ValueError("{!r} is not a directory".format(directory))

    if not recursive:
        # -- SPECIAL CASE: Python 2.7 needs scandir(string) and not Path.
        selected = [Path(entry.path)
                    for entry in scandir(str(directory)) if entry.is_dir()]
        return sorted(selected)

    # -- CASE: Recursive walk directory-tree
    # SPECIAL CASE: Python 2.7 needs os.walk(string) and not Path.
    selected = []
    for root_dir, _dirs, _files in os.walk(str(directory)):
        selected.append(root_dir)
    # -- EXCLUDE: directory (as first entry)
    return sorted([Path(directory) for directory in selected[1:]])
