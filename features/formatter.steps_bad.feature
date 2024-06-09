@use.with_python.min_version=3.11
Feature: Bad Steps Formatter (aka: Bad Step Definitions Formatter)

    As a test writer
    I want a summary if any bad step definitions exist
    So that I have an overview what to fix (and look after).

    . DEFINITION: BAD STEP DEFINITION
    .   * Is a step definition (aka: step matcher)
    .     where the regular expression compile step fails
    .
    . CAUSED BY: More checks/enforcements in the "re" module (since: Python >= 3.11).
    .
    . BEST-PRACTICE: Use BadStepsFormatter in dry-run mode, like:
    .
    .       behave --dry-run -f steps.bad features/


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

        # -- HINT: TYPE-CONVERTER with BAD REGEX PATTERN caused by "(?i)" parts
        @parse.with_pattern(r"(?P<status>(?i)ON|(?i)OFF)", regex_group_count=1)
        def parse_bad_bool(text):
            return text == "ON"

        use_step_matcher("parse")
        register_type(BadBool=parse_bad_bool)

        # -- BAD STEP DEFINITION 1:
        @given('the bad light is switched {state:BadBool}')
        def step_bad_given_light_is_switched_on_off(ctx, state):
            pass
        """
    And a file named "features/steps/bad_steps2.py" with:
        """
        from behave import step, use_step_matcher

        use_step_matcher("re")

        # -- BAD STEP DEFINITION 2: Caused by "(?i)" parts
        @step('some bad light is switched (?P<status>(?i)ON|(?i)OFF)')
        def step_bad_light_is_switched_using_re(ctx, status):
            pass

        @step('good light is switched (?P<status>ON|OFF)')
        def step_good_light_is_switched_using_re(ctx, status):
            pass
        """
    And a file named "features/one.feature" with:
        """
        Feature: F1
          Scenario: S1
            Given a step passes
            When another step passes
        """

  Scenario: Use "bad_steps" formatter in dry-run mode
    When I run "behave --dry-run -f steps.bad features/"
    Then the command output should contain:
      """
      BAD STEP-DEFINITIONS[2]:
      - BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
        LOCATION: features/steps/bad_steps1.py:13
      - BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
        LOCATION: features/steps/bad_steps2.py:6
      """
    But note that "the formatter shows a list of BAD STEP DEFINITIONS"

  Scenario: Use "bad_steps" formatter in normal mode
    When I run "behave -f steps.bad features/"
    Then the command output should contain:
      """
      BAD STEP-DEFINITIONS[2]:
      - BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
        LOCATION: features/steps/bad_steps1.py:13
      - BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
        LOCATION: features/steps/bad_steps2.py:6

      1 feature passed, 0 failed, 0 skipped
      """
    But note that "the formatter shows a list of BAD STEP DEFINITIONS"

  Scenario: Use "bad_steps" formatter with another formatter
    When I run "behave -f steps.bad -f plain features/"
    Then the command output should contain:
      """
      Feature: F1

        Scenario: S1
          Given a step passes ... passed
          When another step passes ... passed

      BAD STEP-DEFINITIONS[2]:
      - BAD-STEP-DEFINITION: @given('the bad light is switched {state:BadBool}')
        LOCATION: features/steps/bad_steps1.py:13
      - BAD-STEP-DEFINITION: @step('^some bad light is switched (?P<status>(?i)ON|(?i)OFF)$')
        LOCATION: features/steps/bad_steps2.py:6

      1 feature passed, 0 failed, 0 skipped
      """
    But note that "the BAD_STEPS formatter output is shown at the end"
