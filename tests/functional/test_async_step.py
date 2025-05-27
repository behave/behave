# -*- coding: UTF-8 -*-
# pylint: disable=wildcard-import,unused-wildcard-import
"""
Unit test facade to protect pytest runner from 3.5 grammar changes:

* Runs tests related to async-steps.
"""

from __future__ import absolute_import
import sys

python_version = sys.version_info[:2]
if python_version >= (3, 5):
    # -- REQUIRES: async/await syntax and coroutine support (since: Python 3.5).
    from ._test_async_step import *  # noqa: F403
