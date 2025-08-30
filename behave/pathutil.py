"""
Provides path related utility functions.
"""

import os
from pathlib import Path


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
        raise TypeError(f"{directory!r} (expected: Path, str)")
    if not directory.exists():
        return []
    if not directory.is_dir():
        raise ValueError("{directory!r} is not a directory")

    if not recursive:
        selected = [Path(entry.path)
                    for entry in os.scandir(directory) if entry.is_dir()]
        return sorted(selected)

    # -- CASE: Recursive walk directory-tree
    selected = []
    for root_dir, _dirs, _files in os.walk(directory):
        selected.append(root_dir)
    # -- EXCLUDE: directory (as first entry)
    return sorted([Path(directory) for directory in selected[1:]])
