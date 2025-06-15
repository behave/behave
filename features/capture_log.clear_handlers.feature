@logging
@capture
Feature: Use --logging-clear-handlers configuration option

  PRECONDITION: capture_log mode is enabled (config.capture_log = true).

  As a tester
  In log-capture mode
  I want sometimes to remove any logging handler before capture starts
  So that I have the log-records output under control.


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
        import logging

        def before_all(context):
            # -- SIMILAR TO: context.config.setup_logging()
            # -- INITIAL LOG-HANDLER: Which will be cleared.
            format = "INITIAL_LOG_HANDLER: %(name)s %(levelname)s: %(message)s;"
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(format))
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(context.config.logging_level)
        """
    And  a file named "features/example.log_with_failure.feature" with:
        """
        Feature:
          Scenario: Failing
            Given I create log records with:
                | category | level   | message |
                | root     |  ERROR  | Hello Alice  |
                | root     |  WARN   | Hello Bob    |
            When a step fails
        """


  Scenario: Use logcapture mode without clearing existing log handlers
    Given a file named "behave.ini" with:
        """
        [behave]
        capture_log = true
        logging_level = WARN
        logging_format = LOG_%(levelname)s:%(name)s: %(message)s
        """
    And I use "LOG_%(levelname)s:%(name)s: %(message)s" as log record format
    When I run "behave -f plain features/example.log_with_failure.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped
        """
    And the command output should contain:
        """
        CAPTURED LOG: scenario
        LOG_ERROR:root: Hello Alice
        LOG_WARNING:root: Hello Bob
        """
    And the command output should contain:
        """
        INITIAL_LOG_HANDLER: root ERROR: Hello Alice;
        INITIAL_LOG_HANDLER: root WARNING: Hello Bob;
        """


  Scenario: Use logcapture mode with clearing additional log handlers (case: command-line)
    Given a file named "behave.ini" with:
        """
        [behave]
        capture_log = true
        logging_level = WARN
        logging_format = LOG_%(levelname)s:%(name)s: %(message)s
        """
    And I use "LOG_%(levelname)s:%(name)s: %(message)s" as log record format
    When I run "behave -f plain --logging-clear-handlers features/example.log_with_failure.feature"
    Then it should fail with:
        """
        CAPTURED LOG: scenario
        LOG_ERROR:root: Hello Alice
        LOG_WARNING:root: Hello Bob
        """
    But the command output should not contain:
        """
        INITIAL_LOG_HANDLER: root ERROR: Hello Alice;
        INITIAL_LOG_HANDLER: root WARNING: Hello Bob;
        """


  Scenario: Use Logcapture mode with clearing additional log handlers (case: configfile)
    Given a file named "behave.ini" with:
        """
        [behave]
        capture_log = true
        logging_level = WARN
        logging_format = LOG_%(levelname)s:%(name)s: %(message)s
        logging_clear_handlers = true
        """
    When I run "behave -f plain features/example.log_with_failure.feature"
    Then it should fail with:
        """
        CAPTURED LOG: scenario
        LOG_ERROR:root: Hello Alice
        LOG_WARNING:root: Hello Bob
        """
    But the command output should not contain:
        """
        INITIAL_LOG_HANDLER: root ERROR: Hello Alice;
        INITIAL_LOG_HANDLER: root WARNING: Hello Bob;
        """
