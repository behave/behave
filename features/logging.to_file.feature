@use.with_python.min_version=3.2
Feature: Logging to a file

  As a tester
  I want to setup logging to use a log-file as sink
  To be able to diagnose problematic details later.

  . SPECIFICATION:
  .   If logging is configured to use a file as sink,
  .   any log-record will be contained in it.
  .
  .   This does not depend on:
  .
  .   * log-capture is enabled or not
  .   * logging categories are excluded from log-capture by using a logging-filter

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
        # -- REQUIRES: Python >= 3.2 -- f-string log-format style.
        [behave]
        capture_log = true
        logging_level = INFO
        logging_format = LOG.{levelname} -- {name}: {message}
        """
    And I use "LOG.{levelname} -- {name}: {message}" as log record format
    And a file named "features/environment.py" with:
        """
        def before_all(ctx):
            log_format = "LOGFILE.{levelname} -- {name}: {message}"
            ctx.config.setup_logging(filename="behave.log", format=log_format)
        """

  Scenario: Log records for passing steps appear in log-file
    Given a file named "features/log_records_and_passes.feature" with:
        """
        Feature:
          Scenario: Log Records and Passing
            Given I create log records with:
              | category | level   | message |
              | root     | ERROR   | LOG_MESSAGE_1 |
              | foo      | WARNING | LOG_MESSAGE_2 |
              | foo.bar  | INFO    | LOG_MESSAGE_3 |
              | bar      | ERROR   | LOG_MESSAGE_4 |
            When another step passes
        """
    When I run "behave -f plain features/log_records_and_passes.feature"
    Then it should pass
    And the command output should not contain the following log records:
        | category | level   | message       |
        | root     | ERROR   | LOG_MESSAGE_1 |
        | foo      | WARNING | LOG_MESSAGE_2 |
        | foo.bar  | INFO    | LOG_MESSAGE_3 |
        | bar      | ERROR   | LOG_MESSAGE_4 |
    But the file "behave.log" should contain:
        """
        LOGFILE.ERROR -- root: LOG_MESSAGE_1
        LOGFILE.WARNING -- foo: LOG_MESSAGE_2
        LOGFILE.INFO -- foo.bar: LOG_MESSAGE_3
        LOGFILE.ERROR -- bar: LOG_MESSAGE_4
        """

  Scenario: Log records for failing scenario appear in log-file
    Given a file named "features/log_records_then_fails.feature" with:
        """
        Feature:
          Scenario: Log Records and Then Failing
            Given I create log records with:
              | category | level   | message |
              | root     | ERROR   | LOG_MESSAGE_1 |
              | foo      | WARNING | LOG_MESSAGE_2 |
              | foo.bar  | INFO    | LOG_MESSAGE_3 |
              | bar      | ERROR   | LOG_MESSAGE_4 |
            When another step fails
        """
    When I run "behave -f plain features/log_records_then_fails.feature"
    Then it should fail
    And the command output should contain the following log records:
        | category | level   | message       |
        | root     | ERROR   | LOG_MESSAGE_1 |
        | foo      | WARNING | LOG_MESSAGE_2 |
        | foo.bar  | INFO    | LOG_MESSAGE_3 |
        | bar      | ERROR   | LOG_MESSAGE_4 |
    And the file "behave.log" should contain:
        """
        LOGFILE.ERROR -- root: LOG_MESSAGE_1
        LOGFILE.WARNING -- foo: LOG_MESSAGE_2
        LOGFILE.INFO -- foo.bar: LOG_MESSAGE_3
        LOGFILE.ERROR -- bar: LOG_MESSAGE_4
        """
    But note that "log-file and log-console can use different log-formats"
    And the command output should contain:
        """
        LOG.ERROR -- root: LOG_MESSAGE_1
        LOG.WARNING -- foo: LOG_MESSAGE_2
        LOG.INFO -- foo.bar: LOG_MESSAGE_3
        LOG.ERROR -- bar: LOG_MESSAGE_4
        """

  Scenario: Log records for filtered-out log categories appear in log-file
    Given a file named "features/log_records_then_fails.feature" with:
        """
        Feature:
          Scenario: Failing
            Given I create log records with:
              | category | level   | message |
              | root     | ERROR   | LOG_MESSAGE_1 |
              | foo      | WARNING | LOG_MESSAGE_2 |
              | foo.bar  | INFO    | LOG_MESSAGE_3 |
              | bar      | ERROR   | LOG_MESSAGE_4 |
            When another step fails
        """
    When I run "behave -f plain --logging-filter=-bar features/log_records_then_fails.feature"
    Then it should fail
    And the command output should contain the following log records:
        | category | level   | message       |
        | root     | ERROR   | LOG_MESSAGE_1 |
        | foo      | WARNING | LOG_MESSAGE_2 |
        | foo.bar  | INFO    | LOG_MESSAGE_3 |
    And the command output should not contain the following log records:
        | category | level | message       | Comment |
        | bar      | ERROR | LOG_MESSAGE_4 | EXCLUDED from log-capture |
    But the file "behave.log" should contain:
        """
        LOGFILE.ERROR -- root: LOG_MESSAGE_1
        LOGFILE.WARNING -- foo: LOG_MESSAGE_2
        LOGFILE.INFO -- foo.bar: LOG_MESSAGE_3
        LOGFILE.ERROR -- bar: LOG_MESSAGE_4
        """
    But note that "log-file and log-console can use different log-formats"
    And the command output should contain:
        """
        LOG.ERROR -- root: LOG_MESSAGE_1
        LOG.WARNING -- foo: LOG_MESSAGE_2
        LOG.INFO -- foo.bar: LOG_MESSAGE_3
        """

  Scenario: Log records for passing/failing steps appear in log-file (2 Scenarios)
    Given a file named "features/log_records_with_passes_and_fails.feature" with:
        """
        Feature: Log Records and Passing/Failing
          Scenario: Passing
            Given I create log records with:
              | category | level   | message |
              | root     | ERROR   | LOG_MESSAGE_1 |
              | foo      | WARNING | LOG_MESSAGE_2 |
            When another step passes

          Scenario: Failing
            Given I create log records with:
              | category | level   | message |
              | other    | INFO    | LOG_MESSAGE_3 |
            When another step fails
        """
    When I run "behave -f plain features/log_records_with_passes_and_fails.feature"
    Then it should fail
    And the command output should not contain the following log records:
        | category | level   | message       |
        | root     | ERROR   | LOG_MESSAGE_1 |
        | foo      | WARNING | LOG_MESSAGE_2 |
    And the command output should contain the following log records:
        | category | level   | message       |
        | other    | INFO    | LOG_MESSAGE_3 |
    But the file "behave.log" should contain:
        """
        LOGFILE.ERROR -- root: LOG_MESSAGE_1
        LOGFILE.WARNING -- foo: LOG_MESSAGE_2
        LOGFILE.INFO -- other: LOG_MESSAGE_3
        """

  Scenario: Log records for failing/passing steps appear in log-file (2 Features)
    Given a file named "features/log_records1.failing.feature" with:
        """
        Feature: Log Records and Failing 1
          Scenario: A
            Given I create log records with:
              | category | level   | message |
              | root     | ERROR   | LOG_MESSAGE_1 |
              | foo      | WARNING | LOG_MESSAGE_2 |
            When another step fails
        """
    And a file named "features/log_records2.passeing.feature" with:
        """
        Feature: Log Records and Passing 2
          Scenario: B
            Given I create log records with:
              | category | level   | message |
              | other2   | INFO    | LOG_MESSAGE_3 |
            When another step passes
        """
    When I run "behave -f plain features"
    Then it should fail
    And the command output should contain the following log records:
        | category | level   | message       |
        | root     | ERROR   | LOG_MESSAGE_1 |
        | foo      | WARNING | LOG_MESSAGE_2 |
    And the command output should not contain the following log records:
        | category | level   | message       |
        | other2   | INFO  | LOG_MESSAGE_3 |
    But the file "behave.log" should contain:
        """
        LOGFILE.ERROR -- root: LOG_MESSAGE_1
        LOGFILE.WARNING -- foo: LOG_MESSAGE_2
        LOGFILE.INFO -- other2: LOG_MESSAGE_3
        """

