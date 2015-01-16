@issue
Feature: Issue #280: AmbiguousStep error with similar step definitions and use_step_matcher("re")

  Having two steps with definitions starting with the same string causes an AmbiguousStep error to be thrown:
  |behave.step_registry.AmbiguousStep: @when('I add a (?<name>\w+) to it and an exclamation mark') has already
  |been defined in existing step @when('I add a (?<name>\w+) to it') at features\steps\steps.py:10
  To fix if a regular expression delimiters (^ and $) should be added to the RegexMatcher


  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then, use_step_matcher
      from hamcrest import assert_that, equal_to, is_not, is_, none

      use_step_matcher("re")

      @given(u'a simple word')
      def step(context):
          context.simple_word = "hi"

      @when(u'I add (?P<name>\w+) to it')
      def step(context, name):
          context.result = ''.join([context.simple_word, " ", name])

      @when(u'I add (?P<name>\w+) to it twice')
      def step(context, name):
          context.result = ''.join([context.simple_word, " ", name, name])

      @then(u'it is a (?P<greeting>hi\s\w+)')
      def step(context, greeting):
          assert_that(context.result, equal_to(greeting))
      """

  Scenario: Ensure AmbiguousStep error is not thrown
    Given a file named "features/issue280.feature" with:
      """
      Feature:
        Scenario Outline:
          Given a simple word
          When I add <name> to it
          Then it is a <greeting>

          Examples:
          | name    | greeting  |
          | Alice   | hi Alice  |

        Scenario Outline:
          Given a simple word
          When I add <name> to it twice
          Then it is a <greeting>

          Examples:
          | name    | greeting      |
          | Alice   | hi AliceAlice |
      """
    When I run "behave -f plain features/issue280.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped, 0 undefined
      """
