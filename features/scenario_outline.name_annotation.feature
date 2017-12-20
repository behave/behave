Feature: Scenario Outline -- Scenario Name Annotations

  As a behave user / test writer
  I want to know in the current example/row combination
  So that I know the context of success/failure within a test run (without details).

  . REQUIREMENTS:
  .   * generated scenario name should better indicate row/example combination.
  .   * name annotation schema for generated scenario names should be configurable.
  .
  . IMPROVEMENTS:
  .   * annotate Scenario Outline name (with row.id, examples.name, ...)
  .
  .
  . SCENARIO OUTLINE NAME ANNOTATION SCHEMA:
  .
  .   scenario_outline_annotation_schema = "{name} -- @{row.id} {examples.name}"
  .
  .   | Placeholder     | Description |
  .   |  name           |  Name of the Scenario Outline.                 |
  .   |  examples.name  |  Name of the examples group (or empty string). |
  .   |  examples.index |  Index of examples group (range: 1..N).        |
  .   |  row.index      |  Index of row in examples group (range: 1..R). |
  .   |  row.id         |  Same as: "{example.index}.{row.index}"        |


  @setup
  Scenario: Test Setup
    Given a new working directory
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

  Scenario: Use default annotation schema for generated scenarios (name annotations)

    Each example/row combination should be easy to spot.

    Given a file named "behave.ini" does not exist
    When I run "behave -f plain --no-timings features/named_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Named Examples -- @1.1 Alice
        Given a param 10 ... passed

      Scenario Outline: Named Examples -- @1.2 Alice
        Given a param 42 ... passed

      Scenario Outline: Named Examples -- @2.1 Bob
        Given a param 43 ... passed
      """
    And note that "the default annotation schema is: {name} -- @{row.id} {examples.name}"
    When I run "behave -f plain --no-timings features/unnamed_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Unnamed Examples -- @1.1
        Given a param 100 ... passed

      Scenario Outline: Unnamed Examples -- @1.2
        Given a param 101 ... passed
      """
    But note that "each generated scenario name has a unique <row.id> annotation"
    And note that "each generated scenario name contains has its <examples.name> as annotation"


  Scenario: Use own annotation schema for generated scenarios (name annotations)
    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -*- {examples.name} @{row.id}
      """
    When I run "behave -f plain --no-timings features/named_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Named Examples -*- Alice @1.1
        Given a param 10 ... passed

      Scenario Outline: Named Examples -*- Alice @1.2
        Given a param 42 ... passed

      Scenario Outline: Named Examples -*- Bob @2.1
        Given a param 43 ... passed
      """
    When I run "behave -f plain --no-timings features/unnamed_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Unnamed Examples -*-  @1.1
        Given a param 100 ... passed

      Scenario Outline: Unnamed Examples -*-  @1.2
        Given a param 101 ... passed
      """


  Scenario: Disable name annotations (use: old naming scheme)
    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name}
      """
    When I run "behave -f plain --no-timings features/named_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Named Examples
        Given a param 10 ... passed

      Scenario Outline: Named Examples
        Given a param 42 ... passed

      Scenario Outline: Named Examples
        Given a param 43 ... passed
      """
    When I run "behave -f plain --no-timings features/unnamed_examples.feature"
    Then it should pass with:
      """
      Scenario Outline: Unnamed Examples
        Given a param 100 ... passed

      Scenario Outline: Unnamed Examples
        Given a param 101 ... passed
      """
