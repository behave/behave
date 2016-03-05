# -*- coding: UTF-8 -*-
"""
Unit test facade to protect py.test runner from Python 3.4/3.5 grammar changes.
"""

from __future__ import absolute_import
import sys

python_version = sys.version_info[:2]
if python_version >= (3, 5):
    # -- PROTECTED-IMPORT:
    # Older Python version have problems with grammer extensions (async/await).
    from ._test_async_step35 import TestAsyncStepDecorator35
    from ._test_async_step34 import TestAsyncStepDecorator34, TestAsyncContext
elif (3, 4) <= python_version < (3, 5):
    # -- PROTECTED-IMPORT:
    # Older Python version have problems with grammer extensions (yield-from).
    from ._test_async_step34 import TestAsyncStepDecorator34, TestAsyncContext
