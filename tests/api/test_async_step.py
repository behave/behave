# -*- coding: UTF-8 -*-
"""
Unit test facade to protect pytest runner from Python 3.4/3.5 grammar changes.

.. note::

    Import/inject python-version specific test suites here
    to avoid python-grammar problems in python versions that do not support it.
"""

from __future__ import absolute_import
import sys

_python_version = sys.version_info[:2]
if _python_version >= (3, 4):
    # -- PROTECTED-IMPORT:
    # Older Python version have problems with grammer extensions (yield-from).
    #  from ._test_async_step34 import TestAsyncStepDecorator34, TestAsyncContext, TestAsyncStepRun34
    from ._test_async_step34 import *
if _python_version >= (3, 5):
    # -- PROTECTED-IMPORT:
    # Older Python version have problems with grammer extensions (async/await).
    #  from ._test_async_step35 import TestAsyncStepDecorator35, TestAsyncStepRun35
    from ._test_async_step35 import *
