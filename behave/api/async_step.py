# -*- coding: UTF-8 -*-
# pylint: disable=line-too-long
"""
This module provides functionality to support "async steps" (coroutines)
in a step-module with behave. This functionality simplifies to test
frameworks and protocols that make use of `asyncio.coroutines`_ or
provide `asyncio.coroutines`_.

EXAMPLE:

.. code-block:: python

    # -- FILE: features/steps/my_async_steps.py
    # EXAMPLE REQUIRES: Python >= 3.5
    from behave import step
    from behave.api.async_step import async_run_until_complete

    @step('an async coroutine step waits {duration:f} seconds')
    @async_run_until_complete
    async def step_async_step_waits_seconds(context, duration):
        await asyncio.sleep(duration)

.. requires:: Python 3.5 (or 3.4) or :mod:`asyncio` backport (like :pypi:`trollius`)
.. seealso::
    https://docs.python.org/3/library/asyncio.html

.. _asyncio.coroutines: https://docs.python.org/3/library/asyncio-task.html#coroutines
"""
# pylint: enable=line-too-long

# -- REQUIRES: Python >= 3.5
from __future__ import absolute_import, print_function
import warnings as _warnings


# -----------------------------------------------------------------------------
# ASYNC STEP DECORATORS:
# -----------------------------------------------------------------------------
def async_run_until_complete(astep_func=None, timeout=None,
                             loop=None, async_context=None):
    """
    Provides a function decorator for async-steps (coroutines).
    Provides an async event loop and runs the async-step until completion
    (or timeout, if specified).

    .. code-block:: python

        # -- DEPRECATING: No longer needed (supported by normal step decorators)
        from behave import step
        from behave.api.async_step import async_run_until_complete
        import asyncio

        @step("an async step is executed")
        @async_run_until_complete
        async def astep_impl(context)
            await asycio.sleep(0.1)

        @step("an async step is executed")
        @async_run_until_complete(timeout=1.2)
        async def astep_impl2(context)
            # -- NOTE: Wrapped event loop waits with timeout=1.2 seconds.
            await asycio.sleep(0.3)

    Parameters:
        astep_func: Async step function (coroutine)
        timeout (int, float):       Timeout to wait for async-step completion.
        loop (asyncio.EventLoop):   Event loop to use or None.
        async_context (name):       Async_context name or object to use.

    .. note::

        * If :param:`timeout` is provided, the event loop waits only the
          specified time.
        * If :param:`loop` is None, the default event loop will be used
          or a new event loop is created.
        * :param:`async_context` is only used, if :param:`loop` is None.
        * If :param:`async_context` is a name, it will be used to retrieve
          the real async_context object from the context.

    .. deprecated:: 1.2.7
        This step decorator is no longer needed. Use normal step decorators instead.

    .. versionremoved:: 1.4.0
        Support of async-step functions was added to normal step decorators.
    """
    message = "@async_run_until_complete (no longer needed)."
    _warnings.warn(message, PendingDeprecationWarning, stacklevel=2)
    from behave.async_step import AsyncStepFunction
    if astep_func is None:
        # -- CASE: @decorator(timeout=1.2, ...)
        def wrapped_decorator(astep_func):
            async_step_func = AsyncStepFunction(astep_func,
                                                timeout=timeout,
                                                loop=loop,
                                                async_context=async_context)
            return async_step_func
        return wrapped_decorator
    else:
        # -- CASE: @decorator ... or astep = decorator(astep)
        assert callable(astep_func)
        async_step_func = AsyncStepFunction(astep_func,
                                            timeout=timeout,
                                            loop=loop,
                                            async_context=async_context)
        return async_step_func

# -- ALIAS:
run_until_complete = async_run_until_complete


# -----------------------------------------------------------------------------
# ASYNC STEP UTILITY CLASSES:
# -----------------------------------------------------------------------------
class AsyncContext(object):
    # pylint: disable=line-too-long
    """Provides a context object for "async steps" to keep track:

    * which event loop is used
    * which (asyncio) tasks are used or of interest

    .. attribute:: loop
        Event loop object to use.
        If none is provided, the current event-loop is used
        (or a new one is created).

    .. attribute:: tasks
        List of started :mod:`asyncio` tasks (of interest).

    .. attribute:: name

        Optional name of this object (in the behave context).
        If none is provided, :attr:`AsyncContext.default_name` is used.

    .. attribute:: should_close
        Indicates if the :attr:`loop` (event-loop) should be closed or not.

    EXAMPLE:

    .. code-block:: python

        # -- FILE: features/steps/my_async_steps.py
        # REQUIRES: Python 3.5
        from behave import given, when, then, step
        from behave.api.async_step import AsyncContext

        @when('I dispatch an async-call with param "{param}"')
        def step_impl(context, param):
            async_context = getattr(context, "async_context", None)
            if async_context is None:
                async_context = context.async_context = AsyncContext()
            task = async_context.loop.create_task(my_async_func(param))
            async_context.tasks.append(task)

        @then('I wait at most {duration:f} seconds until all async-calls are completed')
        def step_impl(context, duration):
            async_context = context.async_context
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

    def __init__(self, loop=None, name=None, should_close=False, tasks=None):
        from behave.async_step import use_or_assign_event_loop
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


# -----------------------------------------------------------------------------
# ASYNC STEP UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def use_or_create_event_loop(loop=None):
    from behave.async_step import use_or_assign_event_loop
    message = "use_or_create_event_loop: Use use_or_assign_event_loop() instead"
    _warnings.warn(message, PendingDeprecationWarning)
    return use_or_assign_event_loop(loop)


def use_or_create_async_context(context, name=None, loop=None, **kwargs):
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
        def step_impl(context, param):
            async_context = use_or_create_async_context(context, "async_context")
            task = async_context.loop.create_task(my_async_func(param))
            async_context.tasks.append(task)

        # -- COROUTINE:
        async def my_async_func(param):
            await asyncio.sleep(0.5)
            return param.upper()

    :param context:     Behave context object to use.
    :param name:        Optional name of async-context object (as string or None).
    :param loop:        Optional event_loop object to use for create call.
    :param kwargs:      Optional :class:`AsyncContext` params for create call.
    :return: :class:`AsyncContext` object from the param:`context`.
    """
    if name is None:
        name = AsyncContext.default_name
    async_context = getattr(context, name, None)
    if async_context is None:
        async_context = AsyncContext(loop=loop, name=name, **kwargs)
        setattr(context, async_context.name, async_context)
    assert isinstance(async_context, AsyncContext)
    assert getattr(context, async_context.name) is async_context
    return async_context
