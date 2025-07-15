@use.with_python.min_version=3.5
Feature: Async-Step-Function(s) with AyncContext


  Background:
    Given a new working directory
    And a file named "features/steps/async_steps.py" with
      """
      import asyncio
      from behave.api.async_step import async_run_until_complete

      ASYNC_STEP_KWARGS = {
          # -- HINT: Provide name of the async-context object.
          "async_context": "async_ctx"
      }

      @step('{some:w} async step is executed')
      @async_run_until_complete(**ASYNC_STEP_KWARGS)
      async def astep_is_executed(ctx, some: str):
          await asyncio.sleep(0.1)

      async def run_this_task(name, duration):
          print(f"ASYNC_TASK: Starting {name}")
          await asyncio.sleep(duration)
          print(f"ASYNC_TASK: Finished {name}")

      @step('I start the task "{name}" with {duration:f} seconds duration')
      @async_run_until_complete(**ASYNC_STEP_KWARGS)
      async def astep_is_executed(ctx, name: str, duration: float):
          print(f"START-TASK: {name}")
          this_coroutine = run_this_task(name, duration)
          this_task = asyncio.create_task(this_coroutine)
          ctx.async_ctx.tasks.append(this_task)
          ctx.async_ctx.loop.call_soon(this_task)
          print(f"START-TASK: {name} (FINISHED)")

      @step('I wait until all async-tasks are completed')
      @async_run_until_complete(**ASYNC_STEP_KWARGS)
      async def astep_wait_until_tasks_are_completed(ctx):
          this_tasks = ctx.async_ctx.tasks
          print(f"WAIT FOR COMPLETION: {len(this_tasks)} task(s)")
          if this_tasks:
              for coro in asyncio.as_completed(this_tasks, timeout=10):
                  await coro
      """

  Rule: Use same async event-loop for the test-run

    Background:
      Given a file named "features/environment.py" with:
        """
        from behave.api.async_step import use_or_create_async_context

        def before_all(ctx):
            async_ctx = use_or_create_async_context(ctx, name="async_ctx")

            # -- PREPARE: Add cleanup to "after_all()" hook-position.
            def close_this_async_context():
                print("CLEANUP: Close my async-context.")
                async_ctx.close()
                print("CLEANUP: Close my async-context (FINISHED).")

            ctx.add_cleanup(close_this_async_context)
        """

    Scenario:
      Given a file named "features/two_scenarios.feature" with:
        """
        Feature: Two Scenarios
          Scenario: One
            Given an async step is executed
            When another async step is executed

          Scenario: Two
            Given I start the task "alice" with 0.3 seconds duration
            When I start the task "bob" with 0.2 seconds duration
            Then I wait until all async-tasks are completed
        """
      When I run "behave -f plain --show-timings --no-capture features/two_scenarios.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        5 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain "ASYNC_TASK: Starting alice"
      And the command output should contain "ASYNC_TASK: Starting bob"
      And the command output should contain "ASYNC_TASK: Finished bob"
      And the command output should contain "ASYNC_TASK: Finished alice"
      But note that "on Windows the finished-task order may vary sporadically"
