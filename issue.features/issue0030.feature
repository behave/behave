@issue
Feature: Issue #30 "behave --version" runs features and shows no version

  Scenario: Ensure environment assumptions are correct (Sanity Check)
    Given a new working directory
    When I run "behave"
    Then it should fail
    And the command output should contain:
      """
      No steps directory in '{__WORKDIR__}/features'
      """

  Scenario: Ensure --version option is processed correctly
    Given a new working directory
    When I run "behave --version"
    Then it should pass
    And the command output should not contain:
      """
      No steps directory in '{__WORKDIR__}/features'
      """

