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
  .     def fixture_foo(context, *args, **kwargs):  # -- CASE: generator-function
  .         the_fixture = setup_fixture_foo(*args, **kwargs)
  .         context.foo = the_fixture
  .         yield the_fixture
  .         cleanup_fixture_foo(the_fixture)   # -- SKIPPED: On fixture-setup-error
  .
  .     @fixture(name="fixture.bar")
  .     def fixture_bar(context, *args, **kwargs):  # -- CASE: function
  .         the_fixture = setup_fixture_bar(*args, **kwargs)
  .         context.bar = the_fixture
  .         context.add_cleanup(the_fixture.cleanup)
  .         return the_fixture
  .
  .     # -- ENVIRONMENT-HOOKS:
  .     def before_tag(context, tag):
  .         if tag == "fixture.foo":
  .             # -- NOTE: Calls setup_fixture part (until yield statement) and
  .             #    registers cleanup_fixture which will be called when
  .             #    context scope is left (after scenario, feature or test-run).
  .             the_fixture = use_fixture(fixture_foo, context)

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step(u'the browser is "{browser_name}"')
      def step_browser_is(context, browser_name):
          assert context.browser == browser_name

      @step(u'no browser info exists')
      def step_no_browser_info(context):
          assert not hasattr(context, "browser")

      @step(u'{word:w} step passes')
      def step_passes(context, word):
          pass
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """
    And an empty file named "features/environment.py"


  Scenario: Use fixture with generator-function (setup/cleanup)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture(name="browser.firefox")
      def browser_firefox(context):
          print("FIXTURE-SETUP: browser.firefox")
          context.browser = "firefox"
          yield
          print("FIXTURE-CLEANUP: browser.firefox")
          # -- SCOPE-CLEANUP OR EXPLICIT: del context.browser

      def before_tag(context, tag):
          if tag == "fixture.browser.firefox":
              use_fixture(browser_firefox, context)
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
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: browser.firefox
        Scenario: Fixture with browser=firefox
          Given the browser is "firefox" ... passed
      FIXTURE-CLEANUP: browser.firefox
      """

  Scenario: Use fixture with function (setup-only)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture(name="browser.chrome")
      def browser_chrome(context):
          # -- CASE: Setup-only
          print("FIXTURE-SETUP: browser.chrome")
          context.browser = "chrome"

      def before_tag(context, tag):
          if tag == "fixture.browser.chrome":
              use_fixture(browser_chrome, context)
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
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: browser.chrome
        Scenario: Fixture with browser=chrome
          Given the browser is "chrome" ... passed

        Scenario: Fixture Cleanup check
          Then no browser info exists ... passed
      """

  Scenario: Use fixture (case: feature)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture
      def foo(context):
          print("FIXTURE-SETUP: foo")
          yield
          print("FIXTURE-CLEANUP: foo")

      def before_tag(context, tag):
          if tag == "fixture.foo":
              use_fixture(foo, context)

      def after_feature(context, feature):
          print("HOOK-CALLED: after_feature: %s" % feature.name)
      """
    And a file named "features/use2.feature" with:
      """
      @fixture.foo
      Feature: Use Fixture for Feature

        Scenario:
          Given a step passes

        Scenario:
          Then another step passes
      """
    When I run "behave -f plain features/use2.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: foo
      Feature: Use Fixture for Feature
        Scenario:
          Given a step passes ... passed

        Scenario:
          Then another step passes ... passed

      HOOK-CALLED: after_feature: Use Fixture for Feature
      FIXTURE-CLEANUP: foo
      """
    But note that "the fixture-cleanup after the feature"


  Scenario: Use fixture (case: step)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function

      def after_scenario(context, scenario):
          print("HOOK-CALLED: after_scenario: %s" % scenario.name)
      """
    And an empty file named "behave4me/__init__.py"
    And a file named "behave4me/fixtures.py" with:
      """
      from __future__ import print_function
      from behave import fixture

      @fixture
      def foo(context, name):
          print("FIXTURE-SETUP: foo%s" % name)
          yield 42
          print("FIXTURE-CLEANUP: foo%s" % name)
      """
    And a file named "features/steps/fixture_steps2.py" with:
      """
      from __future__ import print_function
      from behave import step, use_fixture
      from behave4me.fixtures import foo

      @step(u'I use fixture "{fixture_name}"')
      def step_use_fixture(context, fixture_name):
          if fixture_name.startswith("foo"):
              name = fixture_name.replace("foo", "")
              the_fixture = use_fixture(foo, context, name)
              setattr(context, fixture_name, the_fixture)
          else:
              raise LookupError("Unknown fixture: %s" % fixture_name)
      """
    And a file named "features/use3.feature" with:
      """
      @fixture.foo
      Feature:

        Scenario: Use Fixture
          Given I use fixture "foo_1"
          Then a step passes

        Scenario:
          Then another step passes
      """
    When I run "behave -f plain features/use3.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature:
        Scenario: Use Fixture
          Given I use fixture "foo_1" ... passed
          Then a step passes ... passed
        HOOK-CALLED: after_scenario: Use Fixture
        FIXTURE-CLEANUP: foo_1
      """
    But note that "the fixture-cleanup occurs after the scenario"


  Scenario: Use multiple fixtures (with setup/cleanup)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture
      def foo(context):
          print("FIXTURE-SETUP: foo")
          yield
          print("FIXTURE-CLEANUP: foo")

      @fixture
      def bar(context):
          def cleanup_bar():
              print("FIXTURE-CLEANUP: bar")

          print("FIXTURE-SETUP: bar")
          context.add_cleanup(cleanup_bar)

      def before_tag(context, tag):
          if tag == "fixture.foo":
              use_fixture(foo, context)
          elif tag == "fixture.bar":
              use_fixture(bar, context)
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
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: foo
      FIXTURE-SETUP: bar
        Scenario: Two Fixtures
          Given a step passes ... passed
      FIXTURE-CLEANUP: bar
      FIXTURE-CLEANUP: foo
      """
    But note that "the fixture-cleanup occurs in reverse order (LIFO)"


  Scenario: Use same fixture twice with different args
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture
      def foo(context, name):
          name2 = "foo%s" % name
          print("FIXTURE-SETUP: %s" % name2)
          setattr(context, name2, 1)
          yield
          print("FIXTURE-CLEANUP: %s" % name2)

      def before_tag(context, tag):
          if tag.startswith("fixture.foo"):
              # -- FIXTURE-TAG SCHEMA: fixture.foo*
              name = tag.replace("fixture.foo", "")
              use_fixture(foo, context, name)
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
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: foo_1
      FIXTURE-SETUP: foo_2
        Scenario: Use Fixtures
          Given a step passes ... passed
      FIXTURE-CLEANUP: foo_2
      FIXTURE-CLEANUP: foo_1
      """
    But note that "the fixture-cleanup occurs in reverse order (LIFO)"


  Scenario: Use invalid fixture (with two yields or more)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture
      def invalid_fixture(context):
          # -- CASE: Setup-only
          print("FIXTURE-SETUP: invalid")
          yield
          print("FIXTURE-CLEANUP: invalid")
          yield
          print("OOPS: Too many yields used")

      def before_tag(context, tag):
          if tag == "fixture.invalid":
              use_fixture(invalid_fixture, context)
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
      1 scenario passed, 1 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: invalid
        Scenario: Use invalid fixture
          Given a step passes ... passed
      FIXTURE-CLEANUP: invalid
      CLEANUP-ERROR in cleanup_fixture: InvalidFixtureError: Has more than one yield: <function invalid_fixture at
      """
    But note that "cleanup errors cause scenario to fail (by default)"


  Scenario: Fixture with cleanup-error causes failed (case: scenario)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture
      def bad_with_cleanup_error(context):
          print("FIXTURE-SETUP: bad_with_cleanup_error")
          yield
          print("FIXTURE-CLEANUP: bad_with_cleanup_error")
          raise RuntimeError("BAD_FIXTURE_CLEANUP_ERROR")

      def before_tag(context, tag):
          if tag == "fixture.bad_with_cleanup_error":
              use_fixture(bad_with_cleanup_error, context)
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
      1 scenario passed, 1 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: bad_with_cleanup_error
        Scenario: Use fixture
          Given a step passes ... passed
      FIXTURE-CLEANUP: bad_with_cleanup_error
      CLEANUP-ERROR in cleanup_fixture: RuntimeError: BAD_FIXTURE_CLEANUP_ERROR
      """
    And the command output should contain:
      """
      File "features/environment.py", line 9, in bad_with_cleanup_error
        raise RuntimeError("BAD_FIXTURE_CLEANUP_ERROR")
      RuntimeError: BAD_FIXTURE_CLEANUP_ERROR
      """
    But note that "traceback shows cleanup-fixture failure location"
    And note that "cleanup error causes scenario to fail (by default)"


  Scenario: Multiple fixture cleanup-errors cause no abort after first error (case: scenario)
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.fixture import fixture, use_fixture

      @fixture
      def foo(context):
          print("FIXTURE-SETUP: foo")
          yield
          print("FIXTURE-CLEANUP: foo")

      @fixture
      def bad_with_cleanup_error(context, name):
          print("FIXTURE-SETUP: bad_with_cleanup_error%s" % name)
          yield
          print("FIXTURE-CLEANUP: bad_with_cleanup_error%s" % name)
          raise RuntimeError("BAD_FIXTURE_CLEANUP_ERROR%s" % name)

      def before_tag(context, tag):
          if tag.startswith("fixture.bad_with_cleanup_error"):
              name = tag.replace("fixture.bad_with_cleanup_error", "")
              use_fixture(bad_with_cleanup_error, context, name)
          elif tag.startswith("fixture.foo"):
              use_fixture(foo, context)
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
      1 scenario passed, 1 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      FIXTURE-SETUP: bad_with_cleanup_error_1
      FIXTURE-SETUP: foo
      FIXTURE-SETUP: bad_with_cleanup_error_2
        Scenario: Use fixture
          Given a step passes ... passed
      FIXTURE-CLEANUP: bad_with_cleanup_error_2
      CLEANUP-ERROR in cleanup_fixture: RuntimeError: BAD_FIXTURE_CLEANUP_ERROR_2
      """
    And the command output should contain:
      """
      FIXTURE-CLEANUP: foo
      FIXTURE-CLEANUP: bad_with_cleanup_error_1
      CLEANUP-ERROR in cleanup_fixture: RuntimeError: BAD_FIXTURE_CLEANUP_ERROR_1
      """
    But note that "all fixture-cleanups are executed (even when errors occur)"
    And note that "fixture-cleanups are executed in reverse order (LIFO)"
