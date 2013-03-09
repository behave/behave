# -*- coding: utf-8 -*-
# ============================================================================
# PAVER EXTENSION: paver_patch
# ============================================================================
"""
Provide some patch functionality to decouple "pavement.py" from
concrete installed paver version.

"""

from paver.easy import info

# -----------------------------------------------------------------------------
# PATCH: PMETHODS, ala path.xxx_p()
# -----------------------------------------------------------------------------
_PATH_PMETHOD_NAMES = [
    'makedirs_p',
    'mkdir_p',
    'remove_p',
    'removedirs_p',
    'rmdir_p',
    'rmtree_p',
    'unlink_p',
]

def ensure_path_with_pmethods(path_class):
    """
    Adds "..._p()" methods to path class.
    Earlier versions did not have those.

    EXAMPLE:
        # -- file:pavement.py
        from paver.easy import *
        sys.path.insert(0, ".")

        from paver_ext import paver_patch
        paver_patch.ensure_path_with_pmethods(path)

    :since: paver.path >= 1.2
    """
    for pmethod_name in _PATH_PMETHOD_NAMES:
        assert pmethod_name.endswith("_p")
        method_name = pmethod_name[:-2]
        pfunc = getattr(path_class, pmethod_name, None)
        if not pfunc:
            # -- PATCH PATH-CLASS: Set path_class.pmethod = method
            # NOTE: Old method had sanity check that is now provided by pmethod.
            info("PATCH: path.%s = %s" % (pmethod_name, method_name))
            func = getattr(path_class, method_name)
            setattr(path_class, pmethod_name, func)

# -----------------------------------------------------------------------------
# PATCH: SMETHODS (silent methods), ala path.xxx_s()
# -----------------------------------------------------------------------------
_PATH_SMETHOD_CREATE_NAMES = [
    'makedirs_s',
    'mkdir_s',
]
_PATH_SMETHOD_DESTROY_NAMES = [
    'remove_s',
    'unlink_s',
    'removedirs_s',
    'rmdir_s',
    'rmtree_s',
]

def ensure_path_with_smethods(path_class):
    """
    Adds/patches silent path methods to path class, ala "..._s()".
    They are executed (and printed) only if something needs to be done.

    EXAMPLE:
        # -- file:pavement.py
        from paver.easy import *
        sys.path.insert(0, ".")

        from paver_ext import paver_patch
        paver_patch.ensure_path_with_smethods(path)

    .. note::
        This is similar to Paver < 1.2 behaviour.
    """
    def _make_screate_func(func):
        def wrapped(self, *args, **kwargs):
            if not self.exists():
                return func(self, *args, **kwargs)
        return wrapped

    def _make_sdestroy_func(func):
        def wrapped(self, *args, **kwargs):
            if self.exists():
                return func(self, *args, **kwargs)
        return wrapped

    smethod_names = _PATH_SMETHOD_CREATE_NAMES + _PATH_SMETHOD_DESTROY_NAMES
    for smethod_name in smethod_names:
        assert smethod_name.endswith("_s")
        pmethod_name = "%s_p" % smethod_name[:-2]
        func = getattr(path_class, pmethod_name)
        if smethod_name in _PATH_SMETHOD_CREATE_NAMES:
            screate_func = _make_screate_func(func)
            setattr(path_class, smethod_name, screate_func)
        else:
            sdestroy_func = _make_sdestroy_func(func)
            setattr(path_class, smethod_name, sdestroy_func)
