@issue
Feature: Issue #31 "behave --format help" raises an error

  Scenario:
    Given a new working directory
    When I run "behave --format=help"
    Then it should pass
    And the command output should contain:
      """
      Available formatters:
        json           JSON dump of test run
        json.pretty    JSON dump of test run (human readable)
        null           Provides formatter that does not output anything.
        plain          Very basic formatter with maximum compatibility
        pretty         Standard colourised pretty formatter
      """
