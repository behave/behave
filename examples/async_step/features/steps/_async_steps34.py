# -- REQUIRES: Python >= 3.4 and Python < 3.8
# HINT: Decorator @asyncio.coroutine is prohibited in python 3.8
# USE:  Async generator/coroutine instead.

from behave import step
from behave.api.async_step import async_run_until_complete
import asyncio

# -- USABLE FOR: "3.4" <= python_version < "3.8"
@step('an async-step waits {duration:f} seconds')
@async_run_until_complete
@asyncio.coroutine
def step_async_step_waits_seconds_py34(context, duration):
    yield from asyncio.sleep(duration)
