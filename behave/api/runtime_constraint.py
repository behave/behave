# -*- coding: UTF-8 -*-
"""
Simplifies to specify runtime constraints in

* features/environment.py file
* features/steps/*.py" files
"""

from __future__ import absolute_import
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
    python_version = sys.version_info
    if isinstance(minimal_version, six.string_types):
        python_version = float("%s.%s" % sys.version_info[:2])
        minimal_version = float(minimal_version)
    elif not isinstance(minimal_version, tuple):
        raise TypeError("string or tuple (was: %s)" % type(minimal_version))

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
