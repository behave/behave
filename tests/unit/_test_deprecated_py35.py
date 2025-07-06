"""
Verifies that DeprecatedWarnings, PendingDeprecationWarnings work as expected.
"""

import pytest
from behave.api.async_step import (
    async_run_until_complete,
    use_or_create_event_loop,
)


# -- REQUIRES: Python >= 3.5 -- Using async-function syntax
class TestApiAsyncStep:
    """
    Covers :mod:`behave.api.async_step`.
    """

    def test_deprecated_async_run_until_complete(self):
        """Ensure that the ``@async_run_until_complete`` issues a warning."""
        with pytest.warns(PendingDeprecationWarning, match=r"@async_run_until_complete.*"):
            @async_run_until_complete
            async def async_step_example(ctx):
                pass

    def test_deprecated_use_or_create_event_loop(self):
        with pytest.warns(PendingDeprecationWarning, match=r"use_or_create_event_loop:.*"):
            _ = use_or_create_event_loop()
