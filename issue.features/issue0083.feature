@issue
Feature: Issue #83: behave.__main__:main() Various sys.exit issues

  . Currently, the main function has several issues related
  . to sys.exit() returncode usage:
  .
  . 1. sys.exit("string") is invalid, a number must be used:
  .    => Used in exception cases after run (ParseError, ConfigError)
  .
  . 2. On success, the main() function returns implicitly None
  .    instead of using sys.exit(0)
  .    => No statement at end of function after failed case.

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step(u'a step passes')
        def step_passes(context):
            pass
        """

  Scenario: Successful test run
    Given a file named "features/passing.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When  a step passes
            Then  a step passes
        """
    When I run "behave -c features/passing.feature"
    Then it should pass
    And  the command returncode is "0"

  Scenario: ParseError occurs
    Given a file named "features/invalid_with_ParseError.feature" with:
        """
        Feature:
          Scenario: Invalid scenario which raises ParseError
            Given a step passes
            When2 a step passes
        """
    When I run "behave -c features/invalid_with_ParseError.feature"
    Then it should fail
    And  the command returncode is non-zero
    And  the command output should contain:
        """
        Failed to parse "{__WORKDIR__}/features/invalid_with_ParseError.feature"
        """

  Scenario: ConfigError occurs
    Given a new working directory
    And   a file named "features/passing2.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
        """
    When I run "behave -c features/passing2.feature"
    Then it should fail
    And  the command returncode is non-zero
    And  the command output should contain:
        """
        No steps directory in '{__WORKDIR__}/features'
        """
