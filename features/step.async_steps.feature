@not.with_python2=true
@use.with_python_has_coroutine=true
Feature: Async-Test Support (async-step, ...)

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
  .    * an async-function as coroutine using async/await keywords (Python 3.5)
  .    * an async-function tagged with @asyncio.coroutine and using "yield from"
  .
  .  # -- EXAMPLE CASE 1 (since Python 3.5; preferred):
  .  async def coroutine1(duration):
  .      await asyncio.sleep(duration)
  .
  .  # -- EXAMPLE CASE 2 (since Python 3.4; deprecated since Python 3.8; removed in Python 3.10):
  .  @asyncio.coroutine
  .  def coroutine2(duration):
  .      yield from asyncio.sleep(duration)
  .
  . RATIONALE:
  .   By using async-steps, an additional layer of indirection is avoided.
  .   The async-step can directly interact with other async-functions.


    @use.with_python_has_async_function=true
    Scenario: Use async-step with @async_run_until_complete (async; requires: py.version >= 3.5)
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


    @use.with_python_has_asyncio.coroutine_decorator=true
    Scenario: Use async-step with @async_run_until_complete (@asyncio.coroutine)
      Given a new working directory
      And a file named "features/steps/async_steps34.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete
        import asyncio

        @step('an async-step waits {duration:f} seconds')
        @async_run_until_complete
        @asyncio.coroutine
        def step_async_step_waits_seconds2(context, duration):
            yield from asyncio.sleep(duration)
        """
      And a file named "features/async_run.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step waits 0.3 seconds
        """
      When I run "behave -f plain --show-timings features/async_run.feature"
      Then it should pass with:
        """
        Feature:
           Scenario:
             Given an async-step waits 0.3 seconds ... passed in 0.3
        """

    @use.with_python_has_async_function=true
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
        0 steps passed, 1 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Given an async-step waits 1.0 seconds with timeout ... failed in 0.1
        """
      And the command output should contain:
        """
        Assertion Failed: TIMEOUT-OCCURED: timeout=0.1
        """

    @use.with_python_has_async_function=true
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
        1 step passed, 1 failed, 1 skipped, 0 undefined
        """
      And the command output should contain:
        """
        When an async-step fails ... failed
        """
      And the command output should contain:
        """
        Assertion Failed: XFAIL in async-step
        """

    @use.with_python_has_async_function=true
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
        1 step passed, 1 failed, 1 skipped, 0 undefined
        """
      And the command output should contain:
        """
        When an async-step raises an exception ... failed
        """
      And the command output should contain:
        """
        raise RuntimeError("XFAIL in async-step")
        """

    @use.with_python_has_asyncio.coroutine_decorator=true
    Scenario: Use @async_run_until_complete(timeout=...) and TIMEOUT occurs (@asyncio.coroutine)
      Given a new working directory
      And a file named "features/steps/async_steps_timeout34.py" with:
        """
        from behave import step
        from behave.api.async_step import async_run_until_complete
        import asyncio

        @step('an async-step waits {duration:f} seconds with timeout')
        @async_run_until_complete(timeout=0.2)  # BAD-TIMEOUT-BY-DESIGN
        @asyncio.coroutine
        def step_async_step_waits_seconds_with_timeout34(context, duration):
            yield from asyncio.sleep(duration)
        """
      And a file named "features/async_timeout34.feature" with:
        """
        Feature:
          Scenario:
            Given an async-step waits 1.0 seconds with timeout
        """
      When I run "behave -f plain --show-timings features/async_timeout34.feature"
      Then it should fail with:
        """
        0 steps passed, 1 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Given an async-step waits 1.0 seconds with timeout ... failed in 0.2
        """
      And the command output should contain:
        """
        Assertion Failed: TIMEOUT-OCCURED: timeout=0.2
        """

    @use.with_python_has_asyncio.coroutine_decorator=true
    Scenario: Use async-dispatch and async-collect concepts (@asyncio.coroutine)
      Given a new working directory
      And a file named "features/steps/async_dispatch_steps.py" with:
        """
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
        """
      And a file named "features/async_dispatch.feature" with:
        """
        Feature:
          Scenario:
            Given I dispatch an async-call with param "Alice"
            And   I dispatch an async-call with param "Bob"
            Then the collected result of the async-calls is "ALICE, BOB"
        """
      When I run "behave -f plain --show-timings features/async_dispatch.feature"
      Then it should pass with:
        """
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Given I dispatch an async-call with param "Alice" ... passed in 0.00
        """
      And the command output should contain:
        """
        And I dispatch an async-call with param "Bob" ... passed in 0.00
        """
      And the command output should contain:
        """
        Then the collected result of the async-calls is "ALICE, BOB" ... passed in 0.2
        """
      But note that "the async-collect step waits 0.2 seconds for both async-tasks to finish"
      And note that "the async-dispatch steps do not wait at all"
