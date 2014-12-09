@issue
Feature: Issue #66: context.text and context.table are not cleared

  I noticed that context.table and context.text survive after the step is finished.


  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then
      from hamcrest import assert_that, equal_to, is_not, is_, none
      import six

      @given(u'a step with multiline text')
      def step(context):
          assert context.text is not None
          assert context.text, "Ensure non-empty"
          assert isinstance(context.text, six.string_types)

      @given(u'a step with a table')
      def step(context):
          assert context.table is not None

      @when(u'I check the "context.{name}" attribute')
      def step(context, name):
          context.name  = name
          context.value = getattr(context, name, None)

      @then(u'its value is None')
      def step(context):
          assert_that(context.value, is_(none()))

      @then(u'its value is "{value}"')
      def step(context, value):
          assert_that(context.value, equal_to(value))

      @then(u'its value is not "{value}"')
      def step(context, value):
          assert_that(value, is_not(equal_to(context.value)))
      """

  Scenario: Ensure multiline text data is cleared for next step
    Given a file named "features/issue66_case1.feature" with:
      """
      Feature:
        Scenario:
          Given a step with multiline text:
            '''
            Alice, Bob and Charly
            '''
          When I check the "context.text" attribute
          Then its value is not "Alice, Bob and Charly"
          But  its value is None
      """
    When I run "behave -f plain features/issue66_case1.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Ensure table data is cleared for next step
    Given a file named "features/issue66_case2.feature" with:
      """
      Feature:
        Scenario:
          Given a step with a table:
            | name  | gender |
            | Alice | female |
            | Bob   | male   |
          When I check the "context.table" attribute
          Then its value is None
      """
    When I run "behave -f plain features/issue66_case2.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
