"""
Fixes :mod:`path` breaking API changes.

Newer versions of :mod:`path` no longer support:

* :func:`Path.abspath()`: Use :func:`Path.absolute()`
* :func:`Path.isdir()`: Use :func:`Path.is_dir()`
* :func:`Path.isfile()`: Use :func:`Path.is_file()`
* ...

.. seealso:: https://github.com/jaraco/path
"""

from path import Path


# -----------------------------------------------------------------------------
# MONKEYPATCH (if needed)
# -----------------------------------------------------------------------------
def monkeypatch_path_if_needed():
    if not hasattr(Path, "abspath"):
        Path.abspath = Path.absolute
    if not hasattr(Path, "isdir"):
        Path.isdir = Path.is_dir
    if not hasattr(Path, "isfile"):
        Path.isfile = Path.is_file


# -----------------------------------------------------------------------------
# MODULE SETUP
# -----------------------------------------------------------------------------
# DISABLED: monkeypatch_path_if_needed()
