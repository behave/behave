@issue
Feature: Issue #1068 -- Feature.status is Status.failed in before_scenario() Hook

  . DESCRIPTION OF OBSERVED BEHAVIOR:
  .  Current feature status computation makes only sense after all scenarios are executed.
  .  Each scenario.status is initially in "Status.untested" before the test run.
  .  If a hook implementation decides to call "context.abort()" during the test run,
  .  several scenarios of a feature may still be untested.
  .
  .  Therefore, the feature status computation currently counts
  .  an untested scenario as failed if one or more scenarios have passed or failed.

  Background: Setup
    Given a new working directory
    And a file named "features/steps/use_step_library.py" with:
      """
      from behave import then

      @then(u'{num1:d} is greater than {num2:d}')
      def step_impl(context, num1, num2):
          assert num1 > num2, "FAILED: num1=%s, num2=%s" % (num1, num2)
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """

  Scenario: Verify observed behaviour
    Given a file named "features/syndrome_1068_1.feature" with:
      """
      Feature: F1
        Scenario: Test case 1.1
          Then 5 is greater than 4

        Scenario: Test case 1.2
          Then 2 is greater than 1

        Scenario: Test case 1.3
          Then 3 is greater than 2
      """
    And a file named "features/environment.py" with:
      """
      from __future__ import print_function

      def before_scenario(context, scenario):
          print("BEFORE_SCENARIO: Feature status is: {0} (scenario: {1})".format(
              context.feature.status, scenario.name))
      """
    When I run "behave -f plain features/syndrome_1068_1.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      3 scenarios passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      BEFORE_SCENARIO: Feature status is: Status.untested (scenario: Test case 1.1)
      """
    And the command output should contain:
      """
      BEFORE_SCENARIO: Feature status is: Status.failed (scenario: Test case 1.2)
      """
    And the command output should contain:
      """
      BEFORE_SCENARIO: Feature status is: Status.failed (scenario: Test case 1.3)
      """
    But note that "the feature.status is failed iff some scenarios are passed and others untested"


  Scenario: Proof-of-Concept for Desired Functionality
    Given a file named "features/syndrome_1068_2.feature" with:
      """
      Feature: F2
        Scenario: Test case 2.1
          Then 5 is greater than 4

        Scenario: Test case 2.2 (expected to fail)
          Then 1 is greater than 3

        Scenario: Test case 2.3
          Then 3 is greater than 2

        Scenario: Test case 2.4
          Then 3 is greater than 1
      """
    And a file named "features/environment.py" with:
      """
      from __future__ import print_function
      from behave.model_core import Status

      def after_scenario(context, scenario):
          if scenario.status == Status.failed:
              print("AFTER_FAILED_SCENARIO: %s" % scenario.name)
              skip_remaining_feature_scenarios(context.feature)

      def skip_remaining_feature_scenarios(feature):
          for scenario in feature.iter_scenarios():
              if scenario.status == Status.untested:
                  print("SKIP-SCENARIO: %s" % scenario.name)
                  scenario.skip()
      """
    When I run "behave -f plain features/syndrome_1068_2.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 2 skipped
      """
    And the command output should contain:
      """
      AFTER_FAILED_SCENARIO: Test case 2.2 (expected to fail)
      SKIP-SCENARIO: Test case 2.3
      SKIP-SCENARIO: Test case 2.4
      """
