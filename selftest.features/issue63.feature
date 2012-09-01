@issue
Feature: Issue #63: 'ScenarioOutline' object has no attribute 'stdout'

  The problem occurs when "behave --junit ..." is used
  And a feature contains one or more ScenarioOutline(s).

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      # -- OMIT: from __future__ import print_function
      from behave import given
      import sys

      def generate_output(step, outcome, name):
          # -- OMIT: print("{0}0 {1}: {2};".format(step, outcome, name))
          sys.stdout.write("{0}1 {1}: {2};\n".format(step, outcome, name))
          sys.stderr.write("{0}2 {1}: {2};\n".format(step, outcome, name))

      @given(u'a {outcome} step with "{name}"')
      def step(context, outcome, name):
          context.name = name
          generate_output("Given", outcome, name)
          assert outcome == "passing"

      @when(u'a {outcome} step with "{name}" occurs')
      def step(context, outcome, name):
          generate_output("When", outcome, name)
          assert outcome == "passing"

      @then(u'a {outcome} step with "{name}" is reached')
      def step(context, outcome, name):
          generate_output("Then", outcome, name)
          assert outcome == "passing"
          assert context.name == name
      """

  Scenario: ScenarioOutline with Passing Steps
    Given a file named "features/issue63_case1.feature" with:
      """
      Feature: ScenarioOutline with Passing Steps
        Scenario Outline:
          Given a passing step with "<name>"
          When  a passing step with "<name>" occurs
          Then  a passing step with "<name>" is reached

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c --junit features/issue63_case1.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    But the command output should not contain:
      """
      AttributeError: 'ScenarioOutline' object has no attribute 'stdout'
      """

  Scenario: ScenarioOutline with Passing and Failing Steps
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
      AttributeError: 'ScenarioOutline' object has no attribute 'stdout'
      """
    And the command output should not contain:
      """
      AttributeError: 'Scenario' object has no attribute 'exception'
      """
    And the command output should contain:
      """
      Captured stdout:
      Given1 passing: Alice;
      When1 failing: Alice;
      """
    And the command output should contain:
      """
      Captured stderr:
      Given2 passing: Alice;
      When2 failing: Alice;
      """
