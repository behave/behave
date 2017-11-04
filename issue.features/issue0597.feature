@issue
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
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      """

  Scenario: Passing w/o Encoding-Hint in Steps File (case: py2, py3)
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

  @only.with_python2=true
  Scenario: Failing w/o Encoding-Hint in Steps File (case: python2)
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
    And the command output should contain:
      """
      You can implement step definitions for undefined steps with these snippets:

      @given(u'allé')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given allé')
      """
    But note that "python2 uses encoding=ascii"
    And note that "encoding-hint in steps file solves the problem"


  @not.with_python2=true
  Scenario: Passing w/o Encoding-Hint in Steps File (case: python3)
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
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scénario: A1
        Soit allé ... passed
      """
    And the command output should not contain:
      """
      @given(u'allé')
      def step_impl(context):
          raise NotImplementedError(u'STEP: Given allé')
      """
    But note that "python3 discovers encoding (or uses encoding=UTF-8)"
