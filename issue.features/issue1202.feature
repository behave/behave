@issue
Feature: Issue #1202 -- pyproject.toml that does not contain any [tool] sections

  . DESCRIPTION:
  .   * "behave" fails if "pyproject.toml" file exists without any "[tool]" section
  .   * DISCOVERED WITH: behave v1.2.7.dev6
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1202


  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
      """
      from __future__ import absolute_import
      import behave4cmd0.passing_steps
      """
    And a file named "features/example.feature" with:
      """
      Feature: Example
        Scenario: E1
          Given a step passes
          When another step passes
      """


  Scenario: pyproject.toml without any [tool] section
    Given an empty file named "pyproject.toml"
    When I run `behave -f plain features/example.feature`
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    But the command output should not contain "KeyError: 'tool'"
    And the command output should not contain:
      """
      File "{__CWD__}/behave/configuration.py", line 593, in read_toml_config
        config_tool = config["tool"]
      """
    And note that "behave gracefully ignores the invalid pyproject.toml file"


  Scenario: pyproject.toml with other [tool] section
    Given a file named "pyproject.toml" with:
      """
      [tool.foo]
      one = 1
      """
    When I run `behave -f plain features/example.feature`
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    But the command output should not contain "KeyError: 'tool'"
    And note that "behave skips the pyproject.toml file without relevant information"
