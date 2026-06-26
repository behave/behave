@issue
@logging
@capture
Feature: Issue #1323 -- JSON report missing captured logging on failure

  Ensure the JSON formatter provides the captured output (stdout/stderr/log)
  as first-class fields in the step "result". This way, JSON reports retain
  the "Captured logging" of a failing scenario.

  . REGRESSION: Since the capture refactoring (behave v1.2.7),
  .   "JSONFormatter.result()" stopped including the captured logging that was
  .   previously inlined into the "error_message" of a failed step.
  .
  . RELATED:
  .  * features/formatter.json.feature
  .  * features/capture_log.feature

  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log_steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """
    And a file named "features/environment.py" with:
        """
        def before_all(context):
            context.config.setup_logging()
        """
    And a file named "features/log_and_fail.feature" with:
        """
        Feature:
          Scenario: Failing with logs
            Given I create log records with:
                | category | level | message      |
                | foo      | ERROR | Hello Bob    |
                | bar      | WARN  | Hello Charly |
            When another step fails
        """

  Scenario: Captured log is included in JSON report when a scenario fails
    When I run "behave -f json.pretty -T --capture-log features/log_and_fail.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """
    And the command output should contain:
        """
            "captured_log": [
              "LOG_ERROR:foo: Hello Bob",
              "LOG_WARNING:bar: Hello Charly"
            ],
        """
    But the command output should not contain "captured_stderr"
