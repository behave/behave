# -*- coding: UTF-8 -*-
"""
Official API for step writers that want to use step-matchers.
"""

from __future__ import absolute_import, print_function
import warnings
from behave import matchers as _step_matchers


def register_type(**kwargs):
    _step_matchers.register_type(**kwargs)


def use_default_step_matcher(name=None):
    return _step_matchers.use_default_step_matcher(name=name)

def use_step_matcher(name):
    return _step_matchers.use_step_matcher(name)

def step_matcher(name):
    """DEPRECATED, use :func:`use_step_matcher()` instead."""
    # -- BACKWARD-COMPATIBLE NAME: Mark as deprecated.
    warnings.warn("deprecated: Use 'use_step_matcher()' instead",
                  DeprecationWarning, stacklevel=2)
    return use_step_matcher(name)


# -- REUSE: API function descriptions (aka: docstrings).
register_type.__doc__ = _step_matchers.register_type.__doc__
use_step_matcher.__doc__ = _step_matchers.use_step_matcher.__doc__
use_default_step_matcher.__doc__ = _step_matchers.use_default_step_matcher.__doc__
