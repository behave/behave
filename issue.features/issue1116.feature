@issue
@user.failure
Feature: Issue #1116 -- behave erroring in pretty format in pyproject.toml

  . DESCRIPTION OF OBSERVED BEHAVIOR:
  .  * I am using a "pyproject.toml" with behave-configuration
  .  * I am using 'format = "pretty"' in the TOML config
  .  * When I run it with "behave", I get the following error message:
  .
  .      behave: error: BAD_FORMAT=p (problem: LookupError), r (problem: LookupError), ...
  .
  . PROBLEM ANALYSIS:
  .  * Config-param: format : sequence<string> = ${default_format}
  .  * Wrong type "string" was used for "format" config-param.
  .
  . PROBLEM RESOLUTION:
  .  * Works fine if the correct type is used.
  .  * BUT: Improve diagnostics if wrong type is used.

  Background: Setup
    Given a new working directory
    And a file named "features/steps/use_step_library.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/simple.feature" with:
      """
      Feature: F1
        Scenario: S1
          Given a step passes
          When another step passes
      """

  # @use.with_python.min_version="3.0"
  @use.with_python3=true
  Scenario: Use Problematic Config-File (case: Python 3.x)
    Given a file named "pyproject.toml" with:
      """
      [tool.behave]
      format = "pretty"
      """
    When I run "behave features/simple.feature"
    Then it should fail with:
      """
      ConfigParamTypeError: format = 'pretty' (expected: list<str>, was: str)
      """
    And the command output should not contain:
      """
      behave: error: BAD_FORMAT=p (problem: LookupError), r (problem: LookupError),
      """
    But note that "format config-param uses a string type (expected: list<string>)"


  # @not.with_python.min_version="3.0"
  @use.with_python2=true
  Scenario: Use Problematic Config-File (case: Python 2.7)
    Given a file named "pyproject.toml" with:
      """
      [tool.behave]
      format = "pretty"
      """
    When I run "behave features/simple.feature"
    Then it should fail with:
      """
      ConfigParamTypeError: format = u'pretty' (expected: list<unicode>, was: unicode)
      """
    And the command output should not contain:
      """
      behave: error: BAD_FORMAT=p (problem: LookupError), r (problem: LookupError),
      """
    But note that "format config-param uses a string type (expected: list<string>)"


  Scenario: Use Good Config-File
    Given a file named "pyproject.toml" with:
      """
      [tool.behave]
      format = ["pretty"]
      """
    When I run "behave features/simple.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature: F1 # features/simple.feature:1

        Scenario: S1               # features/simple.feature:2
          Given a step passes      # ../behave4cmd0/passing_steps.py:23
          When another step passes # ../behave4cmd0/passing_steps.py:23
      """
    But note that "the correct format config-param type was used now"
