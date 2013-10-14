Feature: Setup logging_format

  As a tester
  I want to configure the logging_format for log_capture mode
  So that log-records are shown in my preferred format.

  As a tester
  I want to configure the logging_format for logging mode (no-log_capture)
  So that log-records are shown in my preferred format.

  | SPECIFICATION:
  |  * logging_format can be defined on command-line
  |  * logging_format can be defined in behave configuration file
  |
  | NOTE:
  |  The log record format can also be defined in a logging configuration file.

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
            context.config.setup_logging()
        """
    And  a file named "features/example.log_and_fail.feature" with:
        """
        Feature:
          Scenario: Failing
            Given I create log records with:
                | category | level   | message |
                | root     |  ERROR  | Hello Alice |
                | root     |  WARN   | Hello Bob   |
            When a step fails
        """

  @capture
  Scenario: Use logging_format on command-line (case: log_capture mode)
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = true
        logging_level = WARN
        """
    When I run "behave -f plain -T --logging-format='LOG.%(levelname)-8s  %(name)-10s: %(message)s' features/"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain "Captured logging:"
    And the command output should contain:
        """
        Captured logging:
        LOG.ERROR     root      : Hello Alice
        LOG.WARNING   root      : Hello Bob
        """
    When I use the log record configuration:
        | property | value |
        | format   | LOG.%(levelname)-8s  %(name)-10s: %(message)s |
    Then the command output should contain the following log records:
        | category | level   | message |
        | root     |  ERROR  | Hello Alice |
        | root     |  WARN   | Hello Bob   |


  @capture
  Scenario: Use logging_format in config-file (case: log_capture mode)
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = true
        logging_level = WARN
        logging_format = LOG.%(levelname)-8s  %(name)-10s: %(message)s
        """
    When I run "behave -f plain features/"
    Then it should fail
    And the command output should contain "Captured logging:"
    And the command output should contain:
        """
        Captured logging:
        LOG.ERROR     root      : Hello Alice
        LOG.WARNING   root      : Hello Bob
        """

  @no_capture
  Scenario: Use logging_format on command-line (case: logging mode)
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = false
        logging_level = WARN
        """
    When I run "behave -f plain -T --logging-format='LOG.%(levelname)-8s  %(name)-10s: %(message)s' features/"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should not contain "Captured logging:"
    And the command output should contain:
        """
        LOG.ERROR     root      : Hello Alice
        LOG.WARNING   root      : Hello Bob
        """
    When I use the log record configuration:
        | property | value |
        | format   | LOG.%(levelname)-8s  %(name)-10s: %(message)s |
    Then the command output should contain the following log records:
        | category | level   | message |
        | root     |  ERROR  | Hello Alice |
        | root     |  WARN   | Hello Bob   |


  @no_capture
  Scenario: Use logging_format in config-file (case: logging mode)
    Given a file named "behave.ini" with:
        """
        [behave]
        log_capture = false
        logging_level = WARN
        logging_format = LOG.%(levelname)-8s  %(name)-10s: %(message)s
        """
    When I run "behave -f plain features/"
    Then it should fail
    And the command output should not contain "Captured logging:"
    And the command output should contain:
        """
        LOG.ERROR     root      : Hello Alice
        LOG.WARNING   root      : Hello Bob
        """

  @capture
  Scenario: Use logging_datefmt in config-file

    Ensure that "logging_datefmt" option can be used.

    Given a file named "behave.ini" with:
        """
        [behave]
        logging_format = %(asctime)s  LOG.%(levelname)-8s %(name)s: %(message)s
        logging_datefmt = %Y-%m-%dT%H:%M:%S
        """
    When I run "behave -f plain features/"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain "LOG.ERROR    root: Hello Alice"
    And the command output should contain "LOG.WARNING  root: Hello Bob"
