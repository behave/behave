@sequential
@todo
Feature: Parse custom data types in step parameters (type transformation)

  As a test writer
  I want to provide own type parsers (and matcher)
  to simplify writing step definitions.

  . WORKS ONLY WITH MATCHERS:
  .   * parse
  .   * cfparse (parse with cardinality field extension)


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/type_converter_steps.py" with:
        """
        from behave import then, step, register_type
        import parse

        @parse.with_pattern(r"\d+")  # -- ONLY FOR: Zero and positive integers.
        def parse_number(text):
            return int(text)

        register_type(Number=parse_number)
        class NotMatched(object): pass

        @step('a param with "Number:{value:Number}"')
        def step_param_with_number_value(context, value):
            assert isinstance(value, int)
            context.value = value

        @step('a param with "{type:w}:{value}"')
        def step_param_with_unknown_type_value(context, type, value):
            context.value = NotMatched

        @then('the param should be "{outcome}"')
        def step_value_should_be_matched_or_not_matched(context, outcome):
            if outcome == "matched":
                assert isinstance(context.value, int), \
                        "Unexpected type: %s" % type(context.value)
                assert context.value is not NotMatched
            elif outcome == "not matched":
                assert context.value is NotMatched
            else:
              raise ValueError("INVALID: outcome=%s (use: matched, not matched)" % outcome)
        """
    And a file named "features/steps/common_steps.py" with:
        """
        from behave4cmd0 import passing_steps
        """
    And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        show_timings = false
        """


  Scenario: Use own custom type for numbers
    Given a file named "features/example.number_type.feature" with:
        """
        Feature: Simple Custom Type for Numbers

          Scenario Outline: Numbers
            Given a param with "Number:<value>"
            Then the param should be "<outcome>"

          Examples: Good cases for type=Number
            | value  | outcome | Case |
            |   0    | matched | Zero |
            |   1    | matched | One  |
            |  10    | matched | Positive number with 2 digits.  |
            |  42    | matched | Another positive number. |

          Examples: Bad cases for type=Number
            | value  | outcome     | Case |
            |  +1    | not matched | Positive number with plus sign. |
            |  -1    | not matched | Negative number. |
            | 1.234  | not matched | BAD: Floating-point number. |
            | ABC    | not matched | BAD: Not a number. |
        """
    When I run "behave -f plain features/example.number_type.feature"
    Then it should pass with:
        """
        8 scenarios passed, 0 failed, 0 skipped
        """


  Scenario: Type conversion fails
    Given a file named "features/steps/bad_type_converter_steps.py" with:
        """
        from behave import step, register_type
        import parse

        @parse.with_pattern(r".*")  # -- NOTE: Wildcard pattern, accepts anything.
        def parse_fails(text):
            raise ValueError(text)

        register_type(BadType=parse_fails)

        @step('a param with "BadType:{value:BadType}"')
        def step_param_with_badtype_value(context, value):
            assert False, "SHOULD_NEVER_COME_HERE: BadType converter raises error."
        """
    And a file named "features/example.type_conversion_fails.feature" with:
        """
        Feature: Type Conversion Fails
          Scenario: BadType raises ValueError during type conversion
            Given a param with "BadType:BAD_VALUE"

          Scenario: Ensure other scenarios are executed
            Then another step passes
        """
    When I run "behave -f plain features/example.type_conversion_fails.feature"
    Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Scenario: BadType raises ValueError during type conversion
          Given a param with "BadType:BAD_VALUE" ... failed
        Traceback (most recent call last):
        """
    And the command output should contain:
        """
        File "features/steps/bad_type_converter_steps.py", line 6, in parse_fails
          raise ValueError(text)
        """
    And the command output should contain "ValueError: BAD_VALUE"
    And the command output should contain "StepParseError: BAD_VALUE"
