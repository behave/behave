Feature: Scenario Outline -- Improvements

  As a behave user / test writer
  I want that Scenario Outline (as paramtrized Scenario) is improved
  So that I know better which example/row combination is run.

  . REQUIREMENTS:
  .   * Generated scenario name should better indicate row/example combination.
  .   * Naming schema for generated scenario names should be configurable.
  .   * File location of generated scenario should represent row/example.
  .   * It should be possible select all scenarios of an examples group.
  .
  . IMPROVEMENTS:
  .   * annotate Scenario Outline name (with row.id, examples.name, ...)
  .   * use placeholders (from row/example) in Scenario Outline tags.
  .   * use placeholders (from row/example) in Scenario Outline name.
  .   * use placeholders (from row/example) in Examples (group) name.
  .   * file location for generated scenario is unique (selectable in rerun)
  .
  . SPECIFICATION: Special placeholders
  .
  .   | Placeholder     | Description |
  .   |  name           |  Name of the Scenario Outline.                 |
  .   |  examples.name  |  Name of the examples group (or empty string). |
  .   |  examples.index |  Index of examples group (range: 1..N).        |
  .   |  row.index      |  Index of row in examples group (range: 1..R). |
  .   |  row.id         |  Same as: "{example.index}.{row.index}"        |
  .
  . RELATED:
  .   * scenario_outline.name_annotation.feature
  .   * scenario_outline.parametrized.feature

  @setup
  Scenario: Test Setup
    Given a new working directory
    And a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -- @{row.id} {examples.name}
      show_timings = false
      show_skipped = false
      """
    And a file named "features/named_examples.feature" with:
      """
      Feature:
        Scenario Outline: Named Examples
          Given a param <param1>

          Examples: Alice
            | param1 |
            |   10   |
            |   42   |

          Examples: Bob
            | param1 |
            |   43   |
      """
    And a file named "features/unnamed_examples.feature" with:
      """
      Feature:
        Scenario Outline: Unnamed Examples
          Given a param <param1>

          Examples:
            | param1 |
            |   100  |
            |   101  |
      """
    And a file named "features/steps/param_steps.py" with:
      """
      from behave import step

      @step('a param {value:w}')
      def step_impl_with_param(context, value):
          context.param = value

      @step('a param {name}={value}')
      def step_impl_with_param_value(context, name, value):
          context.param_name = name
          context.param_value = value
      """

  Scenario: Unique File Locations in generated scenarios
    When I run "behave -f pretty -c features/named_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Named Examples -- @1.1 Alice  # features/named_examples.feature:7
        Given a param 10                              # features/steps/param_steps.py:3

      Scenario Outline: Named Examples -- @1.2 Alice  # features/named_examples.feature:8
        Given a param 42                              # features/steps/param_steps.py:3

      Scenario Outline: Named Examples -- @2.1 Bob  # features/named_examples.feature:12
        Given a param 43                            # features/steps/param_steps.py:3
      """
    But note that "each generated scenario has unique file location (related to row.line)"


  Scenario: Select generated scenario by unique File Location
    When I run "behave -f plain features/named_examples.feature:8"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 2 skipped
      1 step passed, 0 failed, 2 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scenario Outline: Named Examples -- @1.2 Alice
        Given a param 42 ... passed
      """

  @xfail
  Scenario: Select all generated scenarios of a Scenario Outline by File Location
    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -- @{row.id} {examples.name}
      """
    When I run "behave -f plain features/named_examples.feature:2"
    Then it should pass with:
      """
      3 scenarios passed, 0 failed, 0 skipped
      3 step passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scenario Outline: Named Examples -- @1.2 Alice
        Given a param 42 ... passed
      """

  @select.examples.by_name
  Scenario: Select Examples (Group) by Name (Case: name part)
    When I run "behave --name=Alice -f plain features/named_examples.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 1 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scenario Outline: Named Examples -- @1.1 Alice
        Given a param 10 ... passed

      Scenario Outline: Named Examples -- @1.2 Alice
        Given a param 42 ... passed
      """

  @select.examples.by_name
  Scenario: Select Examples (Group) by Name (Case: regular expression)
    When I run "behave --name='-- @.* Alice' -f plain features/named_examples.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 1 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scenario Outline: Named Examples -- @1.1 Alice
        Given a param 10 ... passed

      Scenario Outline: Named Examples -- @1.2 Alice
        Given a param 42 ... passed
      """

  @select.examples.by_name
  Scenario: Select one Example by Name
    When I run "behave --name='-- @1.2 Alice' -f plain features/named_examples.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 2 skipped
      1 step passed, 0 failed, 2 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Scenario Outline: Named Examples -- @1.2 Alice
        Given a param 42 ... passed
      """
