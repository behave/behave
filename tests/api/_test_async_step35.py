# -*- coding: UTF-8 -*-
# pylint: disable=invalid-name
"""
Unit tests for :mod:`behave.api.async_test` for Python 3.5 (or newer).
"""

# -- IMPORTS:
from __future__ import absolute_import, print_function
import sys
from hamcrest import assert_that, close_to
import pytest

from behave._stepimport import use_step_import_modules, SimpleStepContainer
from behave.runner import Context, Runner
from .testing_support import StopWatch
from .testing_support_async import AsyncStepTheory


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
PYTHON_3_5 = (3, 5)
python_version = sys.version_info[:2]
py35_or_newer = pytest.mark.skipif(python_version < PYTHON_3_5,
                                   reason="Needs Python >= 3.5")

SLEEP_DELTA = 0.050
if sys.platform.startswith("win"):
    SLEEP_DELTA = 0.100


# -----------------------------------------------------------------------------
# TESTSUITE:
# -----------------------------------------------------------------------------
@py35_or_newer
class TestAsyncStepDecoratorPy35:

    def test_step_decorator_async_run_until_complete1(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step
            from behave.api.async_step import async_run_until_complete
            import asyncio

            @step('an async coroutine step waits "{duration:f}" seconds')
            @async_run_until_complete
            async def step_async_step_waits_seconds(context, duration):
                await asyncio.sleep(duration)

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- USES: async def step_impl(...) as async-step (coroutine)
        AsyncStepTheory.validate(step_async_step_waits_seconds)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        context = Context(runner=Runner(config={}))
        with StopWatch() as stop_watch:
            step_async_step_waits_seconds(context, 0.2)
        # DISABLED: assert abs(stop_watch.duration - 0.2) <= 0.05
        assert_that(stop_watch.duration, close_to(0.2, delta=SLEEP_DELTA))


@py35_or_newer
class TestAsyncStepRunPy35:
    """Ensure that execution of async-steps works as expected."""

    def test_async_step_passes(self):
        """ENSURE: Failures in async-steps are detected correctly."""
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import given, when
            from behave.api.async_step import async_run_until_complete

            @given('an async-step passes')
            @async_run_until_complete
            async def given_async_step_passes(context):
                context.traced_steps.append("async-step1")

            @when('an async-step passes')
            @async_run_until_complete
            async def when_async_step_passes(context):
                context.traced_steps.append("async-step2")

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP: Verify that async-steps can be executed.
        context = Context(runner=Runner(config={}))
        context.traced_steps = []
        given_async_step_passes(context)
        when_async_step_passes(context)
        assert context.traced_steps == ["async-step1", "async-step2"]

    def test_async_step_task_crossing(self):
        """ENSURE: Task started in an async-step can be seen running from another step"""
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import given, when
            from behave.api.async_step import async_run_until_complete
            import asyncio

            @given('we build an async task')
            @async_run_until_complete
            async def given_async_step_passes(context):
                async def the_task():
                    await asyncio.sleep(0.1)
                    return "task-done"
                context.the_task = asyncio.create_task(the_task())

            @when('we can wait for the task in another async step')
            @async_run_until_complete
            async def when_async_step_passes(context):
                await context.the_task

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP: Verify that async-steps can be executed.
        context = Context(runner=Runner(config={}))
        
        context.the_task = None
        given_async_step_passes(context)
        when_async_step_passes(context)
        assert context.the_task.done()
        assert context.the_task.result() == "task-done"


    def test_async_step_fails(self):
        """ENSURE: Failures in async-steps are detected correctly."""
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import when
            from behave.api.async_step import async_run_until_complete

            @when('an async-step fails')
            @async_run_until_complete
            async def when_async_step_fails(context):
                assert False, "XFAIL in async-step"

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP: Verify that AssertionError is detected.
        context = Context(runner=Runner(config={}))
        with pytest.raises(AssertionError):
            when_async_step_fails(context)


    def test_async_step_raises_exception(self):
        """ENSURE: Failures in async-steps are detected correctly."""
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import when
            from behave.api.async_step import async_run_until_complete

            @when('an async-step raises exception')
            @async_run_until_complete
            async def when_async_step_raises_exception(context):
                # pylint: disable=pointless-statement
                1 / 0   # XFAIL-HERE: Raises ZeroDivisionError

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP: Verify that raised exception is detected.
        context = Context(runner=Runner(config={}))
        with pytest.raises(ZeroDivisionError):
            when_async_step_raises_exception(context)
