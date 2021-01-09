Feature: Ensure that all examples are usable

  Scenario Outline: Use <example_dir>
    Given I use the directory "<example_dir>" as working directory
    When I run "behave <behave_cmdline>"
    Then it should <outcome>

    Examples:
      | example_dir         | behave_cmdline        | outcome |
      | examples/env_vars   | features/             | pass    |
      | examples/fixture.no_background | features/  | pass    |
      | examples/gherkin_v6 | features/             | pass    |


  Scenario: examples/gherkin_v6 -- @xfail parts
    Given I use the directory "examples/gherkin_v6" as working directory
    When I run "behave --tags=fail features/"
    Then it should fail with:
      """
      0 features passed, 1 failed, 2 skipped
      0 rules passed, 1 failed, 6 skipped
      1 scenario passed, 2 failed, 12 skipped
      2 steps passed, 2 failed, 39 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Failing scenarios:
        features/rule_fails.feature:7  F0 -- Fails
        features/rule_fails.feature:16  F2 -- Fails
      """

  @use.with_python_has_coroutine=true
  Scenario: examples/async_step (requires: python.version >= 3.4)
    Given I use the directory "examples/async_step" as working directory
    When I run "behave features/"
    Then it should pass
