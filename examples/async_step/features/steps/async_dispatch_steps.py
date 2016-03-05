from behave import given, then, step
from behave.api.async_step import use_or_create_async_context, AsyncContext
from hamcrest import assert_that, equal_to, empty
import asyncio

@asyncio.coroutine
def async_func(param):
    yield from asyncio.sleep(0.2)
    return str(param).upper()

@given('I dispatch an async-call with param "{param}"')
def step_dispatch_async_call(context, param):
    async_context = use_or_create_async_context(context, "async_context1")
    task = async_context.loop.create_task(async_func(param))
    async_context.tasks.append(task)

@then('the collected result of the async-calls is "{expected}"')
def step_collected_async_call_result_is(context, expected):
    async_context = context.async_context1
    done, pending = async_context.loop.run_until_complete(
        asyncio.wait(async_context.tasks, loop=async_context.loop))

    parts = [task.result() for task in done]
    joined_result = ", ".join(sorted(parts))
    assert_that(joined_result, equal_to(expected))
    assert_that(pending, empty())
