@wip
Feature: Setup logging subsystem by using a logging configfile

  As a tester
  I want to setup the logging subsystem by using a configfile
  To be more flexible even in complex situations

  @setup
  Scenario: Feature setup
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.log.steps
        import behave4cmd0.failing_steps
        import behave4cmd0.passing_steps
        """
    And a file named "features/example.log_and_pass.feature" with:
        """
        Feature:
          Scenario: Passing
            Given I create log records with:
              | category | level | message |
              | root     | FATAL | Hello Alice  |
              | foo      | ERROR | Hello Bob    |
              | foo.bar  | WARN  | Hello Charly |
              | bar      | INFO  | Hello Dora   |
              | baz      | DEBUG | Hello Emily  |
            And another step passes
        """
    And a file named "features/example.log_and_fail.feature" with:
        """
        Feature:
          Scenario: Failing
            Given I create log records with:
              | category | level | message |
              | root     | FATAL | Hello Alice  |
              | foo      | ERROR | Hello Bob    |
              | foo.bar  | WARN  | Hello Charly |
              | bar      | INFO  | Hello Dora   |
              | baz      | DEBUG | Hello Emily  |
            And another step fails
        """
    And a file named "behave.ini" with:
        """
        [behave]
        log_capture = false
        logging_level = DEBUG
        logging_format = LOG.%(levelname)-8s  %(name)-10s: %(message)s
        """
    And a file named "behave_logging.ini" with:
        """
        [loggers]
        keys=root

        [handlers]
        keys=Console,File

        [formatters]
        keys=Brief

        [logger_root]
        level = NOTSET
        handlers = File
        # handlers = Console,File

        [handler_File]
        class=FileHandler
        args=("behave.log", 'w')
        level=NOTSET
        formatter=Brief

        [handler_Console]
        class=StreamHandler
        args=(sys.stderr,)
        level=NOTSET
        formatter=Brief

        [formatter_Brief]
        format= LOG.%(levelname)-8s  %(name)-10s: %(message)s
        datefmt=
        """

  Scenario: Setup logging subsystem via environment (case: logging mode)
    Given a file named "features/environment.py" with:
        """
        def before_all(context):
            context.config.setup_logging(configfile="behave_logging.ini")
        """
    And I use the log record configuration:
        | property | value |
        | format   | LOG.%(levelname)-8s  %(name)-10s: %(message)s |
    When I run "behave -f plain features/example.log_and_pass.feature"
    Then it should pass
    And the file "behave.log" should contain the log records:
        | category | level | message |
        | root     | FATAL | Hello Alice  |
        | foo      | ERROR | Hello Bob    |
        | foo.bar  | WARN  | Hello Charly |
        | bar      | INFO  | Hello Dora   |
        | baz      | DEBUG | Hello Emily  |
    And the command output should not contain the following log records:
        | category | level | message |
        | root     | FATAL | Hello Alice  |
        | foo      | ERROR | Hello Bob    |
        | foo.bar  | WARN  | Hello Charly |
        | bar      | INFO  | Hello Dora   |
        | baz      | DEBUG | Hello Emily  |


  Scenario: Setup logging subsystem via environment (case: log-capture mode)
    Given a file named "features/environment.py" with:
        """
        def before_all(context):
            context.config.setup_logging(configfile="behave_logging.ini")
        """
    And I use the log record configuration:
        | property | value |
        | format   | LOG.%(levelname)-8s  %(name)-10s: %(message)s |
    When I run "behave -f plain --logcapture features/example.log_and_fail.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
    And the file "behave.log" should contain the log records:
        | category | level | message |
        | root     | FATAL | Hello Alice  |
        | foo      | ERROR | Hello Bob    |
        | foo.bar  | WARN  | Hello Charly |
        | bar      | INFO  | Hello Dora   |
        | baz      | DEBUG | Hello Emily  |
    And the command output should contain the following log records:
        | category | level | message |
        | root     | FATAL | Hello Alice  |
        | foo      | ERROR | Hello Bob    |
        | foo.bar  | WARN  | Hello Charly |
        | bar      | INFO  | Hello Dora   |
        | baz      | DEBUG | Hello Emily  |
