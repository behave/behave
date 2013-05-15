# -*- coding: utf-8 -*-
# ============================================================================
# PAVER EXTENSION: paver_require
# ============================================================================
"""
Ensure that "pavement.py" are run with the expected paver version.

EXAMPLE:

    # -- file:pavement.py
    from paver.easy import *
    sys.path.insert(0, ".")
    from paver_ext import paver_require

    paver_require.min_version("1.2")
"""

from paver.easy import error
from paver.release import VERSION as paver_version
import sys

def min_version(min_version):
    """
    Utility function to ensure that a minimal paver version is used.
    Aborts paver execution if expectation is not met.

    :param min_version: Minimum paver version that is required (as string).
    """
    if not (paver_version >= min_version):
        error("REQUIRE: paver >= %s (actually: %s)" % (min_version, paver_version))
        error("ABORT: Here.")
        sys.exit(1)

def assert_min_version(min_version):
    assert paver_version >= min_version, \
           "REQUIRE: paver >= %s (actually: %s)" % (min_version, paver_version)
