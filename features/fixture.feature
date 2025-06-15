Feature: Fixture

  As a BDD writer
  I want to be able to use fixtures (scope guard)
  So that it is easy to provide setup/cleanup functionality.

  . SPECIFICATION:
  .   A fixture provides common test-support functionality.
  .   It contains the setup functionality and in many cases a teardown/cleanup part.
  .   To simplify writing fixtures, setup and cleanup part are in the same function
  .   (same as: @contextlib.contextmanager, @pytest.fixture).
  .
  .   In most case, you want to use a fixture-tag in a "*.feature" file (in Gherkin)
  .   to mark that a scenario or feature should use a specific fixture.
  .
  .   EXAMPLE:
  .
  .     # -- FILE: features/environment.py
  .     @fixture
  .     def fixture_foo(ctx, *args, **kwargs):  # -- CASE: generator-function
  .         the_fixture = setup_fixture_foo(*args, **kwargs)
  .         ctx.foo = the_fixture
  .         yield the_fixture
  .         cleanup_fixture_foo(the_fixture)   # -- SKIPPED: On fixture-setup-error
  .
  .     @fixture(name="fixture.bar")
  .     def fixture_bar(ctx, *args, **kwargs):  # -- CASE: function
  .         the_fixture = setup_fixture_bar(*args, **kwargs)
  .         ctx.bar = the_fixture
  .         ctx.add_cleanup(the_fixture.cleanup)
  .         return the_fixture
  .
  .     # -- ENVIRONMENT-HOOKS:
  .     def before_tag(ctx, tag):
  .         if tag == "fixture.foo":
  .             # -- NOTE: Calls setup_fixture part (until yield statement) and
  .             #    registers cleanup_fixture which will be called when
  .             #    context scope is left (after scenario, feature or test-run).
  .             the_fixture = use_fixture(fixture_foo, ctx)

  Background:
    Given a new working directory
    And a file named "features/steps/browser_steps.py" with:
      """
      from behave import step

      @step(u'the browser is "{browser_name}"')
      def step_browser_is(ctx, browser_name):
          assert ctx.browser == browser_name

      @step(u'no browser info exists')
      def step_no_browser_info(ctx):
          assert not hasattr(ctx, "browser")

      @step(u'{word:w} step passes')
      def step_passes(ctx, word):
          pass
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """
    And an empty file named "features/environment.py"

  Rule: Fixture Variants
    Scenario: Use fixture with generator-function (setup/cleanup)
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook
        from behave.fixture import fixture, use_fixture

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        @fixture(name="browser.firefox")
        def browser_firefox(ctx):
            print("FIXTURE-SETUP: browser.firefox")
            ctx.browser = "firefox"
            yield
            print("FIXTURE-CLEANUP: browser.firefox")
            # -- SCOPE-CLEANUP OR EXPLICIT: del ctx.browser

        def before_tag(ctx, tag):
            if tag == "fixture.browser.firefox":
                use_fixture(browser_firefox, ctx)
        """
      And a file named "features/alice.feature" with:
        """
        Feature: Fixture setup/teardown
          @fixture.browser.firefox
          Scenario: Fixture with browser=firefox
            Given the browser is "firefox"

          Scenario: Fixture Cleanup check
            Then no browser info exists
        """
      When I run "behave -f plain features/alice.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: Fixture with browser=firefox
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: browser.firefox
        ----
            Given the browser is "firefox" ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: browser.firefox
        ----
        """

    Scenario: Use fixture with function (setup-only)
      Given a file named "features/environment.py" with:
        """
        from __future__ import print_function
        from behave.capture import any_hook
        from behave.fixture import fixture, use_fixture

        any_hook.show_capture_on_success = True

        @fixture(name="browser.chrome")
        def browser_chrome(ctx):
            # -- CASE: Setup-only
            print("FIXTURE-SETUP: browser.chrome")
            ctx.browser = "chrome"

        def before_tag(ctx, tag):
            if tag == "fixture.browser.chrome":
                use_fixture(browser_chrome, ctx)
        """
      And a file named "features/bob.feature" with:
        """
        Feature: Fixture setup only
          @fixture.browser.chrome
          Scenario: Fixture with browser=chrome
            Given the browser is "chrome"

          Scenario: Fixture Cleanup check
            Then no browser info exists
        """
      When I run "behave -f plain features/bob.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: Fixture with browser=chrome
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: browser.chrome
        ----
            Given the browser is "chrome" ... passed

          Scenario: Fixture Cleanup check
            Then no browser info exists ... passed
        """

  Rule: Use Fixture
    Background:
      Given an empty file named "example4me/__init__.py"
      And a file named "example4me/fixtures.py" with:
        """
        from __future__ import print_function
        from behave import fixture

        @fixture
        def foo(ctx, suffix=""):
            name = "foo{}".format(suffix).rstrip()
            print("FIXTURE-SETUP: {name}".format(name=name))
            yield 42
            print("FIXTURE-CLEANUP: {name}".format(name=name))
        """
      And a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook
        from behave.fixture import fixture, use_fixture
        from example4me.fixtures import foo

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        def before_tag(ctx, tag):
            if tag == "fixture.foo":
                use_fixture(foo, ctx)
        """
      And a file named "features/steps/fixture_steps.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave import step, use_fixture
        from example4me.fixtures import foo

        @step(u'I use fixture "{fixture_name}"')
        def step_use_fixture(ctx, fixture_name):
            if fixture_name.startswith("foo"):
                suffix = fixture_name.replace("foo", "")
                the_fixture = use_fixture(foo, ctx, suffix)
                setattr(ctx, fixture_name, the_fixture)
            else:
                raise LookupError("Unknown fixture: %s" % fixture_name)
        """

    Scenario: Use fixture (case: feature)
      Given a file named "features/use_by_feature.feature" with:
        """
        @fixture.foo
        Feature: Use Fixture for Feature

          Scenario: S1
            Given a step passes

          Scenario: S2
            Then another step passes
        """
      When I run "behave -f plain features/use_by_feature.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Use Fixture for Feature
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: foo
        ----
          Scenario: S1
            Given a step passes ... passed

          Scenario: S2
            Then another step passes ... passed
        ----
        CAPTURED STDOUT: feature.cleanup
        FIXTURE-CLEANUP: foo
        ----
        """
      But note that "the fixture-cleanup occurs after the feature"

    Scenario: Use fixture (case: scenario)
      Given a file named "features/use_by_scenario.feature" with:
        """
        Feature: Use Fixture in Scenario S1

          @fixture.foo
          Scenario: S1
            Given a step passes

          Scenario: S2
            Then another step passes
        """
      When I run "behave -f plain features/use_by_scenario.feature"
      Then it should pass
      And the command output should contain:
        """
        Feature: Use Fixture in Scenario S1
          Scenario: S1
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: foo
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: foo
        ----

          Scenario: S2
            Then another step passes ... passed
        """
      But note that "the fixture-cleanup occurs after the scenario"

    Scenario: Use fixture (case: step)
      Given a file named "features/use_by_step.feature" with:
        """
        @fixture.foo
        Feature: Use Fixture in S1 Step
          Scenario: S1
            Given I use fixture "foo_1"
            Then a step passes

          Scenario: S2
            Then another step passes
        """
      When I run "behave -f plain features/use_by_step.feature"
      Then it should pass
      And the command output should contain:
        """
        Feature: Use Fixture in S1 Step
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: foo
        ----
          Scenario: S1
            Given I use fixture "foo_1" ... passed
            Then a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: foo_1
        ----
        """
      But note that "the fixture-cleanup foo_1 occurs after the scenario"


    Scenario: Use fixture (case: feature, step)
      Given a file named "features/use_by_step.feature" with:
        """
        @fixture.foo
        Feature: Use Fixture in Feature and in S1 Step
          Scenario: S1
            Given I use fixture "foo_2"
            Then a step passes

          Scenario: S2
            Then another step passes
        """
      When I run "behave -f plain features/use_by_step.feature"
      Then it should pass
      And the command output should contain:
        """
        Feature: Use Fixture in Feature and in S1 Step
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: foo
        ----
          Scenario: S1
            Given I use fixture "foo_2" ... passed
            Then a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: foo_2
        ----

          Scenario: S2
            Then another step passes ... passed
        ----
        CAPTURED STDOUT: feature.cleanup
        FIXTURE-CLEANUP: foo
        ----
        """
      But note that "the fixture-cleanup foo_2 occurs after the scenario"
      But note that "the fixture-cleanup foo   occurs after the feature"


  Rule: Multiple Fixtures
    Scenario: Use multiple fixtures (with setup/cleanup)
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook
        from behave.fixture import fixture, use_fixture

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        @fixture
        def foo(ctx):
            print("FIXTURE-SETUP: foo")
            yield
            print("FIXTURE-CLEANUP: foo")

        @fixture
        def bar(ctx):
            def cleanup_bar():
                print("FIXTURE-CLEANUP: bar")

            print("FIXTURE-SETUP: bar")
            ctx.add_cleanup(cleanup_bar)

        def before_tag(ctx, tag):
            if tag == "fixture.foo":
                use_fixture(foo, ctx)
            elif tag == "fixture.bar":
                use_fixture(bar, ctx)
        """
      And a file named "features/two.feature" with:
        """
        Feature: Use multiple Fixtures
          @fixture.foo
          @fixture.bar
          Scenario: Two Fixtures
            Given a step passes

          Scenario:
            Then another step passes
        """
      When I run "behave -f plain features/two.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: Two Fixtures
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: foo
        FIXTURE-SETUP: bar
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: bar
        FIXTURE-CLEANUP: foo
        ----
        """
      But note that "the fixture-cleanup occurs in reverse order (LIFO)"


    Scenario: Use same fixture twice with different args
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook
        from behave.fixture import fixture, use_fixture

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        @fixture
        def foo(ctx, name):
            name2 = "foo%s" % name
            print("FIXTURE-SETUP: %s" % name2)
            setattr(ctx, name2, 1)
            yield
            print("FIXTURE-CLEANUP: %s" % name2)

        def before_tag(ctx, tag):
            if tag.startswith("fixture.foo"):
                # -- FIXTURE-TAG SCHEMA: fixture.foo*
                name = tag.replace("fixture.foo", "")
                use_fixture(foo, ctx, name)
        """
      And a file named "features/two.feature" with:
        """
        Feature: Use same Fixture twice
          @fixture.foo_1
          @fixture.foo_2
          Scenario: Use Fixtures
            Given a step passes

          Scenario:
            Then another step passes
        """
      When I run "behave -f plain features/two.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: Use Fixtures
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: foo_1
        FIXTURE-SETUP: foo_2
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: foo_2
        FIXTURE-CLEANUP: foo_1
        ----
        """
      But note that "the fixture-cleanup occurs in reverse order (LIFO)"

  Rule: Bad Fixture
    Scenario: Use invalid fixture (with two yields or more)
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook
        from behave.fixture import fixture, use_fixture

        any_hook.show_capture_on_success = True

        @fixture
        def invalid_fixture(ctx):
            # -- CASE: Setup-only
            print("FIXTURE-SETUP: invalid")
            yield
            print("FIXTURE-CLEANUP: invalid")
            yield
            print("OOPS: Too many yields used")

        def before_tag(ctx, tag):
            if tag == "fixture.invalid":
                use_fixture(invalid_fixture, ctx)
        """
      And a file named "features/invalid_fixture.feature" with:
        """
        Feature: Fixture with more than one yield
          @fixture.invalid
          Scenario: Use invalid fixture
            Given a step passes

          Scenario:
            Then another step passes
        """
      When I run "behave -f plain features/invalid_fixture.feature"
      Then it should fail with:
        """
        1 scenario passed, 0 failed, 1 cleanup_error, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: Use invalid fixture
        ----
        CAPTURED STDOUT: before_tag
        FIXTURE-SETUP: invalid
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        FIXTURE-CLEANUP: invalid
        CLEANUP-ERROR in cleanup_fixture: InvalidFixtureError: Has more than one yield: <function invalid_fixture at
        """
      But note that "cleanup errors cause scenario to fail (by default)"

Rule: Fixtures with Cleanup Errors

  Scenario: Fixture with cleanup-error causes failed (case: scenario)
    Given a file named "features/environment.py" with:
      """
      from __future__ import absolute_import, print_function
      from behave.capture import any_hook
      from behave.fixture import fixture, use_fixture

      any_hook.show_capture_on_success = True

      class SomeError(RuntimeError): pass

      @fixture
      def bad_with_cleanup_error(ctx):
          print("FIXTURE-SETUP: bad_with_cleanup_error")
          yield
          print("FIXTURE-CLEANUP: bad_with_cleanup_error")
          raise SomeError("BAD_FIXTURE_CLEANUP_ERROR")

      def before_tag(ctx, tag):
          if tag == "fixture.bad_with_cleanup_error":
              use_fixture(bad_with_cleanup_error, ctx)
      """
    And a file named "features/bad_fixture.feature" with:
      """
      Feature: Fixture with cleanup error
        @fixture.bad_with_cleanup_error
        Scenario: Use fixture
          Given a step passes

        Scenario:
          Then another step passes
      """
    When I run "behave -f plain features/bad_fixture.feature"
    Then it should fail with:
      """
      1 scenario passed, 0 failed, 1 cleanup_error, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
        Scenario: Use fixture
      ----
      CAPTURED STDOUT: before_tag
      FIXTURE-SETUP: bad_with_cleanup_error
      ----
          Given a step passes ... passed
      ----
      CAPTURED STDOUT: scenario.cleanup
      FIXTURE-CLEANUP: bad_with_cleanup_error
      CLEANUP-ERROR in cleanup_fixture: SomeError: BAD_FIXTURE_CLEANUP_ERROR
      """
    And the command output should contain "Traceback"
    And the command output should contain:
      """
      File "features/environment.py", line 14, in bad_with_cleanup_error
        raise SomeError("BAD_FIXTURE_CLEANUP_ERROR")
      """
    And the command output should contain:
      """
      SomeError: BAD_FIXTURE_CLEANUP_ERROR
      """
    But note that "traceback shows cleanup-fixture failure location"
    And note that "cleanup error causes scenario to fail (by default)"


  Scenario: Multiple fixture cleanup-errors cause no abort after first error (case: scenario)
    Given a file named "features/environment.py" with:
      """
      from __future__ import absolute_import, print_function
      from behave.capture import any_hook
      from behave.fixture import fixture, use_fixture

      any_hook.show_capture_on_success = True

      class SomeError(RuntimeError): pass

      @fixture
      def foo(ctx):
          print("FIXTURE-SETUP: foo")
          yield
          print("FIXTURE-CLEANUP: foo")

      @fixture
      def bad_with_cleanup_error(ctx, suffix=""):
          name = "bad_with_cleanup_error{}".format(suffix).rstrip()
          print("FIXTURE-SETUP: {name}".format(name=name))
          yield
          print("FIXTURE-CLEANUP: {name}".format(name=name))
          raise SomeError("BAD_FIXTURE_CLEANUP_ERROR%s" % suffix)

      def before_tag(ctx, tag):
          if tag.startswith("fixture.bad_with_cleanup_error"):
              suffix = tag.replace("fixture.bad_with_cleanup_error", "")
              use_fixture(bad_with_cleanup_error, ctx, suffix)
          elif tag.startswith("fixture.foo"):
              use_fixture(foo, ctx)
      """
    And a file named "features/bad_fixture2.feature" with:
      """
      Feature: Fixture with cleanup error
        @fixture.bad_with_cleanup_error_1
        @fixture.foo
        @fixture.bad_with_cleanup_error_2
        Scenario: Use fixture
          Given a step passes

        Scenario:
          Then another step passes
      """
    When I run "behave -f plain features/bad_fixture2.feature"
    Then it should fail with:
      """
      1 scenario passed, 0 failed, 1 cleanup_error, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
        Scenario: Use fixture
      ----
      CAPTURED STDOUT: before_tag
      FIXTURE-SETUP: bad_with_cleanup_error_1
      FIXTURE-SETUP: foo
      FIXTURE-SETUP: bad_with_cleanup_error_2
      ----
          Given a step passes ... passed
      ----
      CAPTURED STDOUT: scenario.cleanup
      FIXTURE-CLEANUP: bad_with_cleanup_error_2
      CLEANUP-ERROR in cleanup_fixture: SomeError: BAD_FIXTURE_CLEANUP_ERROR_2
      """
    And the command output should contain:
      """
      FIXTURE-CLEANUP: foo
      FIXTURE-CLEANUP: bad_with_cleanup_error_1
      CLEANUP-ERROR in cleanup_fixture: SomeError: BAD_FIXTURE_CLEANUP_ERROR_1
      """
    But note that "all fixture-cleanups are executed (even when errors occur)"
    And note that "fixture-cleanups are executed in reverse order (LIFO)"
