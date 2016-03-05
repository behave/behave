# -*- coding: UTF-8 -*-
"""
Unit test support for :mod:`behave.api.async_test` tests.
"""

import inspect


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
class AsyncStepTheory(object):
    @staticmethod
    def ensure_normal_function(func):
        if hasattr(inspect, "isawaitable"):
            # -- SINCE: Python 3.5
            assert not inspect.isawaitable(func)

    @classmethod
    def validate(cls, func):
        cls.ensure_normal_function(func)
