@use.with_python.min_version=3.5
Feature: Fixture that uses an Async-Resource

  As a BDD writer
  I want to use a fixture that uses an Async-Resource
  So that I can better use/setup/teardown async/asyncio-based functionality.

  . SEE: Async Fixtures -- https://github.com/behave/behave/issues/1211
  . RELATED: features/fixture.feature
  . RELATED TO: asyncio.Runner (since: Python 3.11)
  .   * Use "backports.asyncio.runner" for older Python versions.
  .   * SEE: https://pypi.org/project/backports.asyncio.runner

  Background: Feature Setup
    Given a new working directory
    And an empty file named "example4me/__init__.py"
    And a file named "example4me/async_resource.py" with:
      """
      class AsyncResource:
          def __init__(self, name: str):
              self.name = name
              self.started = False

          async def start(self):
              print(f"Starting AsyncResource={self.name} ...")
              self.started = True

          async def stop(self):
              print(f"Stopping AsyncResource={self.name} ...")
      """
    And a file named "example4me/async_fixture.py" with:
      """
      import asyncio
      from behave import fixture
      from .async_resource import AsyncResource

      def asyncio_run(coroutine):
          # -- SOLUTION 1:
          return asyncio.run(coroutine)
          # -- SOLUTION 2: Since Python 3.11 (or use backport for older versions)
          # runner = asyncio.Runner()
          # return runner.run(coroutine)
          # -- SOLUTION 3:
          # this_loop = asyncio.get_event_loop()
          # return this_loop.run_until_complete(coroutine)

      @fixture
      def service(ctx, name=None):
          print(f"FIXTURE-SETUP: service={name}")
          name = name or "SERVICE_ONE"
          this_service = AsyncResource(name)
          def stop_service():
              asyncio_run(this_service.stop())
          ctx.add_cleanup(stop_service)
          ctx.service_one = this_service
          asyncio_run(this_service.start())
          yield this_service
          # -- CLEANUP-PHASE: Implicitly calls cleanup-function.
          print(f"FIXTURE-CLEANUP: service={name}")
      """
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And an empty file named "features/environment.py"


  Scenario: Use AsyncResource in a fixture
    Given a file named "features/environment.py" with:
      """
      from __future__ import absolute_import, print_function
      from behave.capture import any_hook
      from behave.fixture import fixture, use_fixture
      from example4me.async_fixture import service

      # -- ENABLE CAPTURED-OUTPUT:
      any_hook.show_capture_on_success = True
      any_hook.show_cleanup_on_success = True

      # -- HOOKS:
      def before_tag(ctx, tag):
          if tag == "fixture.service=one":
              use_fixture(service, ctx, name="one")
      """
    And a file named "features/async_fixture.feature" with:
      """
      Feature: Use Fixture with AsyncResource
        @fixture.service=one
        Scenario: Fixture with service=one (as AsyncResource)
          Given a step passes

        Scenario: Another
          When another step passes
      """
    When I run "behave -f plain features/async_fixture.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
        Scenario: Fixture with service=one (as AsyncResource)
      ----
      CAPTURED STDOUT: before_tag
      FIXTURE-SETUP: service=one
      Starting AsyncResource=one ...
      ----
          Given a step passes ... passed
      ----
      CAPTURED STDOUT: scenario.cleanup
      Stopping AsyncResource=one ...
      FIXTURE-CLEANUP: service=one
      ----
      """
