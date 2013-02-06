@issue
Feature: Issue #32 "behave --junit-directory=xxx" fails if more than 1 level must be created

  Scenario:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'passing')
      def step(context):
          pass
      """
    And a file named "features/issue32_1.feature" with:
      """
      Feature: One
        Scenario: One
            Given passing
      """

    When I run "behave --junit --junit-directory=report/test_results"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      """
    And the directory "report/test_results" should exist
