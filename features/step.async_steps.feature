@use.with_python.min_version=3.5
Feature: Async-Step Support

  SINCE: behave v1.2.7.dev7

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
  .  An async-step uses an async-function as coroutine using async/await keywords
  .  (requires: Python >= 3.5).
  .
  .  # -- EXAMPLE CASE (since Python 3.5):
  .  async def coroutine1(duration):
  .      await asyncio.sleep(duration)
  .
  . RATIONALE:
  .   By using async-steps, an additional layer of indirection is avoided.
  .   The async-step can directly interact with other async-functions.


    Scenario: Use Async-Step
      Given a new working directory
      And a file named "features/steps/async_steps35.py" with:
        """
        from behave import step
        import asyncio

        @step('an async-step waits {duration:f} seconds')
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

    Scenario: Use Async-Step with Timeout and NO_TIMEOUT occurs
      Given a new working directory
      And a file named "features/steps/async_steps_timeout35.py" with:
        """
        from behave import step
        import asyncio

        @step('an async-step waits {duration:f} seconds with timeout', timeout=0.1)
        async def step_async_step_waits_seconds_with_timeout(context, duration):
            await asyncio.sleep(duration)
        """
      And a file named "features/async_timeout35.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step waits 0.010 seconds with timeout
        """
      When I run "behave -f plain --no-timings features/async_timeout35.feature"
      Then it should pass with:
        """
        1 step passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Given an async-step waits 0.010 seconds with timeout ... passed
        """
      And the command output should not contain "TIMEOUT"

    @use.with_python.min_version=3.11
    Scenario: Use Async-Step with Timeout and TIMEOUT occurs
      Given a new working directory
      And a file named "features/steps/async_steps_timeout35.py" with:
        """
        from behave import step
        import asyncio

        # BAD-TIMEOUT-BY-DESIGN
        @step('an async-step waits {duration:f} seconds with timeout', timeout=0.1)
        async def step_async_step_waits_seconds_with_timeout(context, duration):
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
    Scenario: Use Async-Step that fails
      Given a new working directory
      And a file named "features/steps/async_steps_fails35.py" with:
        """
        from behave import step

        @step('an async-step passes')
        async def step_async_step_passes(context):
            pass

        @step('an async-step fails')
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
    Scenario: Use Async-Step that raises error
      Given a new working directory
      And a file named "features/steps/async_steps_exception35.py" with:
        """
        from behave import step

        @step('an async-step passes')
        async def step_async_step_passes(context):
            pass

        @step('an async-step raises an exception')
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
