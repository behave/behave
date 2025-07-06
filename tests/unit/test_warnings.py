from behave.python_feature import PythonFeature

if PythonFeature.has_async_function():
    # -- REQUIRES: async/await syntax and coroutine support (since: Python 3.5).
    from ._test_warnings_py35 import *  # noqa: F403
