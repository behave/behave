@issue
Feature: Issue #172 Junit report file name populated incorrectly when running against a feature file

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
    And a file named "features/feature_in_root_folder.feature" with:
      """
      Feature:
        Scenario:
          Given a step passes
      """
    And a file named "features/subfolder/feature_in_subfolder.feature" with:
      """
      Feature:
        Scenario:
          Given a step passes
      """

  Scenario: Running behave for one feature in root folder
    When I run "behave --junit --junit-directory=test_results features/feature_in_root_folder.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      """
    And a file named "test_results/TESTS-feature_in_root_folder.xml" exists

  Scenario: Running behave for one feature in a subfolder
    When I run "behave --junit --junit-directory=test_results features/subfolder/feature_in_subfolder.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      """
    And a file named "test_results/TESTS-subfolder.feature_in_subfolder.xml" exists

  Scenario: Running behave for all features
    When I run "behave --junit --junit-directory=test_results"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      """
    And a file named "test_results/TESTS-feature_in_root_folder.xml" exists
    And a file named "test_results/TESTS-subfolder.feature_in_subfolder.xml" exists
