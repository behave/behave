"""
Support for "async-steps", that use async-functions/coroutine-functions, like:

.. code:: python

    # -- FILE: features/steps/async_step.py
    from behave import given, when, then, steo
    import asyncio

    @step("some async-step is used"):
    async def async_step(ctx, duration):
        await asyncio.sleep(duration)
"""

from __future__ import absolute_import, print_function
import asyncio
import functools
import inspect
import warnings
import six

from behave._types import require_type
from behave.exception import StepFunctionTypeError
from behave.python_feature import PythonLibraryFeature


# -- PYTHON SDK FEATURE GUARD:
if PythonLibraryFeature.has_asyncio_timeout():
    # -- SINCE: Python >= 3.11
    asyncio_timeout = asyncio.timeout
elif PythonLibraryFeature.has_contextlib_asynccontextmanager():
    # -- CASE: 3.7 <= Python < 3.11 -- NOT-SUPPORTED, but issue a warning
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def asyncio_timeout(delay):
        warnings.warn("IGNORED: asyncio.timeout() -- REQUIRES: Python >= 3.11",
                      RuntimeWarning)
        yield
else:
    # -- CASE: Python < 3.7  -- NOT-SUPPORTED
    asyncio_timeout = None


# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def called_by_coroutine():
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
        # -- HINT: asyncio.get_event_loop() -- DEPRECATED SINCE PYTHON 3.13.
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return asyncio.get_event_loop_policy().get_event_loop()
    except RuntimeError:
        # -- OUTSIDE COROUTINE CALL CONTEXT: No event-loop is set up.
        this_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(this_loop)
        return this_loop


def use_or_create_async_context(ctx, name=None, loop=None, **kwargs):
    """
    Utility function to be used in step implementations to ensure that an
    :class:`AsyncContext` object is stored in the :param:`context` object.

    If no such attribute exists (under the given name),
    a new :class:`AsyncContext` object is created with the provided args.
    Otherwise, the existing context attribute is used.

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/my_async_steps.py
        # EXAMPLE REQUIRES: Python 3.5
        from behave import when
        from behave.api.async_step import use_or_create_async_context

        @when('I dispatch an async-call with param "{param}"')
        def step_impl(ctx, param):
            async_context = use_or_create_async_context(ctx, "async_context")
            task = async_context.loop.create_task(my_async_func(param))
            async_context.tasks.append(task)

        # -- COROUTINE:
        async def my_async_func(param):
            await asyncio.sleep(0.5)
            return param.upper()

    :param ctx:     Behave context object to use.
    :param name:    Optional name of async-context object (as string or None).
    :param loop:    Optional event_loop object to use for create call.
    :param kwargs:  Optional :class:`AsyncContext` params for create call.
    :return: :class:`AsyncContext` object from the :param:`ctx`.
    """
    if name is None:
        name = AsyncContext.default_name
    async_context = getattr(ctx, name, None)
    if async_context is None:
        # XXX PARAMS ORDERING:
        async_context = AsyncContext(loop=loop, name=name, **kwargs)
        setattr(ctx, async_context.name, async_context)

    # -- POSTCONDITIONS:
    require_type(async_context, AsyncContext)
    assert getattr(ctx, async_context.name) is async_context
    return async_context


# -----------------------------------------------------------------------------
# AsyncStepFunction
# -----------------------------------------------------------------------------
class AsyncStepParams:
    """
    Temporary solution for providing backward compatibility
    while using :class:`AsyncStepFunction` instead of
    :deco:`async_run_until_complete()` step decorator.
    """
    LOOP_NAME = "async_loop"
    ASYNC_CONTEXT_NAME = "async_context"

    def __init__(self, loop=None, async_context=None):
        if loop is not None:
            msg = "loop is deprecated, use: asyncio.set_event_loop()"
            warnings.warn(msg, DeprecationWarning)
        if async_context is not None:
            warnings.warn("async_context is deprecated", DeprecationWarning)

        async_context_name = None
        loop_name = None
        if isinstance(async_context, six.string_types):
            async_context_name = async_context
            async_context = None
        if isinstance(loop, six.string_types):
            loop_name = loop
            loop = None

        self.loop = loop
        self.loop_name = loop_name or self.LOOP_NAME
        self.async_context = async_context
        self.async_context_name = async_context_name or self.ASYNC_CONTEXT_NAME
        self._ctx = None

    def get_async_context_from(self, ctx):
        return getattr(ctx, self.async_context_name, self.async_context)

    def get_event_loop_from(self, ctx):
        return getattr(ctx, self.loop_name, self.loop)

    def assign_to_context(self, ctx):
        self._ctx = ctx

        async_context = self.get_async_context_from(ctx)
        async_loop = self.get_event_loop_from(ctx)
        if async_loop is not None:
            setattr(ctx, self.loop_name, async_loop)
        if async_context is not None:
            setattr(ctx, self.async_context_name, async_context)
        return self


class AsyncFunction:
    """
    Call adapter for an async-function (as coroutine function).

    Calls may occur from:

    * Synchronous function context (to async function context)
    * Asynchronous function context
    """
    TIMEOUT_AS_ERROR = False

    def __init__(self, coroutine_func, timeout=None):
        if not inspect.iscoroutinefunction(coroutine_func):
            func_type = type(coroutine_func).__name__
            raise TypeError("%s (NEEDS: async-function)" % func_type)
        if timeout is not None:
            if not PythonLibraryFeature.has_asyncio_timeout():
                msg = "IGNORED: timeout (requires: asyncio.timeout() -- Python >= 3.11)"
                warnings.warn(msg, RuntimeWarning)
            if asyncio_timeout is None:
                # -- ENSURE: _coro_with_timeout() is not used.
                timeout = None

        self.coro_func = coroutine_func
        self.timeout = timeout

    @property
    def loop(self):
        return self.get_event_loop()

    def get_event_loop(self):
        return use_or_assign_event_loop()

    async def _coro_with_timeout(self, *args, **kwargs):
        this_coroutine = self.coro_func(*args, **kwargs)
        try:
            async with asyncio_timeout(self.timeout):
                result = await this_coroutine
                return result
        except asyncio.TimeoutError:
            if self.TIMEOUT_AS_ERROR:
                raise  # -- PROVIDE STACK-TRACE (more diagnostics)
            # -- USE FAILED-ASSERTION: For compact error description.
            assert False, "TIMEOUT-OCCURRED: timeout=%s" % self.timeout

    def __call__(self, *args, **kwargs):
        """Function call operator to call the async-step function."""
        coro_func = self.coro_func
        if self.timeout is not None:
            coro_func = self._coro_with_timeout

        this_loop = self.get_event_loop()
        this_coroutine = coro_func(*args, **kwargs)
        return this_loop.run_until_complete(this_coroutine)

    # -- PREPARED:
    # def _run_coro_with_timeout(self, *args, **kwargs):
    #     this_coroutine = self.coro_func(*args, **kwargs)
    #     this_loop = self.get_event_loop()
    #
    #     task = this_loop.create_task(this_coroutine)
    #     done, pending = this_loop.run_until_complete(
    #         asyncio.wait([task], timeout=self.timeout))
    #     assert not pending, "TIMEOUT-OCCURRED: timeout=%s" % self.timeout
    #     finished_task = done.pop()
    #     exception = finished_task.exception()
    #     if exception:
    #         raise exception


class AsyncStepFunction(AsyncFunction):
    """
    Call adapter/decorator for an async-step function (as coroutine function).
    """
    TIMEOUT_AS_ERROR = False

    def __init__(self, coroutine_func, timeout=None, **kwargs):
        if not inspect.iscoroutinefunction(coroutine_func):
            func_type = type(coroutine_func).__name__
            raise StepFunctionTypeError("%s (NEEDS: async-function)" % func_type)

        # -- PROVIDE: Source file-location of coroutine_func.
        super(AsyncStepFunction, self).__init__(coroutine_func, timeout=timeout)
        functools.update_wrapper(self, coroutine_func)

        # -- MAYBE: Support for Context attributes -- loop, async_context
        self._params = AsyncStepParams(**kwargs)

    def __call__(self, ctx, *args, **kwargs):
        """Function call operator to call the async-step function."""
        self._params.assign_to_context(ctx)
        return super(AsyncStepFunction, self).__call__(ctx, *args, **kwargs)


# -----------------------------------------------------------------------------
# ASYNC STEP UTILITY CLASSES:
# -----------------------------------------------------------------------------
class AsyncContext(object):
    # pylint: disable=line-too-long
    """Provides a context object for "async steps" to keep track:

    * which event loop is used
    * which (asyncio) tasks are used or of interest

    .. attribute:: name

        Optional name of this object (in the behave context).
        If none is provided, :attr:`AsyncContext.default_name` is used.

    .. attribute:: loop
        Event loop object to use.
        If none is provided, the current event-loop is used
        (or a new one is created).

    .. attribute:: tasks
        List of started :mod:`asyncio` tasks (of interest).

    .. attribute:: should_close
        Indicates if the :attr:`loop` (event-loop) should be closed or not.

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/my_async_steps.py
        # REQUIRES: Python 3.5
        from behave import given, when, then, step
        from behave.api.async_step import AsyncContext

        @when('I dispatch an async-call with param "{param}"')
        def step_impl(ctx, param):
            async_context = getattr(ctx, "async_context", None)
            if async_context is None:
                async_context = ctx.async_context = AsyncContext()
            task = async_context.loop.create_task(my_async_func(param))
            async_context.tasks.append(task)

        @then('I wait at most {duration:f} seconds until all async-calls are completed')
        def step_impl(ctx, duration):
            async_context = ctx.async_context
            assert async_context.tasks
            done, pending = async_context.loop.run_until_complete(asyncio.wait(
                async_context.tasks, loop=async_context.loop, timeout=duration))
            assert len(pending) == 0

        # -- COROUTINE:
        async def my_async_func(param):
            await asyncio.sleep(0.5)
            return param.upper()
    """
    # pylint: enable=line-too-long
    default_name = "async_context"

    def __init__(self, name=None, loop=None, should_close=False, tasks=None):
        if name and not isinstance(name, six.string_types):
            raise TypeError("name: {!r} (expected: string)".format(name))

        self.loop = use_or_assign_event_loop(loop)
        self.tasks = tasks or []
        self.name = name or self.default_name
        self.should_close = should_close

    def __del__(self):
        # print("DIAG: AsyncContext.dtor: {}".format(self.name))
        if self.loop and self.should_close:
            self.close()

    def close(self):
        if self.loop and not self.loop.is_closed():
            # print("DIAG: AsyncContext.close: {}".format(self.name))
            self.loop.close()
        self.loop = None
