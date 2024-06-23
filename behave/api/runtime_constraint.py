# -*- coding: UTF-8 -*-
"""
Simplifies to specify runtime constraints in

* features/environment.py file
* features/steps/*.py" files
"""

from __future__ import absolute_import, print_function
import six
import sys
from behave.exception import ConstraintError


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# ---------------------------------------------------------------------------
def require_min_python_version(minimal_version):
    """Simplifies to specify the minimal python version that is required.

    :param minimal_version: Minimum version (as string, tuple)
    :raises: behave.exception.ConstraintError
    """
    if isinstance(minimal_version, six.string_types):
        minimal_version = tuple([int(x) for x in minimal_version.split('.')])
    elif not isinstance(minimal_version, tuple):
        raise ValueError("{!r} (expected: tuple, string)".format(minimal_version))

    python_version = sys.version_info[:2]
    if python_version < minimal_version:
        raise ConstraintError("python >= %s expected (was: %s)" % \
                              (minimal_version, python_version))


def require_min_behave_version(minimal_version):
    """Simplifies to specify the minimal behave version that is required.

    :param minimal_version: Minimum version (as string, tuple)
    :raises: behave.exception.ConstraintError
    """
    # -- SIMPLISTIC IMPLEMENTATION:
    from behave.version import VERSION as behave_version
    behave_version2 = behave_version.split(".")
    minimal_version2 = minimal_version.split(".")
    if behave_version2 < minimal_version2:
        # -- USE: Tuple comparison as version comparison.
        raise ConstraintError("behave >= %s expected (was: %s)" % \
                              (minimal_version, behave_version))
