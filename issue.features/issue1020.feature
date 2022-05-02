@issue
@mistaken
Feature: Issue #1020 -- Switch Step-Matcher in Step Definition File

  Ensure that you can redefine the Step-Matcher in a step definition file.
  SEE: https://github.com/behave/behave/issues/1020

  Scenario: Use steps with regex-matcher
    Given a new working directory
    And a file named "features/example_1020.feature" with:
      """
      Feature:
        Scenario: Alice
          When I meet with "Alice"
          Then I have a lot of fun with "Alice"

        Scenario: Bob
          When I meet with "Bob"
          Then I have a lot of fun with "Bob"
      """
    And a file named "features/steps/steps.py" with:
      """
      # -- FILE: features/steps/step.py
      from behave import given, when, use_step_matcher
      from hamcrest import assert_that, equal_to

      use_step_matcher("re")

      @when(u'I meet with "(?P<person>Alice|Bob)"')
      def step_when_I_meet(context, person):
          context.person = person

      use_step_matcher("parse")

      @then(u'I have a lot of fun with "{person}"')
      def step_then_I_have_fun_with(context, person):
          assert_that(person, equal_to(context.person))
      """

    When I run "behave -f plain features/example_1020.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain "0 undefined"
