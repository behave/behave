# -*- coding: utf-8 -*-
# ============================================================================
# PAVER EXTENSION: paver_patch
# ============================================================================
"""
Provide some patch functionality to decouple "pavement.py" from
concrete installed paver version.

"""

from paver.easy import info

_PATH_PMETHOD_NAMES = [
    'mkdir_p',
    'makedirs_p',
    'rmdir_p',
    'removedirs_p',
    'remove_p',
    'unlink_p',
    'rmtree_p',
]

def ensure_path_with_pmethods(path_class):
    """
    Adds "..._p()" methods to path class.
    Earlier versions did not have those.

    :since: paver.path >= 1.2
    """
    for pmethod_name in _PATH_PMETHOD_NAMES:
        method_name = pmethod_name[:-2]
        pfunc = getattr(path_class, pmethod_name, None)
        if not pfunc:
            # -- PATCH PATH-CLASS: Set path_class.pmethod = method
            # NOTE: Old method had sanity check that is now provided by pmethod.
            info("PATCH: path.%s = %s" % (pmethod_name, method_name))
            func = getattr(path_class, method_name)
            setattr(path_class, pmethod_name, func)
