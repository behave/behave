@issue
Feature: Issue #216: ANSI escape sequences are used while using --wip option

  . ENSURE THAT:
  .   * Coloring is disabled when --wip option is used.
  .   * In addition, no colouring is used when using --show-skipped option
  .   * Undefined step snippets are not "colored".

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "behave.ini" with:
        """
        [behave]
        default_format = pretty
        show_skipped   = false
        show_timings   = false
        """
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.passing_steps
        import behave4cmd0.failing_steps
        import behave4cmd0.note_steps
        """
    And a file named "features/steps/ansi_steps.py" with:
        """
        from behave import step, then
        from behave4cmd0.command_steps import step_command_output_should_not_contain_text

        @then(u'the command output should not contain any ANSI escape sequences')
        def step_command_ouput_should_not_contain_ansi_sequences(context):
            CSI = u"\x1b["  #< ANSI CONTROL SEQUENCE INTRODUCER (CSI).
            step_command_output_should_not_contain_text(context, CSI)
        """
    And a file named "features/scenario_with_undefined_steps.feature" with:
        """
        Feature:

          @wip
          Scenario: Alice
            Given a step passes
            When a step is undefined
            Then a step passes

          @foo
          Scenario: Bob
            When another step is undefined
        """


  Scenario: When using --wip, coloring is disabled
    When I run "behave --wip features"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped, 1 untested
      1 step passed, 0 failed, 1 skipped, 1 undefined, 1 untested
      """
    And the command output should contain:
      """
      Scenario: Alice
        Given a step passes ... passed
        When a step is undefined ... undefined
      """
    But the command output should not contain any ANSI escape sequences
    And note that "the plain formatter is used as default formatter"


  Scenario: When using --wip and --show-skipped, coloring is disabled
    When I run "behave --wip --show-skipped features"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped, 1 untested
      1 step passed, 0 failed, 1 skipped, 1 undefined, 1 untested
      """
    And the command output should contain:
      """
      Scenario: Alice
        Given a step passes ... passed
        When a step is undefined ... undefined
      """
    But the command output should not contain any ANSI escape sequences
    And note that "the plain formatter is used as default formatter"


  Scenario: When using --wip and --format, coloring is disabled
    When I run "behave --wip -f pretty features"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped, 1 untested
      1 step passed, 0 failed, 1 skipped, 1 undefined, 1 untested
      """
    And the command output should contain:
      """
      Feature:  # features/scenario_with_undefined_steps.feature:1

        @wip
        Scenario: Alice            # features/scenario_with_undefined_steps.feature:4
          Given a step passes      # ../behave4cmd0/passing_steps.py:23
          When a step is undefined # None
          Then a step passes       # None
      """
    But the command output should not contain any ANSI escape sequences
    And note that "the plain formatter is overridden on command-line"
    And note that "the coloring mode is disabled"


  Scenario: When using --wip and --color, coloring is disabled
    When I run "behave --wip -f pretty --color features"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped, 1 untested
      1 step passed, 0 failed, 1 skipped, 1 undefined, 1 untested
      """
    And the command output should contain:
      """
      Feature:  # features/scenario_with_undefined_steps.feature:1

        @wip
        Scenario: Alice            # features/scenario_with_undefined_steps.feature:4
          Given a step passes      # ../behave4cmd0/passing_steps.py:23
          When a step is undefined # None
          Then a step passes       # None
      """
    But the command output should not contain any ANSI escape sequences
    And note that "the coloring mode is overridden by the wip mode"
