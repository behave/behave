@use.with_python.min_version=3.8
Feature: Use StepMatcher with CucumberExpressions

    As a test writer
    I want to write steps in "*.feature" files with CucumberExpressions
    So that I can use a human friendly alternative to regular expressions
    And that I can use parameter types and type converters for them.

    . CUCUMBER EXPRESSIONS:
    . * Provide a compact, readable placeholder syntax in step definitions
    . * Support pre-defined parameter types with type conversion
    . * Support to define own parameter types
    .
    . STEP DEFINITION EXAMPLES WITH CUCUMBER EXPRESSIONS:
    .   I have {int} cucumbers in my belly
    .   I have {float} cucumbers in my belly
    .   I have a {color} ball
    .
    . PREDEFINED PARAMETER TYPES:
    .   | ParameterType | Type    | Description
    .   | {int}         | int     | Matches an 32-bit integer number and converts to it, like: 42 |
    .   | {float}       | float   | Matches "float" (as 32-bit float), like: `3.6`, `.8`, `-9.2`  |
    .   | {word}        | string  | Matches one word without whitespace, like: `banana` (not: `banana split`).
    .   | {string}      | string  | Matches double-/single-quoted strings, for example `"banana split"` (not: `banana split`). |
    .   | {}            | string  | Matches anything, like `re_pattern = ".*"`                                    |
    .   | {bigdecimal}  | Decimal | Matches "float", but converts to "BigDecimal" if platform supports it.        |
    .   | {double}      | float   | Matches "float", but converts to 64-bit float number if platform supports it. |
    .   | {biginteger}  | int     | Matches "int", but converts to "BigInteger" if platform supports it.          |
    .   | {byte}        | int     | Matches "int", but converts to 8-bit signed integer if platform supports it.  |
    .   | {short}       | int     | Matches "int", but converts to 16-bit signed integer if platform supports it. |
    .   | {long}        | int     | Matches "int", but converts to 64-bit signed integer if platform supports it. |
    .
    . STEP DEFINITION EXAMPLES FOR MATCHING OTHER PARTS:
    . * MATCHING OPTIONAL TEXT, like:
    .       I have {int} cucumber(s) in my belly
    .     MATCHES:
    .       I have 1 cucumber in my belly
    .       I have 42 cucumbers in my belly
    .
    . * ALTERNATIVE TEXT, like:
    .       I have {int} cucumber(s) in my belly/stomach
    .     MATCHES:
    .       I have 1 cucumber in my belly
    .       I have 42 cucumbers in my stomach
    .
    . * ESCAPING  TO USE: `()` or `{}`, like:
    .       I have {int} \{what} cucumber(s) in my belly \(amazing!)
    .     MATCHES:
    .       I have 1 {what} cucumber in my belly (amazing!)
    .       I have 42 {what} cucumbers in my belly (amazing!)
    .
    . SEE ALSO: https://github.com/cucumber/cucumber-expressions
    . SIMILAR: parse-expressions
    .  * https://github.com/r1chardj0n3s/parse
    .  * https://github.com/jenisys/parse_type


    Background:
        Given a new working directory
        And an empty file named "example4me/__init__.py"
        And a file named "example4me/color.py" with:
            """
            from enum import Enum

            class Color(Enum):
                red = 1
                green = 2
                blue = 3

                @classmethod
                def from_name(cls, text: str):
                    text = text.lower()
                    for enum_item in iter(cls):
                        if enum_item.name == text:
                            return enum_item
                    # -- OOPS:
                    raise ValueError("UNEXPECTED: {}".format(text))
            """
        And a file named "features/steps/page_steps.py" with:
            """
            from behave import step

            # -- STEP DEFINITIONS: Use ALTERNATIVES
            @step("I am on the profile customisation/settings page")
            def step_on_profile_settings_page(ctx):
                print("STEP: Given I am on profile ... page")
            """
        And a file named "features/environment.py" with:
            """
            from behave.cucumber_expression import use_step_matcher_for_cucumber_expressions

            # -- HINT: Use StepMatcher4CucumberExpressions as default step-matcher.
            use_step_matcher_for_cucumber_expressions()
            """

  @fixture.behave.override_background
  Rule: Use predefined ParameterType(s)

    Background:

    Scenario Outline: Number ParameterType:<parameter_type>
      When I provide an "<value>" value as <parameter_type>
      Then the stored value equals "<value>" as <value_type>

      Examples: Integer number
        | parameter_type | value | value_type |
        | int            |   11   | int        |
        | short          |  -12   | int        |
        | long           |   13   | int        |
        | biginteger     |  -14   | int        |
        | byte           |   15   | int        |

      Examples: Floating-point number
        | parameter_type | value  | value_type |
        | float          |  1.2   | float      |
        | double         | -10.2  | float      |
        | bigdecimal     |  13.02 | float      |


    Scenario Outline: String-like ParameterType:<parameter_type>
      When I provide an "<value>" value as <parameter_type>
      Then the stored value equals "<value>" as string

      Examples: String
        | parameter_type | value         | value_type |
        | word           | Alice         | string     |
        | string         | Alice and Bob | string     |

      Examples: Match anything
        | parameter_type | value         | value_type |
        | any            | Alice has 2   | string     |


  Rule: Use own ParameterType(s)
    Scenario: Use Step-Definitions with Step-Parameters
        And a file named "features/steps/color_steps.py" with:
            """
            from behave import given, when, then
            from behave.cucumber_expression import (
                ParameterType,
                define_parameter_type,
                define_parameter_type_with
            )
            from example4me.color import Color

            # -- REGISTER PARAMETER TYPES:
            # OR: Use define_parameter_type_with(name="color", ...)
            define_parameter_type(ParameterType(
                name="color",
                regexp="red|green|blue",
                type=Color,
                transformer=Color.from_name
            ))

            # -- STEP DEFINITIONS: With OPTIONAL parts.
            @when('I select the "{color}" theme colo(u)r')
            def step_when_select_color_theme(ctx, color: Color):
                assert isinstance(color, Color)
                ctx.selected_color = color

            @then('the profile colo(u)r should be "{color}"')
            def step_then_profile_color_should_be(ctx, the_color: Color):
                assert isinstance(the_color, Color)
                assert ctx.selected_color == the_color
            """
        And a file named "features/cucumber_expression.feature" with:
            """
            Feature: Use CucumberExpressions in Step Definitions
                Scenario: User selects a color twice
                  Given I am on the profile settings page
                  When I select the "red" theme colour
                  But  I select the "blue" theme color
                  Then the profile color should be "blue"
            """
        When I run "behave -f plain features/cucumber_expression.feature"
        Then it should pass with:
          """
          Feature: Use CucumberExpressions in Step Definitions
            Scenario: User selects a color twice
              Given I am on the profile settings page ... passed
              When I select the "red" theme colour ... passed
              But I select the "blue" theme color ... passed
              Then the profile color should be "blue" ... passed
          """
        And the command output should contain:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          4 steps passed, 0 failed, 0 skipped
          """
        And note that "step-definitions with CucumberExpressions can be used"


  Rule: Use TypeBuilder for ParameterType(s)

    Scenario: Use TypeBuilder for Color enum
        And a file named "features/steps/color_steps.py" with:
            """
            from behave import given, when, then
            from behave.cucumber_expression import define_parameter_type_with
            from example4me.color import Color
            from parse_type import TypeBuilder

            parse_color = TypeBuilder.make_enum(Color)

            # -- REGISTER PARAMETER TYPES:
            define_parameter_type_with(
                name="color",
                regexp=parse_color.pattern,
                type=Color,
                transformer=parse_color
            )

            # -- STEP DEFINITIONS: With OPTIONAL parts.
            @when('I select the "{color}" theme colo(u)r')
            def step_when_select_color_theme(ctx, color: Color):
                assert isinstance(color, Color)
                ctx.selected_color = color

            @then('the profile colo(u)r should be "{color}"')
            def step_then_profile_color_should_be(ctx, the_color: Color):
                assert isinstance(the_color, Color)
                assert ctx.selected_color == the_color
            """
        And a file named "features/cucumber_expression.feature" with:
            """
            Feature: Use CucumberExpressions in Step Definitions
                Scenario: User selects a color twice
                  Given I am on the profile settings page
                  When I select the "red" theme colour
                  But  I select the "blue" theme color
                  Then the profile color should be "blue"
            """
        When I run "behave -f plain features/cucumber_expression.feature"
        Then it should pass with:
          """
          Feature: Use CucumberExpressions in Step Definitions
            Scenario: User selects a color twice
              Given I am on the profile settings page ... passed
              When I select the "red" theme colour ... passed
              But I select the "blue" theme color ... passed
              Then the profile color should be "blue" ... passed
          """
        And the command output should contain:
          """
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          4 steps passed, 0 failed, 0 skipped
          """
        And note that "step-definitions with CucumberExpressions can be used"

    Scenario: Use TypeBuilder for Many Items
        And a file named "features/steps/many_color_steps.py" with:
          """
          from typing import List
          from behave import given, when, then
          from behave.cucumber_expression import (
              TypeBuilder,
              define_parameter_type_with
          )
          from example4me.color import Color
          from assertpy import assert_that

          parse_color = TypeBuilder.make_enum(Color)
          parse_colors = TypeBuilder.with_many(parse_color)

          # -- REGISTER PARAMETER TYPES:
          define_parameter_type_with(
              name="colors",
              regexp=parse_colors.pattern,
              type=list,  # HINT: List[Color]
              transformer=parse_colors
          )

          # -- STEP DEFINITIONS: With OPTIONAL parts.
          @when('I select the "{colors}" colo(u)r(s)')
          def step_when_select_many_colors(ctx, colors: List[Color]):
              assert isinstance(colors, list)
              for index, color in enumerate(colors):
                  assert isinstance(color, Color), "%r (index=%d)" % (color, index)
              ctx.selected_colors = colors

          @then('I have selected {int} colo(u)r(s)')
          def step_then_count_selected_colors(ctx, number_of_colors: int):
              assert isinstance(number_of_colors, int)
              assert_that(ctx.selected_colors).is_length(number_of_colors)
          """
        And a file named "features/many_colors.feature" with:
          """
          Feature: Use TypeBuilder.with_many
            Scenario: User selects many colors with cardinality=1
              When I select the "blue" colour
              Then I have selected 1 colour

            Scenario: User selects many colors with cardinality=3
              When I select the "red, blue, green" colors
              Then I have selected 3 colors
          """
        When I run "behave -f plain features/many_colors.feature"
        Then it should pass with:
          """
          Scenario: User selects many colors with cardinality=1
            When I select the "blue" colour ... passed
            Then I have selected 1 colour ... passed

          Scenario: User selects many colors with cardinality=3
            When I select the "red, blue, green" colors ... passed
            Then I have selected 3 colors ... passed
          """
        And note that "TypeBuilder.with_many() can be used with ParameterType(s)"
