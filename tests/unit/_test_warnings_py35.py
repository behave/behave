import pytest
from behave.async_step import AsyncStepFunction
from behave.python_feature import PythonLibraryFeature


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
async def some_async_func(ctx):
    pass


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
# -- REQUIRES:
# * Python >= 3.5  -- Using async-function syntax
# * Python <  3.11 -- NOT-SUPPORTED YET: asyncio.timeout()
@pytest.mark.skipif(PythonLibraryFeature.has_asyncio_timeout(),
                    reason="asyncio.timeout() is supported.")
class TestAsyncStepFunction:
    def test_warning__ctor_with_timeout(self):
        """Ensure that the ``AsyncStepFunction(..., timeout=...)`` issues a warning."""
        with pytest.warns(RuntimeWarning, match=r"IGNORED: timeout"):
            _ = AsyncStepFunction(some_async_func, timeout=42)

    @pytest.mark.todo
    @pytest.mark.xfail
    def test_warning__call_with_timeout(self):
        this_async_step = AsyncStepFunction(some_async_func)
        this_async_step.timeout = 42
        context = None

        with pytest.warns(RuntimeWarning, match=r"IGNORED: asyncio.timeout()"):
            this_async_step(context)
