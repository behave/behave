@issue
@use.with_python.min_version=3.2
Feature: Issue #948 -- Add support for value substitution in logging config file

  . SYNDROME:
  . context.config.setup_logging(configfile=..., defaults={...})
  . does not pass param "defaults" to "logging.config.fileConfig()"

  Background: Setup
    Given a new working directory
    And a file named "behave.ini" with:
        """
        # -- REQUIRES: Python >= 3.2 -- f-string log-format style.
        [behave]
        capture_log = true
        logging_level = INFO
        """
    And a file named "logging.ini" with:
        """
        [loggers]
        keys: root

        [handlers]
        keys: File

        [formatters]
        keys: standard

        [logger_root]
        handlers: File
        level: NOTSET

        # -- USING PLACEHOLDER FROM: defaults
        [handler_File]
        class: FileHandler
        level: NOTSET
        formatter: standard
        args=("%(log_file_path)s", 'w')
        # DISABLED: args=("behave4me.log", 'w')

        [formatter_standard]
        format: LOGFILE.%(levelname)s -- %(name)s: %(message)s
        datefmt:
        """
    And a file named "features/steps/use_step_library.py" with:
      """
      import behave4cmd0.passing_steps
      import behave4cmd0.failing_steps
      import behave4cmd0.log_steps
      """
    And a file named "features/log_and_pass.feature" with:
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
    And a file named "features/log_and_fail.feature" with:
        """
        Feature:
          Scenario: Log Records and Failing
            Given I create log records with:
              | category | level   | message |
              | root     | ERROR   | LOG_MESSAGE_1 |
              | foo      | WARNING | LOG_MESSAGE_2 |
              | foo.bar  | INFO    | LOG_MESSAGE_3 |
              | bar      | ERROR   | LOG_MESSAGE_4 |
            When another step fails
        """

  Scenario Outline: Check Syndrome -- outcome: <outcome>
    Given a file named "features/environment.py" with:
      """
      def before_all(context):
          defaults = dict(log_file_path="behave4me.log")
          context.config.setup_logging(configfile="logging.ini", defaults=defaults)
      """
    When I run "behave features/log_and_<outcome>.feature"
    Then it should <outcome>
    Then the file named "behave4me.log" exists
    And the file "behave4me.log" should contain:
      """
      LOGFILE.ERROR -- root: LOG_MESSAGE_1
      LOGFILE.WARNING -- foo: LOG_MESSAGE_2
      LOGFILE.INFO -- foo.bar: LOG_MESSAGE_3
      LOGFILE.ERROR -- bar: LOG_MESSAGE_4
      """

    Examples:
      | outcome |
      | pass    |
      | fail    |
