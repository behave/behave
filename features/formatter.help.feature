Feature: Help Formatter

  As a tester
  I want to know which formatter are supported
  To be able to select one.

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
        progress       Shows dotted progress for each executed scenario.
        progress2      Shows dotted progress for each executed step.
        rerun          Emits scenario file locations of failing scenarios
        steps          Shows step definitions (step implementations).
        steps.doc      Shows documentation for step definitions.
        steps.usage    Shows how step definitions are used by steps.
        tags           Shows tags (and how often they are used).
        tags.location  Shows tags and the location where they are used.
      """
