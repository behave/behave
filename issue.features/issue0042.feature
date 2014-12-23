@issue
Feature: Issue #42 Nice to have snippets for all unimplemented steps taking into account of the tags fltering

  As a user
  I want that all undefined steps are reported,
  not only just the first one in a scenario.

  In addition, all known steps after the first undefined step in a scenario
  should be marked as skipped (even failing ones).


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

  Scenario: One undefined step in a scenario
    Given a file named "features/issue42_missing1.feature" with:
      """
      Feature: Missing Given-Step in a Scenario
        Scenario:
          Given an unknown step
          When  I enter a "Alice"
          Then  the name is "Alice"
      """
    When I run "behave -f plain features/issue42_missing1.feature"
    Then it should fail with:
      """
      0 steps passed, 0 failed, 2 skipped, 1 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @given(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given an unknown step')
      """

  Scenario: Two undefined steps in a scenario
    Given a file named "features/issue42_missing2.feature" with:
      """
      Feature: Missing Given and When steps in a Scenario
        Scenario:
          Given an unknown step
          When  another unknown step
           And  I enter a "Alice"
          Then  the name is "Alice"
      """
    When I run "behave -f plain features/issue42_missing2.feature"
    Then it should fail with:
      """
      0 steps passed, 0 failed, 2 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @given(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given an unknown step')

      @when(u'another unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When another unknown step')
      """

  Scenario: Two undefined steps in the middle with passing steps
    Given a file named "features/issue42_missing3.feature" with:
      """
      Feature: Missing 2 When steps after passing step
        Scenario:
          When I enter a "Alice"
          And  an unknown step
          And  another unknown step
          Then the name is "Alice"
      """
    When I run "behave -f plain features/issue42_missing3.feature"
    Then it should fail with:
      """
      1 step passed, 0 failed, 1 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @when(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When an unknown step')

      @when(u'another unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When another unknown step')
      """

  Scenario: Undefined steps are detected if they occur after a failing step
    Given a file named "features/issue42_missing4.feature" with:
      """
      Feature: Missing 2 When steps after passing step
        Scenario:
          When I enter a "Alice"
          Then the name is "Bob"
          And  an unknown step
          And  another unknown step
      """
    When I run "behave -f plain features/issue42_missing4.feature"
    Then it should fail with:
      """
      1 step passed, 1 failed, 0 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @then(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Then an unknown step')

      @then(u'another unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Then another unknown step')
      """

  Scenario: Failing step after first undefined step should be marked as skipped
    Given a file named "features/issue42_missing4.feature" with:
      """
      Feature: Missing 2 When steps after passing step
        Scenario:
          When I enter a "Alice"
          And  an unknown step
          Then the name is "Bob"
          And  another unknown step
      """
    When I run "behave -f plain features/issue42_missing4.feature"
    Then it should fail with:
      """
      1 step passed, 0 failed, 1 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @when(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When an unknown step')

      @then(u'another unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Then another unknown step')
      """

  Scenario: Two undefined steps in scenario outline
    Given a file named "features/issue42_missing5.feature" with:
      """
      Feature: Missing Given and When Step in a Scenario Outline
        Scenario Outline:
          Given an unknown step
          When  another unknown step
           And  I enter a "<name>"
          Then  the name is "<name>"

        Examples:
            |name |
            |Alice|
            |Bob  |
      """
    When I run "behave -f plain features/issue42_missing5.feature"
    Then it should fail with:
      """
      0 steps passed, 0 failed, 4 skipped, 4 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @given(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given an unknown step')

      @when(u'another unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When another unknown step')
      """

  Scenario: Two undefined steps and run with tags
    Given a file named "features/issue42_missing6.feature" with:
      """
      Feature: Missing steps in tagged scenarios
        @tag1
        Scenario:
          When I enter a "Alice"
          And  an unknown step
          Then the name is "Bob"

        @tag1
        Scenario:
          When I enter a "Alice"
          And  another unknown step
          Then the name is "Bob"

        @another_tag
        Scenario:
          When  I enter a "Alice"
          And   yet another unknown step
          Then  the name is "Bob"
      """
    When I run "behave -f plain --tags tag1 features/issue42_missing6.feature"
    Then it should fail with:
      """
      2 steps passed, 0 failed, 5 skipped, 2 undefined
      """
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:
      @when(u'an unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When an unknown step')

      @when(u'another unknown step')
      def step_impl(context):
          raise NotImplementedError(u'STEP: When another unknown step')
      """
