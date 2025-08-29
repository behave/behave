"""
Provides path related utility functions.
"""

from __future__ import absolute_import, print_function
import os
from pathlib import Path
try:
    # -- SINCE: Python 3.5
    from os import scandir
except ImportError:
    # -- PYTHON-BACKPORT: os.scandir()
    from scandir import scandir


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
    if isinstance(directory, str):
        directory = Path(directory)
    elif not isinstance(directory, Path):
        raise TypeError("{!r} (expected: Path, str)".format(directory))
    if not directory.exists():
        return []
    if not directory.is_dir():
        raise ValueError("{!r} is not a directory".format(directory))

    if not recursive:
        selected = [entry.path for entry in scandir(directory) if entry.is_dir()]
        return sorted(selected)

    # -- CASE: Recursive walk directory-tree
    selected = []
    for root_dir, _dirs, _files in os.walk(directory):
        selected.append(root_dir)
    return sorted(selected[1:])  # -- EXCLUDE: directory (as first entry)
