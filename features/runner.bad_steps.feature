# -- HINT: use.with_python.min_version=3.11
Feature: Runner should show Bad Step Definitions

    As a test writer
    I want to know if any bad step definitions exist
    So that I can fix them.

    . DEFINITION: BAD STEP-DEFINITION
    .   * is a step definition (aka: step matcher)
    .     where the regular expression compile step fails
    .   * causes that this step-definition is not registered in the step-registry
    .
    . TEST RUN OUTCOME:
    .   * Used   BAD STEP-DEFINITION (as undefined step) causes test run to fail.
    .   * Unused BAD STEP-DEFINITION does not cause the test run to fail.
    .
    . CAUSED BY: More checks/enforcements in the "re" module (since: Python >= 3.11).


    Background:
        Given a new working directory
        And a file named "features/steps/use_behave4cmd.py" with:
            """
            import behave4cmd0.passing_steps
            import behave4cmd0.note_steps
            """
        And a file named "features/steps/bad_steps1.py" with:
            """
            from behave import given, when, then, register_type, use_step_matcher
            import parse

            # -- HINT: TYPE-CONVERTER with BAD REGEX PATTERN caused by "(?i) parts
            # GOOD PATTERN: "(?P<status>ON|OFF)"
            @parse.with_pattern(r"(?P<status>(?i)ON|(?i)OFF)", regex_group_count=1)
            def parse_bad_bool(text):
                return text == "ON"

            use_step_matcher("parse")
            register_type(BadBool=parse_bad_bool)

            # -- BAD STEP-DEFINITION 1:
            @given('the bad light is switched {state:BadBool}')
            def step_given_light_is_switched_on_off(ctx, state):
                pass
            """
        And a file named "features/steps/bad_steps2.py" with:
            """
            from behave import step, use_step_matcher

            use_step_matcher("re")

            # -- BAD STEP-DEFINITION 2: Caused by "(?i)" parts
            @step('some bad light is switched (?P<status>(?i)ON|(?i)OFF)')
            def step_light_is_switched_using_re(ctx, status):
                pass

            @step('good light is switched (?P<status>ON|OFF)')
            def step_light_is_switched_using_re(ctx, status):
                pass
            """
        And an empty file named "features/none.feature"


  Rule: Unused BAD STEP-DEFINITIONS do not cause test run to fail
    @use.with_python.min_version=3.11
    @use.with_python.max_version=3.12
    Scenario: Runner detects unused BAD STEP DEFINITIONS in dry-run mode

        HINT: Python <= 3.12 uses "error" exception (instead of: PatternError).

        When I run "behave --dry-run -f plain features/"
        Then it should pass with:
          """
          BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
            LOCATION: features/steps/bad_steps1.py:14
            RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:
          """
        And the command output should contain:
          """
          BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
            LOCATION: features/steps/bad_steps2.py:6
            RAISED EXCEPTION: error:global flags not at the start of the expression at position 39
          """
        And the command output should not contain:
          """
          BAD-STEP-DEFINITION: @step('good light is switched (?P<status>ON|OFF)')
          """
        But note that "the step-registry error handler shows each BAD STEP DEFINITIONS with their error"

    @use.with_python.min_version=3.13
    Scenario: Runner detects unused BAD STEP DEFINITIONS in dry-run mode

        HINT: Python >= 3.13 uses "ParseError" exception.

        When I run "behave --dry-run -f plain features/"
        Then it should pass with:
          """
          BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
            LOCATION: features/steps/bad_steps1.py:14
            RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:
          """
        And the command output should contain:
          """
          BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
            LOCATION: features/steps/bad_steps2.py:6
            RAISED EXCEPTION: PatternError:global flags not at the start of the expression at position 39
          """
        And the command output should not contain:
          """
          BAD-STEP-DEFINITION: @step('good light is switched (?P<status>ON|OFF)')
          """
        But note that "the step-registry error handler shows each BAD STEP DEFINITIONS with their error"

    @use.with_python.min_version=3.11
    @use.with_python.max_version=3.12
    Scenario: Runner detects unused BAD STEP DEFINITIONS in normal mode

        HINT: Python <= 3.12 uses "error" exception.

        When I run "behave -f plain features/"
        Then it should pass with:
          """
          BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
            LOCATION: features/steps/bad_steps1.py:14
            RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:
          """
        And the command output should contain:
          """
          BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
            LOCATION: features/steps/bad_steps2.py:6
            RAISED EXCEPTION: error:global flags not at the start of the expression at position 39
          """
        And the command output should not contain:
          """
          BAD-STEP-DEFINITION: @step('good light is switched (?P<status>ON|OFF)')
          """
        But note that "the step-registry error handler shows each BAD STEP DEFINITIONS with their error"

    @use.with_python.min_version=3.13
    Scenario: Runner detects unused BAD STEP DEFINITIONS in normal mode

        HINT: Python >= 3.13 uses "PatternError" exception.

        When I run "behave -f plain features/"
        Then it should pass with:
          """
          BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
            LOCATION: features/steps/bad_steps1.py:14
            RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:
          """
        And the command output should contain:
          """
          BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
            LOCATION: features/steps/bad_steps2.py:6
            RAISED EXCEPTION: PatternError:global flags not at the start of the expression at position 39
          """
        And the command output should not contain:
          """
          BAD-STEP-DEFINITION: @step('good light is switched (?P<status>ON|OFF)')
          """
        But note that "the step-registry error handler shows each BAD STEP DEFINITIONS with their error"

  @use.with_python.min_version=3.11
  Rule: Used BAD STEP-DEFINITIONS cause test run to fail
    Scenario: Runner detects used BAD STEP DEFINITIONS in normal mode
        Given a file named "features/use_bad_step.feature" with:
          """
          Feature: Failing
            Scenario: Uses BAD STEP -- Expected to fail
              Given the bad light is switched ON
              When another step passes
          """
        When I run "behave -f plain features/use_bad_step.feature"
        Then it should fail with:
          """
          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 error, 0 skipped
          0 steps passed, 0 failed, 1 skipped, 1 undefined
          """
        And the command output should contain:
          """
          Errored scenarios:
            features/use_bad_step.feature:2  Uses BAD STEP -- Expected to fail
          """
        And the command output should contain:
          """
          Scenario: Uses BAD STEP -- Expected to fail
              Given the bad light is switched ON ... undefined
          """
        And the command output should contain:
          """
          BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
            LOCATION: features/steps/bad_steps1.py:14
            RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:
          """

    Scenario: Runner detects used BAD STEP DEFINITIONS in dry-run mode
        Given a file named "features/use_bad_step.feature" with:
          """
          Feature: Failing
            Scenario: Uses BAD STEP -- Expected to fail
              Given the bad light is switched ON
              When another step passes
          """
        When I run "behave -f plain --dry-run features/use_bad_step.feature"
        Then it should fail with:
          """
          0 features passed, 0 failed, 1 error, 0 skipped
          0 scenarios passed, 0 failed, 1 error, 0 skipped
          0 steps passed, 0 failed, 0 skipped, 1 undefined, 1 untested
          """
        And the command output should contain:
          """
          Errored scenarios:
            features/use_bad_step.feature:2  Uses BAD STEP -- Expected to fail
          """
        And the command output should contain:
          """
          Scenario: Uses BAD STEP -- Expected to fail
              Given the bad light is switched ON ... undefined
          """
        And the command output should contain:
          """
          BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
            LOCATION: features/steps/bad_steps1.py:14
            RAISED EXCEPTION: NotImplementedError:Group names (e.g. (?P<name>) can cause failure, as they are not escaped properly:
          """
