# -- REQUIRES: Python >= 3.4
from behave import step
from behave.api.async_step import async_run_until_complete
import asyncio

@step('an async-step waits {duration:f} seconds')
@async_run_until_complete
@asyncio.coroutine
def step_async_step_waits_seconds_py34(context, duration):
    yield from asyncio.sleep(duration)
