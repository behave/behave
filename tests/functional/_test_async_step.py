"""
Test that async-step functions (coroutines) are usable.

REQUIRES: Python version >= 3.5
"""

from __future__ import absolute_import, print_function

from contextlib import contextmanager
import sys
import asyncio

from behave.async_step import AsyncStepFunction
from behave._stepimport import use_step_import_modules, SimpleStepContainer
from behave.python_feature import PythonLibraryFeature
from behave.runner import Context, Runner

# -- IMPORTS:
# from hamcrest import assert_that, close_to, equal_to
from assertpy import assert_that
import pytest

# MAYBE: from tests.api.testing_support import StopWatch
from tests.api.testing_support_async import AsyncStepTheory


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
async def async_plus_two(value: int) -> int:
    return value + 2

@contextmanager
def async_step_uses_timeout_as_error():
    try:
        initial_value = AsyncStepFunction.TIMEOUT_AS_ERROR
        AsyncStepFunction.TIMEOUT_AS_ERROR = True
        yield
    finally:
        AsyncStepFunction.TIMEOUT_AS_ERROR = initial_value


# -----------------------------------------------------------------------------
# TEST MARKERS:
# -----------------------------------------------------------------------------
python_version = sys.version_info[:2]
use_with_async_await_syntax = pytest.mark.skipif(python_version < (3, 5),
                                                 reason="REQUIRES: async/await syntax (Python >= 3.5)")

SLEEP_DELTA = 0.050
if sys.platform.startswith("win"):
    SLEEP_DELTA = 0.100


# -----------------------------------------------------------------------------
# TEST SUITE:
# -----------------------------------------------------------------------------
@use_with_async_await_syntax
class TestAsyncStepFunction:

    @staticmethod
    def find_step_function_from(step_registry, step_text, step_type=None):
        from behave.model import Step
        if step_type is None:
            step_type = "step"

        keyword = step_type
        step = Step("", 0, keyword, step_type, step_text)
        step_definition = step_registry.find_step_definition(step)
        return step_definition.func

    @staticmethod
    def check_wrapper(async_step_func, coro_func):
        # -- WRAPPER=async_step_func that wraps coro_func (as SOURCE).
        assert async_step_func.__doc__ == coro_func.__doc__
        assert async_step_func.__name__ == coro_func.__name__
        assert async_step_func.__qualname__ == coro_func.__qualname__
        assert async_step_func.__module__ == coro_func.__module__

    def test_wraps_coroutine_function_correctly(self):
        async def coroutine_function_1(ctx):
            """ASYNC_STEP documentation is here."""

        async_step_function = AsyncStepFunction(coroutine_function_1)
        assert async_step_function.__doc__ == "ASYNC_STEP documentation is here."
        self.check_wrapper(async_step_function, coroutine_function_1)

    def test_call_should_call_coroutine_function(self):
        async def coroutine_function_2(ctx):
            ctx.called.append("coroutine_function_2")
            value = await async_plus_two(3)
            assert value == 5

        async_step_function = AsyncStepFunction(coroutine_function_2)
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        async_step_function(ctx)
        assert ctx.called == ["coroutine_function_2"]

    def test_call_with_params_calls_coroutine_function(self):
        async def coroutine_function_3(ctx, value: int):
            ctx.called.append(f"coroutine_function_3_with_{value}")
            actual_value = await async_plus_two(value)
            expected_value = value + 2
            assert actual_value == expected_value

        async_step_function = AsyncStepFunction(coroutine_function_3)
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        async_step_function(ctx, value=10)
        assert_that(ctx.called).is_equal_to(["coroutine_function_3_with_10"])

    def test_async_step_correctly(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            from behave import step

            @step('an async-step is called')
            async def async_step_is_called(ctx):
                """ASYNC_STEP documentation is HERE."""

        _step_function = self.find_step_function_from(step_container.step_registry,
                                                     "an async-step is called",
                                                     "step")
        assert async_step_is_called.__doc__ == "ASYNC_STEP documentation is HERE."



@use_with_async_await_syntax
class TestUseAsyncStep:

    def test_async_step_can_be_used(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            from behave import step

            @step('an async-step is called')
            async def async_step_is_called(ctx):
                ctx.called.append("async_step_is_called")
                actual_value = await async_plus_two(10)
                assert_that(actual_value).is_equal_to(12)

        # pylint: enable=import-outside-toplevel, unused-argument
        # -- USES: async def step_impl(...) as async-step (coroutine)
        AsyncStepTheory.validate(async_step_is_called)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        async_step_is_called(ctx)
        assert isinstance(async_step_is_called, AsyncStepFunction)
        assert_that(ctx.called).is_equal_to(["async_step_is_called"])

    def test_async_step_with_params_can_be_called(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step is called with "{value:d}')
            async def async_step_with_params(ctx, value: int):
                assert isinstance(value, int)
                ctx.called.append(f"async_step_is_called_with_{value}")
                actual_value = await async_plus_two(value)
                assert_that(actual_value).is_equal_to(value + 2)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        async_step_with_params(ctx, 10)
        assert_that(ctx.called).is_equal_to(["async_step_is_called_with_10"])

    def test_outcome_passed(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step should have "{name}')
            async def async_step_passes(ctx, name: str):
                actual_name = ctx.name
                assert_that(name).is_equal_to(actual_name)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        ctx = Context(runner=Runner(config={}))
        ctx.name = "Alice"
        async_step_passes(ctx, "Alice")

    def test_outcome_failed(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step should have "{name}')
            async def async_step_fails(ctx, name: str):
                actual_name = ctx.name
                assert_that(name).is_equal_to(actual_name)

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        ctx = Context(runner=Runner(config={}))
        ctx.name = "Alice"
        with pytest.raises(AssertionError):
            async_step_fails(ctx, "BOB")  # Alice != BOB

    def test_outcome_error(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step raises RuntimeError')
            async def async_step_with_error(ctx):
                raise RuntimeError("OOPS")

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        ctx = Context(runner=Runner(config={}))
        with pytest.raises(RuntimeError):
            async_step_with_error(ctx)

    # ruff: noqa: E501
    @pytest.mark.filterwarnings("ignore: 'asyncio.get_event_loop_policy' is deprecated.*:DeprecationWarning")
    def test_event_loop_is_unset(self, monkeypatch):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step with {name}')
            async def async_step_1(ctx, name):
                ctx.called.append(f"HELLO {name}")

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []

        # -- INITIAL CASE: No event loop is allocated or set.
        def mock_get_event_loop():
            ctx.called.append("EVENTLOOP_RUNTIME_ERROR")
            raise RuntimeError("OOPS")

        policy = asyncio.get_event_loop_policy()
        monkeypatch.setattr(policy, "get_event_loop", mock_get_event_loop)
        async_step_1(ctx, "ASYNC_STEP_1")
        assert_that(ctx.called).is_equal_to(["EVENTLOOP_RUNTIME_ERROR", "HELLO ASYNC_STEP_1"])

    def test_event_loop_exists(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step')
            async def async_step_2(ctx, name):
                ctx.called.append(f"HELLO {name}")

        # -- SETUP:
        this_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(this_loop)
        assert this_loop == asyncio.get_event_loop()

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        async_step_2(ctx, "ASYNC_STEP_2")
        assert_that(ctx.called).is_equal_to(["HELLO ASYNC_STEP_2"])


@pytest.mark.skipif(not PythonLibraryFeature.has_asyncio_timeout(),
                    reason="asyncio.timeout() is not supported.")
class TestAsyncStepFunctionWithTimeout:
    def test_with_timeout_if_no_timeout_occurs(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step with timeout', timeout=0.5)
            async def async_step_with_timeout(ctx, name):
                ctx.called.append(f"HELLO {name}")

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        async_step_with_timeout(ctx, "ASYNC_STEP_1")
        assert_that(ctx.called).is_equal_to(["HELLO ASYNC_STEP_1"])

    def test_with_timeout_if_timeout_occurs_as_error(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step with timeout', timeout=0.001)
            async def async_step_with_timeout_raises_error(ctx, name):
                await asyncio.sleep(0.01)
                ctx.called.append("LATE_HELLO {name}")

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        with async_step_uses_timeout_as_error():
            with pytest.raises(asyncio.TimeoutError):
                async_step_with_timeout_raises_error(ctx, "BAD_ASYNC_STEP_1")
        assert ctx.called == []

    def test_with_timeout_if_timeout_occurs(self):
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import step

            @step('an async-step with timeout', timeout=0.001)
            async def async_step_with_timeout_raises_error(ctx, name):
                await asyncio.sleep(0.01)
                ctx.called.append("LATE_HELLO {name}")

        # -- RUN ASYNC-STEP: Verify that it is behaving correctly.
        # ENSURE: Execution of async-step matches expected duration.
        ctx = Context(runner=Runner(config={}))
        ctx.called = []
        with pytest.raises(AssertionError):
            async_step_with_timeout_raises_error(ctx, "BAD_ASYNC_STEP_1")
        assert ctx.called == []

    def test_async_step_with_task_crossing(self):
        """
        ENSURE: Task started in an async-step can be seen running from another step.
        """
        # -- PROVIDED-BY: jeteve in PR #1249
        step_container = SimpleStepContainer()
        with use_step_import_modules(step_container):
            # -- STEP-DEFINITIONS EXAMPLE (as MODULE SNIPPET):
            # VARIANT 1: Use async def step_impl()
            # pylint: disable=import-outside-toplevel, unused-argument
            from behave import given, when
            import asyncio

            @given('we build an async task')
            async def given_async_step_passes(context):
                async def the_task():
                    await asyncio.sleep(0.1)
                    return "task-done"

                context.the_task = asyncio.create_task(the_task())

            @when('we can wait for the task in another async step')
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
