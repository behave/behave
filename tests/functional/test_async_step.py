"""
Unit test facade to protect pytest runner from 3.5 grammar changes:

* Runs tests related to async-steps.
"""

from behave.python_feature import PythonFeature

if PythonFeature.has_async_function():
    # -- REQUIRES: async/await syntax and coroutine support (since: Python 3.5).
    from ._test_async_step import *  # noqa: F403
