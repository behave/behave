@issue
Feature: Issue #330 Skipped scenarios are included in junit reports when -k is specified

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('a step passes')
      def step_passes(context):
          pass
      """
    And a file named "features/feature_matched.feature" with:
      """
      @tag1
      Feature:
        Scenario:
          Given a step passes
      """
    And a file named "features/feature_not_matched.feature" with:
      """
      Feature:
        Scenario:
          Given a step passes
      """

  Scenario: Junit report is not created with --no-skipped
    When I run "behave --junit --junit-directory=test_results -t tag1 --no-skipped"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 1 skipped
      """
    And a file named "test_results/TESTS-feature_matched.xml" exists
    And a file named "test_results/TESTS-feature_not_matched.xml" exists
    And the file "test_results/TESTS-feature_not_matched.xml" should contain
    """
    <testsuite errors="0" failures="0" name="feature_not_matched.feature_not_matched" skipped="0" tests="1" time="0.0" />
    """

  Scenario: Junit report is created with default options
    When I run "behave --junit --junit-directory=test_results -t tag1"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 1 skipped
      """
    And a file named "test_results/TESTS-feature_matched.xml" exists
    And a file named "test_results/TESTS-feature_not_matched.xml" exists
    And the file "test_results/TESTS-feature_not_matched.xml" should contain
    """
     <testsuite errors="0" failures="0" name="feature_not_matched.feature_not_matched" skipped="1" tests="1" time="0.0">
    """
