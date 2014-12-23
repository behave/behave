@issue
Feature: Issue #41 Missing Steps are duplicated in a Scenario Outline

  As I user
  I want that missing steps are reported only once.

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'I enter a "{name}"')
      def step(context, name):
          context.name = name

      @when(u'I enter a "{name}"')
      def step(context, name):
          context.name = name

      @then(u'the name is "{name}"')
      def step(context, name):
          assert context.name == name
      """

  Scenario: Missing Given Step
    Given a file named "features/issue41_missing1.feature" with:
      """
      Feature: Missing Given-Step in a Scenario Outline
        Scenario Outline:
          Given an unknown step
          When  I enter a "<name>"
          Then  the name is "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue41_missing1.feature"
    Then it should fail with:
      """
      0 steps passed, 0 failed, 4 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @given(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given an unknown step')
      """
    But the command output should not contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @given(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given an unknown step')
      @given(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given an unknown step')
      """

  Scenario: Missing When Step
    Given a file named "features/issue41_missing2.feature" with:
      """
      Feature: Missing When-Step in a Scenario Outline
        Scenario Outline:
          Given I enter a "<name>"
          When  I use an unknown step
          Then  the name is "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue41_missing2.feature"
    Then it should fail with:
      """
      2 steps passed, 0 failed, 2 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @when(u'I use an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When I use an unknown step')
      """
    But the command output should not contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @when(u'I use an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When I use an unknown step')
      @when(u'I use an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When I use an unknown step')
      """

  Scenario: Missing Then Step
    Given a file named "features/issue41_missing3.feature" with:
      """
      Feature: Missing Then-Step in a Scenario Outline
        Scenario Outline:
          Given I enter a "<name>"
          When  I enter a "<name>"
          Then  I use an unknown step

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -c -f plain features/issue41_missing3.feature"
    Then it should fail with:
      """
      4 steps passed, 0 failed, 0 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @then(u'I use an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Then I use an unknown step')
      """
    But the command output should not contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @then(u'I use an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Then I use an unknown step')
      @then(u'I use an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Then I use an unknown step')
      """
