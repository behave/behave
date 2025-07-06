@use.with_python.min_version=3.5
Feature: Async-Step with Step Decorator

  DEPRECATING: Better use normal step decorators (since: behave v1.2.7).

  As a test writer and step provider
  I want to test async frameworks or protocols (that use asyncio)

  . USE CASES:
  .   * async-step with run-to-complete semantics (like synchronous step)
  .   * async-dispatch-and-collect-results-later:
  .     one or more steps dispatch async-calls (tasks)
  .     and final step(s) that waits until tasks have been completed
  .     (collects the results of the async-calls and verifies them)
  .
  . TERMINOLOGY: async-step
  .  An async-step is either
  .    * an async-function as coroutine using async/await keywords (Python >= 3.5)
  .
  .  # -- EXAMPLE CASE 1 (since Python 3.5):
  .  async def coroutine1(duration):
  .      await asyncio.sleep(duration)
  .
  . RATIONALE:
  .   By using async-steps, an additional layer of indirection is avoided.
  .   The async-step can directly interact with other async-functions.


    Scenario: Use Async-Step with Step Decorator
      Given a new working directory
      And a file named "features/steps/async_steps35.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete
        import asyncio

        @step('an async-step waits {duration:f} seconds')
        @async_run_until_complete
        async def step_async_step_waits_seconds(context, duration):
            await asyncio.sleep(duration)
        """
      And a file named "features/async_run.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step waits 0.2 seconds
        """
      When I run "behave -f plain --show-timings features/async_run.feature"
      Then it should pass with:
        """
        Feature:
           Scenario:
             Given an async-step waits 0.2 seconds ... passed in 0.2
        """


    @use.with_python.min_version=3.11
    Scenario: Use @async_run_until_complete(timeout=...) and TIMEOUT occurs (async-function)
      Given a new working directory
      And a file named "features/steps/async_steps_timeout35.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete
        import asyncio

        @step('an async-step waits {duration:f} seconds with timeout')
        @async_run_until_complete(timeout=0.1)  # BAD-TIMEOUT-BY-DESIGN
        async def step_async_step_waits_seconds_with_timeout35(context, duration):
            await asyncio.sleep(duration)
        """
      And a file named "features/async_timeout35.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step waits 1.0 seconds with timeout
        """
      When I run "behave -f plain --show-timings features/async_timeout35.feature"
      Then it should fail with:
        """
        0 steps passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
        Given an async-step waits 1.0 seconds with timeout ... failed in 0.1
        """
      And the command output should contain:
        """
        ASSERT FAILED: TIMEOUT-OCCURRED: timeout=0.1
        """

    @async_step_fails
    Scenario: Use @async_run_until_complete and async-step fails (async-function)
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
        @async_run_until_complete
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
      When I run "behave -f plain features/async_failure.feature"
      Then it should fail with:
        """
        1 step passed, 1 failed, 1 skipped
        """
      And the command output should contain:
        """
        When an async-step fails ... failed
        """
      And the command output should contain:
        """
        ASSERT FAILED: XFAIL in async-step
        """

    @async_step_fails
    Scenario: Use @async_run_until_complete and async-step raises error (async-function)
      Given a new working directory
      And a file named "features/steps/async_steps_exception35.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete

        @step('an async-step passes')
        @async_run_until_complete
        async def step_async_step_passes(context):
            pass

        @step('an async-step raises an exception')
        @async_run_until_complete
        async def step_async_step_raises_exception(context):
            raise RuntimeError("XFAIL in async-step")
        """
      And a file named "features/async_exception35.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step passes
            When an async-step raises an exception
            Then an async-step passes
        """
      When I run "behave -f plain features/async_exception35.feature"
      Then it should fail with:
        """
        1 step passed, 0 failed, 1 error, 1 skipped
        """
      And the command output should contain:
        """
        When an async-step raises an exception ... error
        """
      And the command output should contain:
        """
        raise RuntimeError("XFAIL in async-step")
        """

    Scenario: Sync-Step with Async-Step Decorator raises StepFunctionTypeError

      NOTE: This error is raised during the steps loading phase.

      Given a new working directory
      And a file named "features/steps/sync_steps.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete
        from time import sleep

        @step('a sync-step waits {duration:f} seconds')
        @async_run_until_complete  # PROBLEM-POINT: Needs async-function
        def sync_step_waits_seconds(context, duration):
            sleep(duration)
        """
      And a file named "features/async_sync_mismatch.feature" with:
        """
        Feature:
          Scenario:
            Given an sync-step waits 0.2 seconds
        """
      When I run "behave -f plain features/async_sync_mismatch.feature"
      Then it should fail with:
        """
        StepFunctionTypeError: function (NEEDS: async-function)
        """
