@logging
@capture
Feature: Use --logging-clear-handlers configuration option

  PRECONDITION: log_capture mode is enabled (config.log_capture = true).

  As a tester
  In log-capture mode
  I want sometimes to remove any logging handler before capture starts
  So that I have the log-records output under control.


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
        def before_all(context):
            # -- SAME-AS: context.config.setup_logging()
            import logging
            logging.basicConfig(level=context.config.logging_level)

            # -- ADDITIONAL LOG-HANDLER: Which will be cleared.
            format = "LOG-HANDLER2: %(name)s %(levelname)s: %(message)s;"
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(format))
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
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
        log_capture = true
        logging_level = WARN
        """
    When I run "behave -f plain features/example.log_with_failure.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Captured logging:
        ERROR:root:Hello Alice
        WARNING:root:Hello Bob
        """
    And the command output should contain:
        """
        LOG-HANDLER2: root ERROR: Hello Alice;
        LOG-HANDLER2: root WARNING: Hello Bob;
        """


  Scenario: Use logcapture mode with clearing additional log handlers (case: command-line)
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = true
        logging_level = WARN
        """
    When I run "behave -f plain --logging-clear-handlers features/example.log_with_failure.feature"
    Then it should fail with:
        """
        Captured logging:
        ERROR:root:Hello Alice
        WARNING:root:Hello Bob
        """
    But the command output should not contain:
        """
        LOG-HANDLER2: root ERROR: Hello Alice;
        LOG-HANDLER2: root WARNING: Hello Bob;
        """


  Scenario: Use Logcapture mode with clearing additional log handlers (case: configfile)
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = true
        logging_level = WARN
        logging_clear_handlers = true
        """
    When I run "behave -f plain features/example.log_with_failure.feature"
    Then it should fail with:
        """
        Captured logging:
        ERROR:root:Hello Alice
        WARNING:root:Hello Bob
        """
    But the command output should not contain:
        """
        LOG-HANDLER2: root ERROR: Hello Alice;
        LOG-HANDLER2: root WARNING: Hello Bob;
        """
