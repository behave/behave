@sequential
Feature: Parse integer data types in step parameters (type transformation)

  As a test writer
  I want write steps with parameter that should have integer data types
  So that I can just use the step parameter with the correct type


  Behave uses the parse module (inverse of Python string.format).
  Therefore, the following ``parse types`` for integer numbers are already supported:

    ===== =========================================== ============= ================================
    Type  Characters Matched (regex class)            Output Type   Example(s)
    ===== =========================================== ============= ================================
     d     Digits (effectively integer numbers)        int           12345  0b101  0o761  0x1ABE
     n     Numbers with thousands separators (, or .)  int           12,345
     b     Binary numbers                              int           10111  0b1011
     o     Octal numbers                               int           07654  0o123
     x     Hexadecimal numbers (lower and upper case)  int           DEADBEAF  0xBEEF
    ===== =========================================== ============= ================================

    SEE ALSO:
      * http://pypi.python.org/pypi/parse
      * string.format: http://docs.python.org/library/string.html#format-string-syntax


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/integer_param_steps.py" with:
        """
        from behave import then, step

        class NotMatched(object): pass

        @step('a integer param with "{value:d}"')
        def step_integer_param_with(context, value):
            assert type(value) is int
            context.value = value

        @step('a integer param with "{value}"')
        def step_integer_param_otherwise(context, value):
            context.value = NotMatched

        @step('a number param with "{value:n}"')
        def step_number_param_with(context, value):
            step_integer_param_with(context, value)

        @step('a number param with "{value}"')
        def step_number_param_otherwise(context, value):
            step_integer_param_otherwise(context, value)

        @step('a binary number param with "{value:b}"')
        def step_binary_param_with(context, value):
            step_integer_param_with(context, value)

        @step('a binary number param with "{value}"')
        def step_binary_param_otherwise(context, value):
            step_integer_param_otherwise(context, value)

        @step('a octal number param with "{value:o}"')
        def step_hexadecimal_param_with(context, value):
            step_integer_param_with(context, value)

        @step('a octal number param with "{value}"')
        def step_hexadecimal_param_otherwise(context, value):
            step_integer_param_otherwise(context, value)

        @step('a hexadecimal number param with "{value:x}"')
        def step_hexadecimal_param_with(context, value):
            step_integer_param_with(context, value)

        @step('a hexadecimal number param with "{value}"')
        def step_hexadecimal_param_otherwise(context, value):
            step_integer_param_otherwise(context, value)

        @then('the value should be {outcome} as integer number')
        def step_value_should_be_matched_as_number(context, outcome):
            expected_type = int
            if outcome == "matched":
                assert type(context.value) is expected_type, \
                        "Unexpected type: %s" % type(context.value)
            else:
                assert context.value is NotMatched

        @then('the value should be {outcome} as integer number with "{expected:d}"')
        def step_value_should_be_matched_as_number_with_expected(context, outcome, expected):
            step_value_should_be_matched_as_number(context, outcome)
            assert context.value == expected, \
                "FAILED: value(%s) == expected(%s)" % (context.value, expected)
        """


  Scenario: Use type "d" (Digits) for integer params
    Given a file named "features/example.int_param.with_type_d.feature" with:
        """
        Feature: Use type "d" (Digits) for integer params

          Scenario Outline: Good cases
            Given a integer param with "<Value>"
            Then the value should be matched as integer number with "<Expected Value>"

          Examples:
            | Value  | Expected Value | Case |
            |  -1    |   -1 | Negative number |
            |  +1    |    1 | With plus sign  |
            |   0    |    0 |   |
            |   1    |    1 |   |
            |  10    |   10 |   |
            |  42    |   42 |   |


          Scenario Outline: Bad cases (not matched)
            Given a integer param with "<Value>"
            Then the value should be <Outcome> as integer number

          Examples:
            | Value  | Outcome     | Reason |
            |  1.23  | not-matched | Float number |
            |  1E+2  | not-matched | Float number |
            |  Alice | not-matched | Not a number |


          Scenario Outline: Conversion from other number system (base=2, 8, 16)
            Given a integer param with "<Value>"
            Then the value should be matched as integer number with "<Expected Value>"

          Examples:
            | Value   | Expected Value | Case |
            |  0b1011 |    11 | Binary number |
            |  0o123  |    83 | Octal number  |
            |  0xBEEF | 48879 | Hexadecimal number |
        """
    When I run "behave -f plain features/example.int_param.with_type_d.feature"
    Then it should pass with:
        """
        12 scenarios passed, 0 failed, 0 skipped
        """

  Scenario: Use type "n" (Number) for integer params

    This data type supports numbers with thousands separators (',' or '.').

    Given a file named "features/example.int_param.with_type_n.feature" with:
        """
        Feature: Use type "n" (Number) for integer params

          Scenario Outline: Good cases
            Given a number param with "<Value>"
            Then the value should be matched as integer number with "<Expected Value>"

          Examples:
            | Value       | Expected Value |
            |          -1 |       -1 |
            |           0 |        0 |
            |           1 |        1 |
            |          10 |       10 |
            |      12.345 |    12345 |
            |      12,543 |    12543 |
            |  12,345.678 | 12345678 |
            |  12.345,678 | 12345678 |


          Scenario Outline: Bad cases (not matched)
            Given a number param with "<Value>"
            Then the value should be <Outcome> as integer number

          Examples:
            | Value   | Outcome     | Reason |
            |  123.34 | not-matched | Separator in wrong position |
            |  1.23   | not-matched | Float number or separator in wrong position |
            |  1E+2   | not-matched | Float number |
            |  Alice  | not-matched | Not a number |
        """
    When I run "behave -f plain features/example.int_param.with_type_n.feature"
    Then it should pass with:
        """
        12 scenarios passed, 0 failed, 0 skipped
        """

  Scenario: Use type "b" (Binary Number) for integer params
    Given a file named "features/example.int_param.with_type_b.feature" with:
        """
        Feature: Use type "b" (Binary number) for integer params

          Scenario Outline: Good cases
            Given a binary number param with "<Value>"
            Then the value should be matched as integer number with "<Expected Value>"

          Examples:
            | Value    | Expected Value | Case |
            |        0 |    0 |                |
            |        1 |    1 |                |
            |       10 |    2 |                |
            |       11 |    3 |                |
            |      100 |    4 |                |
            |      101 |    5 |                |
            |     0111 |    7 | With padded, leading zero      |
            |   0b1001 |    9 | With binary number prefix "0b" |
            |   0b1011 |   11 | With binary number prefix "0b" |
            | 10000000 |  128 | Larger binary number |

          Scenario Outline: Bad cases (not matched)
            Given a binary number param with "<Value>"
            Then the value should be <Outcome> as integer number

          Examples:
            | Value  | Outcome     | Reason |
            |    21  | not-matched | Invalid binary number |
            |  0b21  | not-matched | Invalid binary number with binary number prefix |
            |  1.23  | not-matched | Float number |
            |  1E+2  | not-matched | Float number |
            |  Alice | not-matched | Not a number |
        """
    When I run "behave -f plain features/example.int_param.with_type_b.feature"
    Then it should pass with:
        """
        15 scenarios passed, 0 failed, 0 skipped
        """

  Scenario: Use type "o" (octal number) for integer params
    Given a file named "features/example.int_param.with_type_o.feature" with:
        """
        Feature: Use type "o" (octal number) for integer params

          Scenario Outline: Good cases
            Given a octal number param with "<Value>"
            Then the value should be matched as integer number with "<Expected Value>"

          Examples:
            | Value    | Expected Value | Case |
            |        0 |    0 |                |
            |       12 |   10 |                |
            |       21 |   17 |                |
            |       65 |   53 |                |
            |      123 |   83 |                |
            |      0o1 |    1 | With leading octal prefix |
            |     0o12 |   10 |                |
            |     0o21 |   17 |                |


          Scenario Outline: Bad cases (not matched)
            Given a octal number param with "<Value>"
            Then the value should be <Outcome> as integer number

          Examples:
            | Value  | Outcome     | Reason |
            |     8  | not-matched | Invalid octal number |
            |    81  | not-matched | Invalid octal number |
            |  0o81  | not-matched | Invalid octal number with octal number prefix |
            |  1.23  | not-matched | Float number |
            |  1E+2  | not-matched | Float number |
            |  Alice | not-matched | Not a number |
        """
    When I run "behave -f plain features/example.int_param.with_type_o.feature"
    Then it should pass with:
        """
        14 scenarios passed, 0 failed, 0 skipped
        """

  Scenario: Use type "x" (hexadecimal number) for integer params
    Given a file named "features/example.int_param.with_type_x.feature" with:
        """
        Feature: Use type "x" (hexadecimal number) for integer params

          Scenario Outline: Good cases
            Given a hexadecimal number param with "<Value>"
            Then the value should be matched as integer number with "<Expected Value>"

          Examples:
            | Value    | Expected Value | Case       |
            |        0 |          0 |                |
            |       12 |         18 |                |
            |       21 |         33 |                |
            |       65 |        101 |                |
            |      123 |        291 |                |
            |     beef |      48879 | With hexadecimal letters (lowercase)  |
            |     BEEF |      48879 | With hexadecimal letters (uppercase)  |
            | deadbeef | 3735928559 | Larger hex number              |
            | DeadBeef | 3735928559 | Larger hex number (mixed case) |
            |     0x01 |          1 | With hexadecimal prefix |
            |     0x12 |         18 |                |
            |     0x21 |         33 |                |
            |   0xbeef |      48879 |                |
            |   0xBeEF |      48879 |                |


          Scenario Outline: Bad cases (not matched)
            Given a hexadecimal number param with "<Value>"
            Then the value should be <Outcome> as integer number

          Examples:
            | Value  | Outcome     | Reason |
            |     G  | not-matched | Invalid hex digit |
            |    G1  | not-matched | Invalid hex number |
            |  0x1G  | not-matched | Invalid hex number with hex number prefix |
            |  1.23  | not-matched | Float number |
            |  1E+2  | not-matched | Float number |
            |  Alice | not-matched | Not a number |
        """
    When I run "behave -f plain features/example.int_param.with_type_x.feature"
    Then it should pass with:
        """
        20 scenarios passed, 0 failed, 0 skipped
        """
