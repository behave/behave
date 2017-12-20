# -*- coding: utf-8 -*-
"""
Decides if vendor bundles are used or not.
Setup python path accordingly.
"""

from __future__ import absolute_import, print_function
import os.path
import sys

# -----------------------------------------------------------------------------
# DEFINES:
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
TASKS_VENDOR_DIR = os.path.join(HERE, "_vendor")
INVOKE_BUNDLE = os.path.join(TASKS_VENDOR_DIR, "invoke.zip")
INVOKE_BUNDLE_VERSION = "0.13.0"

DEBUG_SYSPATH = False


# -----------------------------------------------------------------------------
# EXCEPTIONS:
# -----------------------------------------------------------------------------
class VersionRequirementError(SystemExit): pass

# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_path(invoke_minversion=None):
    """Setup python search and add ``TASKS_VENDOR_DIR`` (if available)."""
    # print("INVOKE.tasks: setup_path")
    if not os.path.isdir(TASKS_VENDOR_DIR):
        print("SKIP: TASKS_VENDOR_DIR=%s is missing" % TASKS_VENDOR_DIR)
        return
    elif os.path.abspath(TASKS_VENDOR_DIR) in sys.path:
        # -- SETUP ALREADY DONE:
        # return
        pass

    use_vendor_bundles = os.environ.get("INVOKE_TASKS_USE_VENDOR_BUNDLES", "no")
    if need_vendor_bundles(invoke_minversion):
        use_vendor_bundles = "yes"

    if use_vendor_bundles == "yes":
        syspath_insert(0, os.path.abspath(TASKS_VENDOR_DIR))
        if setup_path_for_bundle(INVOKE_BUNDLE, pos=1):
            import invoke
            bundle_path = os.path.relpath(INVOKE_BUNDLE, os.getcwd())
            print("USING: %s (version: %s)" % (bundle_path, invoke.__version__))
    else:
        # -- BEST-EFFORT: May rescue something
        syspath_append(os.path.abspath(TASKS_VENDOR_DIR))
        setup_path_for_bundle(INVOKE_BUNDLE, pos=len(sys.path))

    if DEBUG_SYSPATH:
        for index, p in enumerate(sys.path):
            print("  %d.  %s" % (index, p))


def require_invoke_minversion(min_version, verbose=False):
    """Ensures that :mod:`invoke` has at the least the :param:`min_version`.
    Otherwise,

    :param min_version: Minimal acceptable invoke version (as string).
    :param verbose:     Indicates if invoke.version should be shown.
    :raises: VersionRequirementError=SystemExit if requirement fails.
    """
    # -- REQUIRES: sys.path is setup and contains invoke
    try:
        import invoke
        invoke_version = invoke.__version__
    except ImportError:
        invoke_version = "__NOT_INSTALLED"

    if invoke_version < min_version:
        message = "REQUIRE: invoke.version >= %s (but was: %s)" % \
                  (min_version, invoke_version)
        message += "\nUSE: pip install invoke>=%s" % min_version
        raise VersionRequirementError(message)

    INVOKE_VERSION = os.environ.get("INVOKE_VERSION", None)
    if verbose and not INVOKE_VERSION:
        os.environ["INVOKE_VERSION"] = invoke_version
        print("USING: invoke.version=%s" % invoke_version)

def need_vendor_bundles(invoke_minversion=None):
    invoke_minversion = invoke_minversion or "0.0.0"
    need_vendor_answers = []
    need_vendor_answers.append(need_vendor_bundle_invoke(invoke_minversion))
    # -- REQUIRE: path.py
    try:
        import path
        need_bundle = False
    except ImportError:
        need_bundle = True
    need_vendor_answers.append(need_bundle)

    # -- DIAG: print("INVOKE: need_bundle=%s" % need_bundle1)
    # return need_bundle1 or need_bundle2
    return any(need_vendor_answers)

def need_vendor_bundle_invoke(invoke_minversion="0.0.0"):
    # -- REQUIRE: invoke
    try:
        import invoke
        need_bundle = invoke.__version__ < invoke_minversion
        if need_bundle:
            del sys.modules["invoke"]
            del invoke
    except ImportError:
        need_bundle = True
    except Exception:
        need_bundle = True
    return need_bundle

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_path_for_bundle(bundle_path, pos=0):
    if os.path.exists(bundle_path):
        syspath_insert(pos, os.path.abspath(bundle_path))
        return True
    return False

def syspath_insert(pos, path):
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(pos, path)

def syspath_append(path):
    if path in sys.path:
        sys.path.remove(path)
    sys.path.append(path)

