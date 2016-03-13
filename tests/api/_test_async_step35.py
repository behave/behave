# -*- coding: UTF-8 -*-
"""
Unit tests for :mod:`behave.api.async_test` for Python 3.5 (or newer).
"""

# -- IMPORTS:
from __future__ import absolute_import, print_function
import sys
from behave._stepimport import use_step_import_modules
from behave.runner import Context, Runner
import pytest

from .testing_support import StopWatch, SimpleStepContainer
from .testing_support_async import AsyncStepTheory


# -----------------------------------------------------------------------------
# SUPPORT:
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# ASYNC STEP EXAMPLES:
# -----------------------------------------------------------------------------
# if python_version >= 3.5:
#     @step('an async coroutine step waits "{duration:f}" seconds')
#     @async_run_until_complete
#     async def step_async_step_waits_seconds(context, duration):
#         print("async_step: Should sleep for %.3f seconds" % duration)
#         await asyncio.sleep(duration)
#
# if python_version >= 3.4:
#     @step('a tagged-coroutine async step waits "{duration:f}" seconds')
#     @async_run_until_complete
#     @asyncio.coroutine
#     def step_async_step_waits_seconds2(context, duration):
#         print("async_step2: Should sleep for %.3f seconds" % duration)
#         yield from asyncio.sleep(duration)
#
# -----------------------------------------------------------------------------
# TEST MARKERS:
# -----------------------------------------------------------------------------
# xfail = pytest.mark.xfail
python_version = float("%s.%s" % sys.version_info[:2])
py35_or_newer = pytest.mark.skipif(python_version < 3.5, reason="Needs Python >= 3.5")

# -----------------------------------------------------------------------------
# TESTSUITE:
# -----------------------------------------------------------------------------
@py35_or_newer
class TestAsyncStepDecorator35(object):

    def test_step_decorator_async_run_until_complete1(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            from behave import step
            from behave.api.async_step import async_run_until_complete
            import asyncio

            @step('an async coroutine step waits "{duration:f}" seconds')
            @async_run_until_complete
            async def step_async_step_waits_seconds(context, duration):
                await asyncio.sleep(duration)

        # -- USES: async def step_impl(...) as async-step (coroutine)
        AsyncStepTheory.validate(step_async_step_waits_seconds)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        context = Context(runner=Runner(config={}))
        with StopWatch() as stop_watch:
            step_async_step_waits_seconds(context, 0.2)
        assert abs(stop_watch.duration - 0.2) <= 0.05
