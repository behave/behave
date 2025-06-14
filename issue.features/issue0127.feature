@issue
@deprecated
Feature: Issue #127: Strip trailing colons

  . CHANGED IN: behave v1.2.7.dev6
  .   * parser: Trailing colons are not stripped from steps in feature files
  .   * Use step with trailing colons in step-definitions
  . REASON: More natural (and fixes problem in PyCharm IDE).
  .
  . OLD DESCRIPTION STARTS HERE:
  .   Trailing colon in a step is stripped by the Gherkin parser.
  .   Undefined step snippets should not suggest the step with a trailing colon.
  .
  . DEPRECATED GENERAL RULE (by looking at the parser):
  .   1. Colon in step in feature file is OK
  .      (parser strips this for step-with-table or step-with-multiline-text).
  .   2. Step definitions in Python files should not end with a colon
  .      (used in @given/@when/@then decorators).


  Background:
    Given a new working directory
    And   a file named "features/example127.feature" with:
        """
        Feature:
          Scenario:
            Given the following superusers exist:
              | Name  | User Id |
              | Alice | 101     |
              | Bob   | 102     |
            And the following superusers exist
              | Name  | User Id |
              | Charly | 103    |
              | Doro   | 104    |
        """

  Scenario: Step Definition has no trailing colon (GOOD CASE)
    Given a file named "features/steps/good_steps.py" with:
        """
        from behave import given

        @given(u'the following superusers exist')
        @given(u'the following superusers exist:')
        def step_given_following_superusers_exist(context):
            pass
        """
    When I run "behave -f plain features/example127.feature"
    Then it should pass
    And the command output should not contain:
        """
        You can implement step definitions for undefined steps with these snippets:
        """
    And the command output should not contain:
        """
        @given(u'the following superusers exist:')
        def step_impl(context):
            raise StepNotImplementedError(u'Given the following superusers exist:')
        """
