@issue
Feature: Issue #177: Cannot setup logging_format

  | DESCPRIPTION:
  |   When the logging_format is set in the behave configuration file
  |   or on command-line, an exception is thrown, because
  |   the ConfigParser tries to replace the placeholders in the format string
  |   with option values in the configuration file (which do not exist).
  |
  | SOLUTION:
  |   The format string must be processed as raw value (by the ConfigParser).
  |
  | RELATED:
  |   * features/logging.setup_format.feature
  |   * features/logging.setup_level.feature


  @reuse.colocated_test
  Scenario: Setup logging_format
    Given I use the current directory as working directory
    When I run "behave -f plain features/logging.setup_format.feature"
    Then it should pass
    And the command output should not contain:
      """
      Traceback (most recent call last):
      """
    And the command output should not contain:
      """
      ConfigParser.InterpolationMissingOptionError: Bad value
      """

  @reuse.colocated_test
  Scenario: Setup logging_level

    Ensure that the problem that was also mentioned, works as expected.
    Note that this "problem" never existed (hint: missing user knowledge).

    Given I use the current directory as working directory
    When I run "behave -f plain features/logging.setup_level.feature"
    Then it should pass
