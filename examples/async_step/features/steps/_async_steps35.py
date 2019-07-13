# -- REQUIRES: Python >= 3.5

from behave import step
from behave.api.async_step import async_run_until_complete
import asyncio

@step('an async-step waits {duration:f} seconds')
@async_run_until_complete
async def step_async_step_waits_seconds_py35(context, duration):
    """Simple example of a coroutine as async-step (in Python 3.5 or newer)"""
    await asyncio.sleep(duration)
