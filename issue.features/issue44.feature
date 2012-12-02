@issue
Feature: Issue #44 Shell-like comments are removed in Multiline Args

  As I user
  I want that multiline arguments (docstrings) contents are preserved.

  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then
      from hamcrest import assert_that, equal_to

      @given(u'a multiline text argument with')
      def step(context):
          context.expected_text = context.text

      @then(u'the multiline text argument should be')
      def step(context):
          assert_that(context.text, equal_to(context.expected_text))
      """

  Scenario: Ensure shell comment lines are not filtered out in multiline text
    Given a file named "features/issue44_test.feature" with:
      '''
      Feature: Multiline text with shell comment lines
        Scenario:
          Given a multiline text argument with:
            """
            Lorem ipsum.
            # THIS IS A SHELL COMMENT.
            Ipsum lorem.
            """
          Then the multiline text argument should be:
            """
            Lorem ipsum.
            # THIS IS A SHELL COMMENT.
            Ipsum lorem.
            """
      '''
    When I run "behave -c -f pretty features/issue44_test.feature"
    Then it should pass
    And  the command output should contain:
        """
        # THIS IS A SHELL COMMENT.
        """
    But  the command output should not contain:
        """
        Lorem ipsum.
        Ipsum lorem.
        """
