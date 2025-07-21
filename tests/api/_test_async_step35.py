# -*- coding: UTF-8 -*-
# pylint: disable=invalid-name
"""
Unit tests for :mod:`behave.api.async_test` for Python 3.5 (or newer).

----

::

    python_implementation()
            Returns a string identifying the Python implementation.

            Currently, the following implementations are identified:
              'CPython' (C implementation of Python),
              'Jython' (Java implementation of Python),
              'PyPy' (Python implementation of Python).
"""

# -- IMPORTS:
from __future__ import absolute_import, print_function

import os
from platform import python_implementation
import sys

from hamcrest import assert_that, close_to
from mock import Mock
import pytest

from behave._stepimport import use_step_import_modules, SimpleStepContainer
from behave.api.async_step import (
    use_or_create_async_context
)
from behave.async_step import AsyncContext
from behave.configuration import Configuration
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
# -----------------------------------------------------------------------------
# TEST MARKERS:
# -----------------------------------------------------------------------------
PYTHON_3_5 = (3, 5)
CI = os.environ.get("CI", "false").lower() == "true"
python_version = sys.version_info[:2]
py35_or_newer = pytest.mark.skipif(python_version < PYTHON_3_5,
                                   reason="Needs Python >= 3.5")

SLEEP_DELTA = 0.100
if CI:
    # -- NEEDED-FOR: CI pipeline
    if sys.platform.startswith("win"):
        SLEEP_DELTA = 0.150
    elif python_implementation() == "PyPy":
        # -- NEEDED-FOR: pypy-3.10
        SLEEP_DELTA = 0.250


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
def make_context():
    config = Configuration(load_config=False)
    return Context(runner=Runner(config=config))


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
        context = make_context()
        with StopWatch() as stop_watch:
            step_async_step_waits_seconds(context, 0.2)
        # DISABLED: assert abs(stop_watch.duration - 0.2) <= 0.05
        assert_that(stop_watch.duration, close_to(0.2, delta=SLEEP_DELTA))


@py35_or_newer
class TestAsyncContext:
    def test_use_or_create_async_context__when_missing(self):
        # -- CASE: AsynContext attribute is created with default_name
        # pylint: disable=protected-access
        context = make_context()
        context._push()

        async_context = use_or_create_async_context(context)
        assert isinstance(async_context, AsyncContext)
        assert async_context.name == "async_context"
        assert getattr(context, "async_context", None) is async_context

        context._pop()
        assert getattr(context, "async_context", None) is None

    def test_use_or_create_async_context__when_exists(self):
        # -- CASE: AsynContext attribute exists with default_name
        context = make_context()
        async_context0 = context.async_context = AsyncContext()
        assert context.async_context.name == "async_context"
        assert hasattr(context, AsyncContext.default_name)

        async_context = use_or_create_async_context(context)
        assert isinstance(async_context, AsyncContext)
        assert async_context.name == "async_context"
        assert getattr(context, "async_context", None) is async_context
        assert async_context is async_context0

    @pytest.mark.xfail
    @pytest.mark.todo
    def test_use_or_create_async_context__when_missing_with_name(self):
        # -- CASE: AsynContext attribute is created with own name
        loop0 = Mock()
        context = make_context()
        async_context = use_or_create_async_context(context, "acontext", loop=loop0)
        assert isinstance(async_context, AsyncContext)
        assert async_context.name == "acontext"
        assert getattr(context, "acontext", None) is async_context
        assert async_context.loop is loop0

    @pytest.mark.xfail
    @pytest.mark.todo
    def test_use_or_create_async_context__when_exists_with_name(self):
        # -- CASE: AsynContext attribute exists with own name
        loop0 = Mock()
        context = make_context()
        async_context0 = context.acontext = AsyncContext(name="acontext", loop=loop0)
        assert context.acontext.name == "acontext"

        loop1 = Mock()
        async_context = use_or_create_async_context(context, "acontext", loop=loop1)
        assert isinstance(async_context, AsyncContext)
        assert async_context is async_context0
        assert getattr(context, "acontext", None) is async_context
        assert async_context.loop is loop0


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
        # -- RUN ASYNC-STEP:
        # Verify that async-steps can be execution without problems.
        context = make_context()
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

            @when('an async-step fails')
            @async_run_until_complete
            async def when_async_step_fails(context):
                assert False, "XFAIL in async-step"

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- RUN ASYNC-STEP: Verify that AssertionError is detected.
        context = make_context()
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
        context = make_context()
        with pytest.raises(ZeroDivisionError):
            when_async_step_raises_exception(context)
