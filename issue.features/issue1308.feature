@issue
@logging
@capture
Feature: Issue #1308 -- before_scenario hook prevents capturing logs

  . DESCRIPTION:
  .   If the environment file has a "before_scenario" hook (even an empty one),
  .   the log records of the steps are no longer captured:
  .   The "CAPTURED LOG" section is missing in the failure report.
  .
  . REASON:
  .   The hook is captured on its own (nested capture). Its LoggingCapture
  .   removes the active LoggingCapture of the scenario from the root logger
  .   and does not reinstate it when the hook is done.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1308

  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log_steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """
    And a file named "behave.ini" with:
        """
        [behave]
        logging_format = LOG_%(levelname)s:%(name)s: %(message)s
        """
    And a file named "features/example.log_and_fail.feature" with:
        """
        Feature:
          Scenario: Failing
            Given I create log records with:
                | category | level   | message |
                | root     |  FATAL  | Hello Alice  |
                | foo      |  ERROR  | Hello Bob    |
                | foo.bar  |  WARN   | Hello Charly |
                | bar      |  INFO   | Hello Dora   |
                | baz      |  DEBUG  | Hello Emily  |
            When another step fails
        """

  Scenario Outline: Log records are captured <case>
    Given a file named "features/environment.py" with:
        """
        from behave.capture import capture_output

        @capture_output(show_on_success=True)
        def before_all(context):
            context.config.setup_logging()

        <hook>
        """
    When I run "behave -f plain -T --capture-log features/example.log_and_fail.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped
        """
    And the command output should contain "CAPTURED LOG:"
    And the command output should contain the following log records:
        | category | level   | message |
        | root     |  FATAL  | Hello Alice  |
        | foo      |  ERROR  | Hello Bob    |
        | foo.bar  |  WARN   | Hello Charly |
        | bar      |  INFO   | Hello Dora   |
    But the command output should not contain the following log records:
        | category | level   | message     | Comment |
        | baz      |  DEBUG  | Hello Emily | Log-level too low: filtered-out |

    Examples:
      | case                         | hook |
      | without hook (baseline)      | pass |
      | with a before_scenario hook  | def before_scenario(context, scenario): pass |
      | with a before_step hook      | def before_step(context, step): pass |
      | with an after_step hook      | def after_step(context, step): pass |
