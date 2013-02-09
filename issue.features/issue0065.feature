@issue
Feature: Issue #65  Unrecognized --tag-help argument

  The "behave --help" output refers to the option "--tag-help"
  in the description of the "--tags" option.
  The correct option for more help on tags is "--tags-help".

  Scenario: Ensure environment assumptions are correct (Sanity Check)
    Given a new working directory
    When I run "behave --help"
    Then the command output should contain:
      """
      --tags-help
      """
    But  the command output should not contain:
      """
      --tag-help
      """
