# -*- coding: UTF-8 -*-
"""
Simplifies to specify runtime constraints in

* features/environment.py file
* features/steps/*.py" files
"""

from __future__ import absolute_import
from behave.exception import ConstraintError


# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# ---------------------------------------------------------------------------
def require_min_python_version(minimal_version):
    """Simplifies to specify the minimal python version that is required.

    :param minimal_version: Minimum version (as string, tuple)
    :raises: behave.exception.ConstraintError
    """
    import six
    import sys
    python_version = sys.version_info
    if isinstance(minimal_version, six.string_types):
        python_version = "%s.%s" % sys.version_info[:2]
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
    if behave_version < minimal_version:
        raise ConstraintError("behave >= %s expected (was: %s)" % \
                              (minimal_version, behave_version))
