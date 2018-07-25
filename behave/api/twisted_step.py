"""
This module provides functionality to support twisted
in a step-module with behave.

The principle is to use two threads:
- main thread running behave
- auxiliary thread running twisted reactor

For this you need a environment.py including the following:

.. code-block: python

    from threading import Thread
    # If you want you can choose an alternative reactor here
    from twisted.internet import reactor

    def before_all(context):
        # If you want to start something add the following:
        # reactor.callWhenRunning(f, *args, **kwargs)
        context.reactor = reactor
        context.thread = Thread(target=reactor.run, kwargs={"installSignalHandlers": False})
        context.thread.start()

    def after_all(context):
        reactor.callFromThread(context.reactor.stop)
        context.thread.join()

Then you can call in your twisted steps:

.. code-block: python

    from behave import given, when, then
    from twisted.internet import defer
    from twisted_step import twisted_run_until_complete

    @then('receive an event')
    @twisted_run_until_complete # (timeout=1)
    def step_impl(context):
        # Step running in twisted reactor thread
        # raise Exception("an exception in step")
        deferred = defer.Deferred()
        context.reactor.callLater(3, deferred.callback, None)
        return deferred

.. note::

    If the timeout is fired, the step will continue.
    You have the responsability to take any action
    to cleanup the steps that were timeouted.

Copyright (c) 2018 Philippe Goetz - Siemens AG
"""
import functools
import threading
import twisted.internet
from twisted.internet import defer


class ThreadContext(object):
    def __init__(self, context):
        self.context = context
        self.event = threading.Event()
        self.result = None
        self.deferred = None


def wrapper(thread_context, astep_func, args, kwargs):
    # Run in twisted reactor thread
    def callback(result):
        thread_context.result = result
        thread_context.event.set()
    thread_context.deferred = defer.maybeDeferred(astep_func, thread_context.context, *args, **kwargs)
    thread_context.deferred.addBoth(callback)

# -----------------------------------------------------------------------------
# DEFERRED STEP DECORATOR
# -----------------------------------------------------------------------------
def twisted_run_until_complete(astep_func=None, timeout=None):
    """
    Provides a function decorator that will execute the decorated function
    in twisted reactor thread.

    Parameters:
        astep_func: step function that will be executed in twisted reactor thread
                    it can be synchronous or asynchronous.
        timeout (int, float):       Timeout to wait for function completion.
    """

    def step_decorator(astep_func, context, *args, **kwargs):
        # Run in behave thread
        timeout = kwargs.pop("_timeout", None)
        thread_context = ThreadContext(context)
        # call the astep_func in twisted reactor thread
        context.reactor.callFromThread(wrapper, thread_context, astep_func, args, kwargs)
        finished = thread_context.event.wait(timeout)
        if not finished:
            # cancel the deferred in twisted reactor thread
            context.reactor.callFromThread(thread_context.deferred.cancel)
            # thread_context.event.wait()
            assert finished, "TIMEOUT-OCCURED: timeout=%s" % timeout
        if isinstance(thread_context.result, defer.failure.Failure):
            thread_context.result.raiseException()

    if astep_func is None:
        # -- CASE: @decorator(timeout=1.2, ...)
        # MAYBE: return functools.partial(step_decorator,
        def wrapped_decorator1(astep_func):
            @functools.wraps(astep_func)
            def wrapped_decorator2(context, *args, **kwargs):
                return step_decorator(astep_func, context, *args,
                                      _timeout=timeout,
                                      **kwargs)
            assert callable(astep_func)
            return wrapped_decorator2
        return wrapped_decorator1
    else:
        # -- CASE: @decorator ... or astep = decorator(astep)
        # MAYBE: return functools.partial(step_decorator, astep_func=astep_func)
        assert callable(astep_func)
        @functools.wraps(astep_func)
        def wrapped_decorator(context, *args, **kwargs):
            return step_decorator(astep_func, context, *args, **kwargs)
        return wrapped_decorator

# -- ALIAS:
run_until_complete = twisted_run_until_complete
