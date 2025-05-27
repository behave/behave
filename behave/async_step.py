"""
Support for "async-steps", that use async-functions/coroutine-functions, like:

.. code:: python

    # -- FILE: features/steps/async_step.py
    from behave import given, when, then, steo
    import asyncio

    @step("some async-step is used"):
    async def async_step(ctx, duration):
        await asyncio.sleep(duration)

----

TODO:

- IMPLEMENT: AsyncStepParams
- Cleanup bi-directional dependency problem with behave.api.async_step
- Move behave.api.async_step.AsyncContext here
"""

import asyncio
import functools
import inspect
import warnings
import six

from behave.api.async_step import AsyncContext
from behave.exception import StepFunctionTypeError


def get_async_context(context, **kwargs):
    print("TODO: NOT-IMPLEMENTED-YET")
    return AsyncContext()


def called_by_corutine():
    # -- NOTE: running_loop is only returned if called by a coroutine.
    running_loop = asyncio._get_running_loop()  # RETURNS: EventLoop or None
    return running_loop is not None


def use_or_assign_event_loop(loop=None):
    """
    Use the provided event loop or use the default event loop.
    If no event loop is provided, create a new one and assign it as default.
    """
    if loop and not loop.is_closed():
        return loop

    try:
        # -- HINT: asyncio.get_event_loop() -- DEPRECATED SINC PYTHON 3.13.
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return asyncio.get_event_loop_policy().get_event_loop()
    except RuntimeError:
        # -- OUTSIDE COROUTINE CALL CONTEXT: No event-loop is set up.
        this_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(this_loop)
        return this_loop


class AsyncStepParams:
    """XXX_JE_IDEA"""
    def __init__(self, loop=None, async_context=None):
        if isinstance(async_context, six.string_types):
            pass

        self.loop = loop
        self.loop_name = None
        self.async_context = async_context
        self.async_context_name = None

    def get_async_context_from(self, context):
        return NotImplemented

    def get_event_loop_from(self, context):
        return NotImplemented



class AsyncStepFunction:
    """
    Call adapter/decorator for an async-step function (as coroutine function).

    All calls occur from synchronous function context to async function context.
    """
    TIMEOUT_AS_ERROR = False

    def __init__(self, coroutine_func, timeout=None, **kwargs):
        if not inspect.iscoroutinefunction(coroutine_func):
            func_type = type(coroutine_func).__name__
            raise StepFunctionTypeError("%s (NEEDS: async-function)" % func_type)

        self.coro_func = coroutine_func
        self.async_step_kwargs = kwargs
        self.timeout = timeout

        # -- MAYBE: Support for Context attributes -- loop, async_context
        # XXX
        self.loop_name = None
        loop = kwargs.pop("loop", None)

        # -- PROVIDE: Source file-location of coroutine_func.
        functools.update_wrapper(self, coroutine_func)

    def get_event_loop(self, context):
        return use_or_assign_event_loop()

    async def _coro_with_timeout(self, context, *args, **kwargs):
        this_coroutine = self.coro_func(context, *args, **kwargs)
        try:
            async with asyncio.timeout(self.timeout):
                result = await this_coroutine
                return result
        except asyncio.TimeoutError:
            if self.TIMEOUT_AS_ERROR:
                raise  # -- PROVIDE STACK-TRACE (more diagnostics)
            # -- USE FAILED-ASSERTION: For compact error description.
            assert False, "TIMEOUT-OCCURRED: timeout=%s" % self.timeout

    def __call__(self, context, *args, **kwargs):
        """Function call operator to call the async-step function."""
        coro_func = self.coro_func
        if self.timeout is not None:
            coro_func = self._coro_with_timeout

        # async_context = self.get_async_context(context)
        this_loop = self.get_event_loop(context)
        this_coroutine = coro_func(context, *args, **kwargs)
        return this_loop.run_until_complete(this_coroutine)

