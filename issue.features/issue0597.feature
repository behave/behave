@issue
@mistaken
@wip
Feature:
Feature: Issue #597 -- Steps with accented letters doesn't seem to work


  Background:
    Given a new working directory
    And a file named "features/french.feature" with:
      """
      # language: fr
      Fonctionnalité: Alice

        Scénario: A1
          Soit allé
          Quand comment
          Alors cava
      """

  Scenario: Working Example
    Given a file named "features/steps/french_steps.py" with:
      """
      # -*- coding: UTF-8 -*-
      from behave import given, when, then

      @given(u'allé')
      def given_step_alle(ctx):
          pass

      @when(u'comment')
      def when_step_comment(ctx):
          pass

      @then(u'cava')
      def then_step_cava(ctx):
          pass
      """
    When  I run "behave -f plain features/"
    Then it should pass with:
      """
      Fonctionnalité: Alice

        Scénario: A1
          Soit allé ... passed
          Quand comment ... passed
          Alors cava ... passed

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Failing Example when no Encoding-Hint is provided in Steps File
    Given a file named "features/steps/french_steps.py" with:
      """
      from behave import given, when, then

      @given(u'allé')
      def given_step_alle(ctx):
          pass

      @when(u'comment')
      def when_step_comment(ctx):
          pass

      @then(u'cava')
      def then_step_cava(ctx):
          pass
      """
    When  I run "behave -f plain features/"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 0 failed, 2 skipped, 1 undefined
      """
    And the command output should contain:
      """
      Scénario: A1
        Soit allé ... undefined
      """
    But note that "encoding hint in steps file solves the problem"
