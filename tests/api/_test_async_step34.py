# -*- coding: UTF-8 -*-
# pylint: disable=invalid-name
"""
Unit tests for :mod:`behave.api.async_test`.
"""

# -- IMPORTS:
from __future__ import absolute_import, print_function
import sys
from unittest.mock import Mock
from hamcrest import assert_that, close_to
import pytest

from behave.api.async_step import AsyncContext, use_or_create_async_context
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
# DEPRECATED: @asyncio.coroutine decorator (since: Python >= 3.8)
PYTHON_3_5 = (3, 5)
PYTHON_3_8 = (3, 8)
python_version = sys.version_info[:2]
requires_py34_to_py37 = pytest.mark.skipif(
    not (PYTHON_3_5 <= python_version < PYTHON_3_8),
    reason="Supported only for python.versions: 3.4 .. 3.7 (inclusive)")


SLEEP_DELTA = 0.050
if sys.platform.startswith("win"):
    SLEEP_DELTA = 0.100


# -----------------------------------------------------------------------------
# TESTSUITE:
# -----------------------------------------------------------------------------
@requires_py34_to_py37
class TestAsyncStepDecoratorPy34:

    def test_step_decorator_async_run_until_complete2(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 2: Use @asyncio.coroutine def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step
            from behave.api.async_step import async_run_until_complete
            import asyncio

            @step('a tagged-coroutine async step waits "{duration:f}" seconds')
            @async_run_until_complete
            @asyncio.coroutine
            def step_async_step_waits_seconds2(context, duration):
                yield from asyncio.sleep(duration)

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- USES: async def step_impl(...) as async-step (coroutine)
        AsyncStepTheory.validate(step_async_step_waits_seconds2)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        context = Context(runner=Runner(config={}))
        with StopWatch() as stop_watch:
            step_async_step_waits_seconds2(context, duration=0.2)

        # DISABLED: assert abs(stop_watch.duration - 0.2) <= 0.05
        assert_that(stop_watch.duration, close_to(0.2, delta=SLEEP_DELTA))


class TestAsyncContext:
    @staticmethod
    def make_context():
        return Context(runner=Runner(config={}))

    def test_use_or_create_async_context__when_missing(self):
        # -- CASE: AsynContext attribute is created with default_name
        # pylint: disable=protected-access
        context = self.make_context()
        context._push()

        async_context = use_or_create_async_context(context)
        assert isinstance(async_context, AsyncContext)
        assert async_context.name == "async_context"
        assert getattr(context, "async_context", None) is async_context

        context._pop()
        assert getattr(context, "async_context", None) is None

    def test_use_or_create_async_context__when_exists(self):
        # -- CASE: AsynContext attribute exists with default_name
        context = self.make_context()
        async_context0 = context.async_context = AsyncContext()
        assert context.async_context.name == "async_context"
        assert hasattr(context, AsyncContext.default_name)

        async_context = use_or_create_async_context(context)
        assert isinstance(async_context, AsyncContext)
        assert async_context.name == "async_context"
        assert getattr(context, "async_context", None) is async_context
        assert async_context is async_context0

    def test_use_or_create_async_context__when_missing_with_name(self):
        # -- CASE: AsynContext attribute is created with own name
        loop0 = Mock()
        context = self.make_context()
        async_context = use_or_create_async_context(context, "acontext", loop=loop0)
        assert isinstance(async_context, AsyncContext)
        assert async_context.name == "acontext"
        assert getattr(context, "acontext", None) is async_context
        assert async_context.loop is loop0

    def test_use_or_create_async_context__when_exists_with_name(self):
        # -- CASE: AsynContext attribute exists with own name
        loop0 = Mock()
        context = self.make_context()
        async_context0 = context.acontext = AsyncContext(name="acontext", loop=loop0)
        assert context.acontext.name == "acontext"

        loop1 = Mock()
        async_context = use_or_create_async_context(context, "acontext", loop=loop1)
        assert isinstance(async_context, AsyncContext)
        assert async_context is async_context0
        assert getattr(context, "acontext", None) is async_context
        assert async_context.loop is loop0


@requires_py34_to_py37
class TestAsyncStepRunPy34:
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
            import asyncio

            @given('an async-step passes')
            @async_run_until_complete
            @asyncio.coroutine
            def given_async_step_passes(context):
                context.traced_steps.append("async-step1")

            @when('an async-step passes')
            @async_run_until_complete
            @asyncio.coroutine
            def when_async_step_passes(context):
                context.traced_steps.append("async-step2")

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP:
        # Verify that async-steps can be execution without problems.
        context = Context(runner=Runner(config={}))
        context.traced_steps = []
        given_async_step_passes(context)
        when_async_step_passes(context)
        assert context.traced_steps == ["async-step1", "async-step2"]


    def test_async_step_fails(self):
        """ENSURE: Failures in async-steps are detected correctly."""
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import when
            from behave.api.async_step import async_run_until_complete
            import asyncio

            @when('an async-step fails')
            @async_run_until_complete
            @asyncio.coroutine
            def when_async_step_fails(context):
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
            import asyncio

            @when('an async-step raises exception')
            @async_run_until_complete
            @asyncio.coroutine
            def when_async_step_raises_exception(context):
                # pylint: disable=pointless-statement
                1 / 0   # XFAIL-HERE: Raises ZeroDivisionError

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP: Verify that raised exeception is detected.
        context = Context(runner=Runner(config={}))
        with pytest.raises(ZeroDivisionError):
            when_async_step_raises_exception(context)
