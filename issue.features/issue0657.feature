@issue
@not.with_python2=true
Feature: Issue #657 -- Allow async steps with timeouts to fail when they raise exceptions

    @use.with_python_has_async_function=true
    @async_step_fails
    Scenario: Use @async_run_until_complete and async-step fails (py.version >= 3.8)
      Given a new working directory
      And a file named "features/steps/async_steps_fails35.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete

        @step('an async-step passes')
        @async_run_until_complete
        async def step_async_step_passes(context):
            pass

        @step('an async-step fails')
        @async_run_until_complete(timeout=2)
        async def step_async_step_fails(context):
            assert False, "XFAIL in async-step"
        """
      And a file named "features/async_failure.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step passes
            When an async-step fails
            Then an async-step passes
        """
      When I run "behave -f plain --show-timings features/async_failure.feature"
      Then it should fail with:
        """
        1 step passed, 1 failed, 1 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Assertion Failed: XFAIL in async-step
        """
      And the command output should contain:
        """
        When an async-step fails ... failed in 0.0
        """
      But note that "the async-step should fail immediately"
