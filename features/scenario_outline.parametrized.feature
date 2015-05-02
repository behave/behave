Feature: Scenario Outline -- Parametrized Scenarios

  As a test writer
  I want to use the DRY principle when writing scenarios
  So that I am more productive and my work is less error-prone.
  
  . COMMENT:
  .   A Scenario Outline is basically a parametrized Scenario template.
  .   It is instantiated for each examples row with the corresponding data.
  .
  . SCENARIO GENERICS BASICS: What can be parametrized?
  .   * Scenario name:  Based on Scenario Outline with placeholders
  .   * Scenario steps: Step name with placeholders (including: step.text, step.table)
  .   * Scenario tags:  Based on Scenario Outline tags with placeholders
  .
  . CONSTRAINTS:
  .   * placeholders (names) for tags should not contain any whitespace.
  .   * a row data placeholder may override/hide a special placeholder (see below).
  .
  . SPECIAL PLACEHOLDERS:
  .   | Placeholder     | Description |
  .   |  examples.name  |  Name of the examples group (or empty string). |
  .   |  examples.index |  Index of examples group (range: 1..N).        |
  .   |  row.index      |  Index of row in examples group (range: 1..R). |
  .   |  row.id         |  Same as: "{example.index}.{row.index}"        |


  @setup
  Scenario: Test Setup
    Given a new working directory
    And a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -*- {examples.name}
      """
    And a file named "features/steps/param_steps.py" with:
      """
      from behave import step

      @step('a param {value:w}')
      def step_with_param(context, value):
          context.param = value

      @step('a param {name}={value}')
      def step_with_param_value(context, name, value):
          context.param_name = name
          context.param_value = value

      @step('a step with text')
      def step_with_param_value(context):
          assert context.text is not None, "REQUIRE: text"

      @step('a step with table')
      def step_with_param_value(context):
          assert context.table is not None, "REQUIRE: table"

      @step('an unknown param {name}={value}')
      def step_with_unknown_param_value(context, name, value):
          pass
      """

  @parametrize.name
  Scenario: Parametrized name in generated Scenarios (Case: Row Placeholders)
    Given a file named "features/use_name_with_row_params.feature" with:
      """
      Feature: SOP1
        Scenario Outline: Use placeholder <name>-<param1>
          Given a param param1=<param1>
          And a param name=<name>

          Examples: E-<ID>
            | ID  | name  | param1 |
            | 001 | Alice |  100  |
            | 002 | Bob   |  101  |
      """
    When I run "behave -f progress3 features/use_name_with_row_params.feature"
    Then it should pass with:
      """
      Use placeholder Alice-100 -*- E-001  ..
      Use placeholder Bob-101 -*- E-002  ..
      """

  @parametrize.name
  Scenario: Parametrized name in generated Scenarios (Case: Special Placeholders)
    Given a file named "features/use_name_with_special_params.feature" with:
      """
      Feature: SOP2
        Scenario Outline: Use placeholder S<examples.index>-<row.index> <examples.name>
          Given a param name=<name>
          And a param row.id=<row.id>

          Examples: E-<ID>/@<row.id>
            | ID  | name  | param1 |
            | 001 | Alice |  100  |
            | 002 | Bob   |  101  |
      """
    When I run "behave -f progress3 features/use_name_with_special_params.feature"
    Then it should pass with:
      """
      Use placeholder S1-1 E-001/@1.1 -*- E-001/@1.1  ..
      Use placeholder S1-2 E-002/@1.2 -*- E-002/@1.2  ..
      """

  @parametrize.steps
  Scenario: Use placeholders in generated scenario steps
    Given a file named "features/use_steps_with_params.feature" with:
      """
      Feature:
        Scenario Outline: Use row placeholders
          Given a param ID=<ID>
          And a param name=<name>
          And a param param1=<param1>

          Examples:
            | ID  | name  | param1 |
            | 001 | Alice |  101   |
            | 002 | Bob   |  102   |
      """
    When I run "behave -f plain --no-timings features/use_steps_with_params.feature"
    Then it should pass with:
      """
      Scenario Outline: Use row placeholders -*-
        Given a param ID=001 ... passed
        And a param name=Alice ... passed
        And a param param1=101 ... passed

      Scenario Outline: Use row placeholders -*-
        Given a param ID=002 ... passed
        And a param name=Bob ... passed
        And a param param1=102 ... passed
      """

  @parametrize.steps
  Scenario: Use an unknown placeholder in generated scenario steps
    Given a file named "features/use_steps_with_unknown_params.feature" with:
      """
      Feature:
        Scenario Outline: Use unknown placeholders
          Given an unknown param unknown=<unknown>

          Examples:
            | ID  | name  | param1 |
            | 001 | Alice |  100   |
      """
    When I run "behave -f plain --no-timings features/use_steps_with_unknown_params.feature"
    Then it should pass with:
      """
      Scenario Outline: Use unknown placeholders -*-
        Given an unknown param unknown=<unknown> ... passed
      """
    But note that "unknown placeholders are not replaced"


  @parametrize.steps
  Scenario: Use placeholders in generated scenario step.text
    Given a file named "features/use_steps_with_param_text.feature" with:
      '''
      Feature:
        Scenario Outline: Use parametrized step with text
          Given a step with text:
            """
            <greeting> <name>;
            Travel agency: <travel agency>
            """

          Examples:
            | ID  | name  | greeting | travel agency |
            | 001 | Alice |  Hello   | Pony express  |
      '''
    When I run "behave -f plain --no-timings features/use_steps_with_param_text.feature"
    Then it should pass with:
      '''
      Scenario Outline: Use parametrized step with text -*-
          Given a step with text ... passed
            """
            Hello Alice;
            Travel agency: Pony express
            """
      '''
    And note that "placeholders in step.text are replaced with row data"


  @parametrize.steps
  Scenario: Use placeholders in generated scenario step.table
    Given a file named "features/use_steps_with_param_table.feature" with:
      """
      Feature:
        Scenario Outline: Use parametrized step with table
          Given a step with table:
            | Id   | Name   | Travel Agency   | row id   |
            | <ID> | <name> | <travel agency> | <row.id> |

          Examples:
            | ID  | name  | greeting | travel agency |
            | 001 | Alice |  Hello   | Pony express  |
      """
    When I run "behave -f plain --no-timings features/use_steps_with_param_table.feature"
    Then it should pass with:
      """
      Scenario Outline: Use parametrized step with table -*-
        Given a step with table ... passed
          | Id  | Name  | Travel Agency | row id   |
          | 001 | Alice | Pony express  | <row.id> |
      """
    And note that "placeholders in step.table cells are replaced with row data"
    But note that "<row.id> is currently not supported in table cells (like other special placeholders)"


  @parametrize.steps
  Scenario: Use special placeholders in generated scenario steps
    Given a file named "features/use_steps_with_special_params.feature" with:
      """
      Feature:
        Scenario Outline: Use special placeholders @<row.id>
          Given a param name=<name>
          And a param examples.name=<examples.name>
          And a param examples.index=<examples.index>
          And a param row.index=<row.index>
          And a param row.id=<row.id>

          Examples: E-<ID>/@<row.id>
            | ID  | name  | param1 |
            | 001 | Alice |  100  |
            | 002 | Bob   |  101  |
      """
    When I run "behave -f plain --no-timings features/use_steps_with_special_params.feature"
    Then it should pass with:
      """
      Scenario Outline: Use special placeholders @1.1 -*- E-001/@1.1
          Given a param name=Alice ... passed
          And a param examples.name=E-001/@1.1 ... passed
          And a param examples.index=1 ... passed
          And a param row.index=1 ... passed
          And a param row.id=1.1 ... passed

      Scenario Outline: Use special placeholders @1.2 -*- E-002/@1.2
          Given a param name=Bob ... passed
          And a param examples.name=E-002/@1.2 ... passed
          And a param examples.index=1 ... passed
          And a param row.index=2 ... passed
          And a param row.id=1.2 ... passed
      """


  @parametrize.name
  @parametrize.steps
  Scenario: When special placeholder name is used for row data (Case: Override)

    Ensure that row data (placeholder) can override special placeholder (if needed).
    AFFECTED: scenario.name, examples.name, step.name

    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -*- special:row.id=@{row.id} {examples.name}
      """
    And a file named "features/use_name_with_overwritten_params.feature" with:
      """
      Feature: SOP3
        Scenario Outline: Use placeholder data:row.id=<row.id>
          Given a param name=<name>
          And a param row.id=<row.id>

          Examples: E-<ID>/<row.id>
            | ID  | name  | row.id |
            | 001 | Alice |  100  |
            | 002 | Bob   |  101  |
      """
    When I run "behave -f progress3 features/use_name_with_overwritten_params.feature"
    Then it should pass with:
      """
      Use placeholder data:row.id=100 -*- special:row.id=@1.1 E-001/100  ..
      Use placeholder data:row.id=101 -*- special:row.id=@1.2 E-002/101  ..
      """
    When I run "behave -f plain --no-timings features/use_name_with_overwritten_params.feature"
    Then it should pass with:
      """
      Scenario Outline: Use placeholder data:row.id=100 -*- special:row.id=@1.1 E-001/100
          Given a param name=Alice ... passed
          And a param row.id=100 ... passed

      Scenario Outline: Use placeholder data:row.id=101 -*- special:row.id=@1.2 E-002/101
          Given a param name=Bob ... passed
          And a param row.id=101 ... passed
      """
    But note that "a row data placeholder can override a special placeholder"
    And note that "the name annotation {row.id} still allows to refer to the special one"



  @parametrize.steps
  Scenario: Placeholder value has placeholder syntax (Case: recursion-check)

    Ensure that weird placeholder value cases are handled correctly.
    Ensure that no recursion occurs.

    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -*- @{row.id} {examples.name}
      """
    And a file named "features/use_value_with_placeholder_syntax.feature" with:
      """
      Feature:
        Scenario Outline: Use weird placeholder values
          Given a param name=<name>

          Examples:
            | name      | Expected | ID  | Case: |
            | <ID>      | 001      | 001 | Value refers to other, known placeholder.|
            | <ID>      | 002      | 002 | Check if row specific value is used.     |
            | <unknown> | <unkown> | 003 | Value refers to unknown placeholder.     |
            | <name>    | <name>   | 004 | Value refers to itself (recursion?).     |
      """
    When I run "behave -f plain --no-timings features/use_value_with_placeholder_syntax.feature"
    Then it should pass with:
      """
      Scenario Outline: Use weird placeholder values -*- @1.1
        Given a param name=001 ... passed

      Scenario Outline: Use weird placeholder values -*- @1.2
        Given a param name=002 ... passed

      Scenario Outline: Use weird placeholder values -*- @1.3
        Given a param name=<unknown> ... passed

      Scenario Outline: Use weird placeholder values -*- @1.4
        Given a param name=<name> ... passed
       """

  @simple.case
  @parametrize.tags
  Scenario: Parametrized tags in a Scenario Outline
    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -*- @{row.id} {examples.name}
      """
    And a file named "features/parametrized_tags.feature" with:
      """
      Feature:
        @foo @outline.e<examples.index> @outline.row.<row.id> @outline.ID.<ID>
        Scenario Outline: Use parametrized tags
          Given a param name=<name>

          Examples:
            | ID  | name  |
            | 001 | Alice |
            | 002 | Bob   |
      """
    When I run "behave -f pretty -c --no-timings features/parametrized_tags.feature"
    Then it should pass with:
      """
      @foo @outline.e1 @outline.row.1.1 @outline.ID.001
      Scenario Outline: Use parametrized tags -*- @1.1   # features/parametrized_tags.feature:8
        Given a param name=Alice                         # features/steps/param_steps.py:7

      @foo @outline.e1 @outline.row.1.2 @outline.ID.002
      Scenario Outline: Use parametrized tags -*- @1.2   # features/parametrized_tags.feature:9
        Given a param name=Bob                           # features/steps/param_steps.py:7
       """
    But note that "special and row data placeholders can be used in tags"


  @parametrize.tags
  Scenario: Parametrized tags in a Scenario Outline (Case: Whitespace... in value)
    Given a file named "behave.ini" with:
      """
      [behave]
      scenario_outline_annotation_schema = {name} -*- @{row.id} {examples.name}
      """
    And a file named "features/parametrized_tags2.feature" with:
      """
      Feature:
        @outline.name.<name>
        Scenario Outline: Use parametrized tags
          Given a param name=<name>

          Examples:
            | ID  | name         | Case: |
            | 001 | Alice Cooper | Placeholder value w/ whitespace |
            | 002 | Bob\tMarley  | Placeholder value w/ tab        |
            | 003 | Joe\nCocker  | Placeholder value w/ newline    |
      """
    When I run "behave -f pretty -c --no-source features/parametrized_tags2.feature"
    Then it should pass with:
      """
      @outline.name.Alice_Cooper
      Scenario Outline: Use parametrized tags -*- @1.1
        Given a param name=Alice Cooper

      @outline.name.Bob_Marley
      Scenario Outline: Use parametrized tags -*- @1.2
        Given a param name=Bob\tMarley

      @outline.name.Joe_Cocker
      Scenario Outline: Use parametrized tags -*- @1.3
        Given a param name=Joe\nCocker
      """
    But note that "placeholder values with special chars (whitespace, ...) are transformed"

