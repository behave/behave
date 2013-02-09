@issue
Feature: Issue #69: JUnitReporter: Fault when processing ScenarioOutlines with failing steps

  The problem occurs when "behave --junit ..." is used
  And a feature contains one or more ScenarioOutline(s) with failing steps.

  The JUnitReport does not process ScenarioOutline correctly (logic-error).
  Therefore, Scenarios of a ScenarioOutline are processes as Scenario steps.
  This causes problems when the step.status is "failed".

  RELATED:
    * issue #63

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given

      @given(u'a {outcome} step with "{name}"')
      def step(context, outcome, name):
          context.name = name
          assert outcome == "passing"

      @when(u'a {outcome} step with "{name}" occurs')
      def step(context, outcome, name):
          assert outcome == "passing"
          assert context.name == name

      @then(u'a {outcome} step with "{name}" is reached')
      def step(context, outcome, name):
          assert outcome == "passing"
          assert context.name == name
      """

  Scenario: ScenarioOutline with Failing Steps
    Given a file named "features/issue63_case2.feature" with:
      """
      Feature: ScenarioOutline with Passing and Failing Steps
        Scenario Outline:
          Given a passing step with "<name>"
          When  a failing step with "<name>" occurs
          Then  a passing step with "<name>" is reached

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c --junit features/issue63_case2.feature"
    Then it should fail with:
      """
      0 scenarios passed, 2 failed, 0 skipped
      2 steps passed, 2 failed, 2 skipped, 0 undefined
      """
    But the command output should not contain:
      """
      AttributeError: 'Scenario' object has no attribute 'exception'
      """
    And the command output should not contain:
      """
      behave/reporter/junit.py
      """

