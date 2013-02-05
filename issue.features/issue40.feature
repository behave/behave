@issue
Feature: Issue #40 Test Summary Scenario/Step Counts are incorrect for Scenario Outline

  As I user
  I want that each passed and each failed scenario is counted
  And I want that each passed and failed step in a ScenarioOutline is counted

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'a step {outcome} with "{name}"')
      def step(context, outcome, name):
          context.name = name
          assert outcome == "passes"

      @when(u'a step {outcome} with "{name}"')
      def step(context, outcome, name):
          assert outcome == "passes"
          assert context.name == name

      @then(u'a step {outcome} with "{name}"')
      def step(context, outcome, name):
          assert outcome == "passes"
          assert context.name == name
      """

  Scenario: ScenarioOutline with Passing Steps
    Given a file named "features/issue40_1.feature" with:
      """
      Feature: Verify Scenario/Step Summary Pass Count with ScenarioOutline
        Scenario Outline:
          Given a step passes with "<name>"
          When  a step passes with "<name>"
          Then  a step passes with "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue40_1.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: ScenarioOutline with Failing Given-Steps
    Given a file named "features/issue40_2G.feature" with:
      """
      Feature: Scenario/Step Summary Pass/Fail Count with ScenarioOutline
        Scenario Outline:
          Given a step fails with "<name>"
          When  a step passes with "<name>"
          Then  a step passes with "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue40_2G.feature"
    Then it should fail with:
      """
      0 scenarios passed, 2 failed, 0 skipped
      0 steps passed, 2 failed, 4 skipped, 0 undefined
      """

  Scenario: ScenarioOutline with Failing When-Steps
    Given a file named "features/issue40_2W.feature" with:
      """
      Feature: Scenario/Step Summary Pass/Fail Count with ScenarioOutline
        Scenario Outline:
          Given a step passes with "<name>"
          When  a step fails with "<name>"
          Then  a step passes with "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue40_2W.feature"
    Then it should fail with:
      """
      0 scenarios passed, 2 failed, 0 skipped
      2 steps passed, 2 failed, 2 skipped, 0 undefined
      """

  Scenario: ScenarioOutline with Failing Then-Steps
    Given a file named "features/issue40_2T.feature" with:
      """
      Feature: Scenario/Step Summary Pass/Fail Count with ScenarioOutline
        Scenario Outline:
          Given a step passes with "<name>"
          When  a step passes with "<name>"
          Then  a step fails with "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue40_2T.feature"
    Then it should fail with:
      """
      0 scenarios passed, 2 failed, 0 skipped
      4 steps passed, 2 failed, 0 skipped, 0 undefined
      """

  Scenario: ScenarioOutline with Mismatched When-Step Example Row
    Given a file named "features/issue40_3W.feature" with:
      """
      Feature: Scenario/Step Summary Pass/Fail Count with ScenarioOutline
        Scenario Outline:
          Given a step passes with "<name>"
          When  a step passes with "Alice"
          Then  a step passes with "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue40_3W.feature"
    Then it should fail with:
      """
      1 scenario passed, 1 failed, 0 skipped
      4 steps passed, 1 failed, 1 skipped, 0 undefined
      """

  Scenario: ScenarioOutline with Mismatched Then-Step Example Row
    Given a file named "features/issue40_3W.feature" with:
      """
      Feature: Scenario/Step Summary Pass/Fail Count with ScenarioOutline
        Scenario Outline:
          Given a step passes with "<name>"
          When  a step passes with "<name>"
          Then  a step passes with "Alice"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue40_3W.feature"
    Then it should fail with:
      """
      1 scenario passed, 1 failed, 0 skipped
      5 steps passed, 1 failed, 0 skipped, 0 undefined
      """
