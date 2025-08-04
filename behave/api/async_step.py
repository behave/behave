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

    @step('an async coroutine step waits {duration:f} seconds')
    async def step_async_step_waits_seconds(context, duration):
        await asyncio.sleep(duration)

.. requires:: Python 3.5

    * https://docs.python.org/3/library/asyncio.html

.. _asyncio.coroutines: https://docs.python.org/3/library/asyncio-task.html#coroutines
"""
# pylint: enable=line-too-long

# -- REQUIRES: Python >= 3.5
from __future__ import absolute_import, print_function
import warnings as _warnings

from behave._types import require_callable as _require_callable
from behave.async_step import (
    # -- PART OF API:
    AsyncContext,  # noqa: F401
    use_or_assign_event_loop,
    use_or_create_async_context,  # noqa: F401

    # -- NOT PART OF API:
    AsyncStepFunction as _AsyncStepFunction,
)


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

    if astep_func is None:
        # -- CASE: @decorator(timeout=1.2, ...)
        def wrapped_decorator(astep_func):
            async_step_func = _AsyncStepFunction(astep_func,
                                                 timeout=timeout,
                                                 loop=loop,
                                                 async_context=async_context)
            return async_step_func
        return wrapped_decorator
    else:
        # -- CASE: @decorator ... or astep = decorator(astep)
        _require_callable(astep_func)
        async_step_func = _AsyncStepFunction(astep_func,
                                             timeout=timeout,
                                             loop=loop,
                                             async_context=async_context)
        return async_step_func

# -- ALIAS:
run_until_complete = async_run_until_complete


# -----------------------------------------------------------------------------
# ASYNC STEP UTILITY FUNCTIONS:
# -----------------------------------------------------------------------------
def use_or_create_event_loop(loop=None):
    message = "use_or_create_event_loop: Use use_or_assign_event_loop() instead"
    _warnings.warn(message, PendingDeprecationWarning)
    return use_or_assign_event_loop(loop)
