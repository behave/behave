@issue
Feature: Issue #383 -- Handle (custom) Type parsing errors better

  . Custom type parsing errors that occur during step matching
  . lead currently to abortion of the test run.
  . In addition, the actual reason what occured is very low-level.
  .
  . DESIRED:
  .   * Protect test runner/execution logic
  .   * Improve handling of these kind of errors
  .   * Provide better diagnostics
  .   * Continue to run tests (if possible)
  .
  . NOTE:
  . This kind of problem is often caused by regular expressions that
  . are not specific enough for the type conversion (LAZY-REGEXP DESIGN).
  . Therefore, the problem occurs during type conversion/parsing phase
  . and not in the initial step detection/matching phase.
  .
  . RELATED: features/step_param.custom_types.feature


  Scenario: Type conversion fails
    Given a new working directory
    And a file named "features/steps/bad_type_converter_steps.py" with:
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
    And a file named "features/steps/reused_steps.py" with:
        """
        from behave4cmd0 import passing_steps
        """
    And a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
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
