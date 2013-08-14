@sequential
Feature: Parse data types in step parameters (type transformation)

  As a test writer
  I want write steps with parameter that should have floating-point data types
  So that I can just use the step parameter with the correct type

  behave uses the parse module (inverse of Python string.format).
  Therefore, the following ``parse types`` for floats are already supported:

    ===== =========================================== ============= ================================
    Type  Characters Matched (regex class)            Output Type   Example(s)
    ===== =========================================== ============= ================================
     %     Percentage (converted to value/100.0)       float         51.2%
     f     Fixed-point numbers                         float         1.23  -1.45
     e     Floating-point numbers with exponent        float         1.1e-10  -12.3E+5
     g     General number format (either d, f or e)    float         123  1.23  -1.45E+12
    ===== =========================================== ============= ================================


    SEE ALSO:
      * http://pypi.python.org/pypi/parse
      * string.format: http://docs.python.org/library/string.html#format-string-syntax


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/float_param_steps.py" with:
        """
        from behave import then, step
        class NotMatched(object): pass

        @step('a float param with "{value:g}"')
        def step_float_param_with(context, value):
            assert type(value) is float
            context.value = value

        @step('a float param with "{value}"')
        def step_float_param_otherwise(context, value):
            context.value = NotMatched

        @step('a generic float param with "{value:g}"')
        def step_generic_float_param_with(context, value):
            step_float_param_with(context, value)

        @step('a generic float param with "{value}"')
        def step_generic_float_param_otherwise(context, value):
            step_float_param_otherwise(context, value)

        @step('a float with exponent param with "{value:e}"')
        def step_float_with_exponent_param_with(context, value):
            step_float_param_with(context, value)

        @step('a float with exponent param with "{value}"')
        def step_float_with_exponent_param_otherwise(context, value):
            step_float_param_otherwise(context, value)

        @step('a percentage param with "{value:%}"')
        def step_percentage_param_with(context, value):
            step_float_param_with(context, value)

        @step('a percentage param with "{value}"')
        def step_percentage_param_otherwise(context, value):
            step_float_param_otherwise(context, value)

        @step('a fixed-point number param with "{value:f}"')
        def step_fixed_point_number_param_with(context, value):
            step_float_param_with(context, value)

        @step('a fixed-point number param with "{value}"')
        def step_fixed_point_number_param_otherwise(context, value):
            step_float_param_otherwise(context, value)

        @then('the value should be {outcome} as float number')
        def step_value_should_be_matched_as_float_number(context, outcome):
            expected_type = float
            if outcome == "matched":
                assert type(context.value) is expected_type, \
                        "Unexpected type: %s" % type(context.value)
            else:
                assert context.value is NotMatched

        @then('the value should be {outcome} as float number with "{expected:g}"')
        def step_value_should_be_matched_as_float_number_with_expected(context, outcome, expected):
            step_value_should_be_matched_as_float_number(context, outcome)
            assert context.value == expected, \
                "FAILED: value(%s) == expected(%s)" % (context.value, expected)
        """


  Scenario: Float parameter values with type "%" (percentage)
    Given a file named "features/example.float_param.with_percent.feature" with:
        """
        Feature: Float parameter values with type "%" (percentage)

          Scenario Outline: Good cases
            Given a percentage param with "<Value>"
            Then the value should be matched as float number with "<Expected Value>"

          Examples:
            | Value  | Expected Value | Case |
            |    0%  |    0     | Zero       |
            |   20%  |    0.2   | Positive number   |
            |  120%  |    1.2   | Larger than 100%  |
            | 10.5%  |    0.105 | Float number    |
            |  -10%  |   -0.1   | Negative number |
            |  +10%  |    0.1   | With plus sign  |


          Scenario Outline: Bad cases (not matched)
            Given a percentage param with "<Value>"
            Then the value should be <Outcome> as float number

          Examples:
            | Value  | Outcome     | Reason |
            |   123  | not-matched | Percentage sign is missing |
            |  1.23  | not-matched | Float number without percentage sign |
            |  Alice | not-matched | Not a number |
        """
    When I run "behave -f plain features/example.float_param.with_percent.feature"
    Then it should pass with:
        """
        9 scenarios passed, 0 failed, 0 skipped
        """


  Scenario: Fixed-point parameter values with type "f"
    Given a file named "features/example.float_param.with_type_f.feature" with:
        """
        Feature: Float parameter values with type "f" (fixed-point number)

          Scenario Outline: Good cases
            Given a fixed-point number param with "<Value>"
            Then the value should be matched as float number with "<Expected Value>"

          Examples:
            | Value  | Expected Value | Case     |
            |   0.23 |    0.23  |                |
            |   1.23 |    1.23  |                |
            | 123.45 |  123.45  |                |
            |  +1.23 |    1.23  | With plus sign |
            |  -1.23 |   -1.23  | Negative float |


          Scenario Outline: Bad cases (not matched)
            Given a fixed-point number param with "<Value>"
            Then the value should be <Outcome> as float number

          Examples:
            | Value   | Outcome     | Reason |
            |   123   | not-matched | Integer number             |
            | 1.23E-7 | not-matched | Float number with exponent |
            |  Alice  | not-matched | Not a number               |
        """
    When I run "behave -f plain features/example.float_param.with_type_f.feature"
    Then it should pass with:
        """
        8 scenarios passed, 0 failed, 0 skipped
        """


  Scenario: Float with exponent parameter values with type "e"
    Given a file named "features/example.float_param.with_type_e.feature" with:
        """
        Feature: Float parameter values with type "e" (float with exponents)

          Scenario Outline: Good cases
            Given a float with exponent param with "<Value>"
            Then the value should be matched as float number with "<Expected Value>"

          Examples:
            | Value     | Expected Value | Case                |
            |  1.0E-10  |   1E-10   | With mantisse, negative exponent |
            |  1.23E+5  |   123E3   | Exponent with plus sign  |
            |  123.0E+3 |  1.23E5   | Exponent with plus sign  |
            | -1.23E5   |  -123E3   | Negative number with mantisse and exponent |
            |     INF   |    +INF   | Infinity (INF)           |
            |    +INF   |     INF   |                          |
            |    -INF   |    -INF   |                          |
            |    +inf   |     INF   | Lower-case special names |


          Scenario Outline: Bad cases (not matched)
            Given a float with exponent param with "<Value>"
            Then the value should be <Outcome> as float number

          Examples:
            | Value   | Outcome     | Reason |
            |   1E10  | not-matched | Without mantissa |
            |   1.E10 | not-matched | Short mantissa   |
            |   123   | not-matched | Integer number   |
            |  Alice  | not-matched | Not a number     |
        """
    When I run "behave -f plain features/example.float_param.with_type_e.feature"
    Then it should pass with:
        """
        12 scenarios passed, 0 failed, 0 skipped
        """


  Scenario: Generic float parameter values with type "g"
    Given a file named "features/example.float_param.with_type_g.feature" with:
        """
        Feature: Float parameter values with type "g" (generic float)

          Scenario Outline: Good cases
            Given a generic float param with "<Value>"
            Then the value should be matched as float number with "<Expected Value>"

          Examples:
            | Value     | Expected Value | Case                |
            |        1  |   1.0     | Integer number format    |
            |     1E10  |   1.0E10  | Float with exponent and shortened mantissa |
            |   1.23E5  |   1.23E5  | Float with exponent and mantissa |
            |   1.23e5  |   1.23E5  | Float with exponent and mantissa (lower-case) |
            |  1.0E-10  |   1E-10   | With mantisse, negative exponent |
            |  1.23E+5  |   123E3   | Exponent with plus sign   |
            |  123.0E+3 |   1.23E5  | Exponent with plus sign   |
            | -1.23E5   |  -123E3   | Negative number with mantisse and exponent |


          Scenario Outline: Bad cases (not matched)
            Given a generic float param with "<Value>"
            Then the value should be <Outcome> as float number

          Examples:
            | Value   | Outcome     | Reason             |
            | 0b101   | not-matched | Binary number      |
            | 0o17    | not-matched | Octal number       |
            | 0x1A    | not-matched | Hexadecimal number |
            | 1.E10   | not-matched | Short mantissa     |
            | Alice   | not-matched | Not a number       |
        """
    When I run "behave -f plain features/example.float_param.with_type_g.feature"
    Then it should pass with:
        """
        13 scenarios passed, 0 failed, 0 skipped
        """
