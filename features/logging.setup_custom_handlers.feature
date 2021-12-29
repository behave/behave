Feature: Setup logging with custom handlers

  As a tester
  I want to configure custom logging handlers to obtain loggers
  of different granularity in log-files and console.

  As a tester
  I want to control the logging level of all handlers individually,
  including the level of the log-capture and the console handler.

  . SPECIFICATION:
  .  * logging_level can be defined on command-line
  .  * logging_level can be defined in behave configuration file
  .  * the configured logging_level defines the level of captured logs in --logcapture mode
  .  * the configured logging_level defines the level of console logs in --nologcapture mode
  .  * the level of other handlers is not influenced by the configured logging_level


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log.steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """
    And a file named "features/environment.py" with:
        """
        import logging

        def before_all(context):
            formatter = logging.Formatter(context.config.logging_format)
            root_logger = logging.getLogger()

            # unset root logger level to allow for all custom handler levels
            root_logger.setLevel(logging.NOTSET)

            # add file handler with DEBUG level
            debug_handler = logging.FileHandler('debug.log', mode='w')
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            root_logger.addHandler(debug_handler)

            # add file handler with INFO level
            debug_handler = logging.FileHandler('info.log', mode='w')
            debug_handler.setLevel(logging.INFO)
            debug_handler.setFormatter(formatter)
            root_logger.addHandler(debug_handler)

            # add console handler in non-capture mode, with configured level
            if not context.config.log_capture:
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(context.config.logging_level)
                stream_handler.setFormatter(formatter)
                root_logger.addHandler(stream_handler)

        """
    And  a file named "features/example.log_with_failure.feature" with:
        """
        Feature:
          Scenario: S1
            Given I create log records with:
                | category | level   | message                 |
                | root     |  ERROR  | Hello1 log-error-record |
                | root     |  WARN   | Hello1 log-warn-record  |
                | root     |  INFO   | Hello1 log-info-record  |
                | root     |  DEBUG  | Hello1 log-debug-record |
            When a step fails
        """
    And  a file named "features/example.log_with_pass.feature" with:
        """
        Feature:
          Scenario: S2
            Given I create log records with:
                | category | level   | message                 |
                | root     |  ERROR  | Hello2 log-error-record |
                | root     |  WARN   | Hello2 log-warn-record  |
                | root     |  INFO   | Hello2 log-info-record  |
                | root     |  DEBUG  | Hello2 log-debug-record |
            When a step passes
        """


  @capture
  Scenario: Logcapture mode: ensure that logfile has debug level logs
    Given a file named "behave.ini" with:
        """
        [behave]
        logging_level = ERROR
        """
    When I run "behave -f plain -T features/"
    Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Captured logging:
        ERROR:root:Hello1 log-error-record
        """
    But the command output should not contain the following log records:
        | category | level   | message                 | Comment           |
        | root     |  WARN   | Hello1 log-warn-record  | Log-level too low |
        | root     |  INFO   | Hello1 log-info-record  | Log-level too low |
        | root     |  DEBUG  | Hello1 log-debug-record | Log-level too low |
        | root     |  ERROR  | Hello2 log-error-record | Scenario passes   |
        | root     |  WARN   | Hello2 log-warn-record  | Scenario passes   |
        | root     |  INFO   | Hello2 log-info-record  | Scenario passes   |
        | root     |  DEBUG  | Hello2 log-debug-record | Scenario passes   |
    And the file "debug.log" should contain the log records:
        | category | level   | message                 |
        | root     |  WARN   | Hello1 log-warn-record  |
        | root     |  INFO   | Hello1 log-info-record  |
        | root     |  DEBUG  | Hello1 log-debug-record |
        | root     |  ERROR  | Hello2 log-error-record |
        | root     |  WARN   | Hello2 log-warn-record  |
        | root     |  INFO   | Hello2 log-info-record  |
        | root     |  DEBUG  | Hello2 log-debug-record |
    And the file "info.log" should contain the log records:
        | category | level   | message                 |
        | root     |  WARN   | Hello1 log-warn-record  |
        | root     |  INFO   | Hello1 log-info-record  |
        | root     |  ERROR  | Hello2 log-error-record |
        | root     |  WARN   | Hello2 log-warn-record  |
        | root     |  INFO   | Hello2 log-info-record  |
    But the file "info.log" should not contain the log records:
        | category | level   | message                 | Comment           |
        | root     |  DEBUG  | Hello1 log-debug-record | Log-level too low |
        | root     |  DEBUG  | Hello2 log-debug-record | Log-level too low |


  @no_capture
  Scenario: Normal mode: ensure that logfile has debug level logs
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = false
        logging_level = ERROR
        """
      When I run "behave -f plain -T features/"
      Then it should fail with:
        """
        1 scenario passed, 1 failed, 0 skipped
        3 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain the following log records:
        | category | level   | message |
        | root     |  ERROR  | Hello1 log-error-record |
        | root     |  ERROR  | Hello2 log-error-record |
    But the command output should not contain the following log records:
        | category | level   | message                 | Comment           |
        | root     |  WARN   | Hello1 log-warn-record  | Log-level too low |
        | root     |  INFO   | Hello1 log-info-record  | Same reason       |
        | root     |  DEBUG  | Hello1 log-debug-record | Same reason       |
        | root     |  WARN   | Hello2 log-warn-record  | Same reason       |
        | root     |  INFO   | Hello2 log-info-record  | Same reason       |
        | root     |  DEBUG  | Hello2 log-debug-record | Same reason       |
    And the file "debug.log" should contain the log records:
        | category | level   | message                 |
        | root     |  WARN   | Hello1 log-warn-record  |
        | root     |  INFO   | Hello1 log-info-record  |
        | root     |  DEBUG  | Hello1 log-debug-record |
        | root     |  ERROR  | Hello2 log-error-record |
        | root     |  WARN   | Hello2 log-warn-record  |
        | root     |  INFO   | Hello2 log-info-record  |
        | root     |  DEBUG  | Hello2 log-debug-record |
    And the file "info.log" should contain the log records:
        | category | level   | message                 |
        | root     |  WARN   | Hello1 log-warn-record  |
        | root     |  INFO   | Hello1 log-info-record  |
        | root     |  ERROR  | Hello2 log-error-record |
        | root     |  WARN   | Hello2 log-warn-record  |
        | root     |  INFO   | Hello2 log-info-record  |
    But the file "info.log" should not contain the log records:
        | category | level   | message                 | Comment           |
        | root     |  DEBUG  | Hello1 log-debug-record | Log-level too low |
        | root     |  DEBUG  | Hello2 log-debug-record | Log-level too low |
