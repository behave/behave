# -*- coding: UTF-8 -*-
"""
Supports some active-tags related Python features (similar to: feature flags).
"""

from __future__ import absolute_import
from behave.tag_matcher import BoolValueObject
from behave.python_feature import PythonFeature


# -----------------------------------------------------------------------------
# SUPPORTED: ACTIVE-TAGS
# -----------------------------------------------------------------------------
# -- PYTHON FEATURE, like: @use.with_python.feature.coroutine=yes
ACTIVE_TAG_VALUE_PROVIDER = {
    "python.feature.coroutine": BoolValueObject(PythonFeature.has_coroutine()),
    "python.feature.async_function": BoolValueObject(PythonFeature.has_async_function()),
    "python.feature.async_keyword": BoolValueObject(PythonFeature.has_async_keyword()),

    # -- DEPRECATING (older active-tag names):
    "python_has_coroutine": BoolValueObject(PythonFeature.has_coroutine()),
    "python_has_async_function": BoolValueObject(PythonFeature.has_async_function()),
    "python_has_async_keyword": BoolValueObject(PythonFeature.has_async_keyword()),
}
