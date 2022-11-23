Feature: Help Formatter

  As a tester
  I want to know which formatters are supported
  To be able to select one.

  . SPECIFICATION: Using "behave --format=help" on command line
  .   * Shows list of available formatters with their name and description
  .   * Good formatters / formatter-aliases are shown in "AVAILABLE FORMATTERS" section
  .   * Bad formatter-aliases are shown in "UNAVAILABLE FORMATTERS" section
  .   * Bad formatter syndromes are: ModuleNotFoundError, ClassNotFoundError, InvalidClassError
  .
  . FORMATTER ALIASES:
  .   * You can specify formatter-aliases for user-defined formatter classes
  .     under the section "[behave.formatters]" in the config-file.

  Background:
    Given a new working directory

  Rule: Good Formatters are shown in "AVAILABLE FORMATTERS" Section
    Scenario: Good case (with builtin formatters)
      Given an empty file named "behave.ini"
      When I run "behave --format=help"
      Then it should pass
      And the command output should contain:
        """
        AVAILABLE FORMATTERS:
          json           JSON dump of test run
          json.pretty    JSON dump of test run (human readable)
          null           Provides formatter that does not output anything.
          plain          Very basic formatter with maximum compatibility
          pretty         Standard colourised pretty formatter
          progress       Shows dotted progress for each executed scenario.
          progress2      Shows dotted progress for each executed step.
          progress3      Shows detailed progress for each step of a scenario.
          rerun          Emits scenario file locations of failing scenarios
          sphinx.steps   Generate sphinx-based documentation for step definitions.
          steps          Shows step definitions (step implementations).
          steps.catalog  Shows non-technical documentation for step definitions.
          steps.doc      Shows documentation for step definitions.
          steps.usage    Shows how step definitions are used by steps.
          tags           Shows tags (and how often they are used).
          tags.location  Shows tags and the location where they are used.
        """

    Scenario: Good Formatter by using a Formatter-Alias
      Given an empty file named "behave4me/__init__.py"
      And a file named "behave4me/good_formatter.py" with:
        """
        from behave.formatter.base import Formatter

        class SomeFormatter(Formatter):
            name = "some"
            description = "Very basic formatter for Some format."

            def __init__(self, stream_opener, config):
                super(SomeFormatter, self).__init__(stream_opener, config)
        """
      And a file named "behave.ini" with:
        """
        [behave.formatters]
        some = behave4me.good_formatter:SomeFormatter
        """
      When I run "behave --format=help"
      Then it should pass
      And the command output should contain:
        """
        rerun          Emits scenario file locations of failing scenarios
        some           Very basic formatter for Some format.
        sphinx.steps   Generate sphinx-based documentation for step definitions.
        """
      And note that "the new formatter appears in the sorted list of formatters"
      But the command output should not contain "UNAVAILABLE FORMATTERS"


  Rule: Bad Formatters are shown in "UNAVAILABLE FORMATTERS" Section

    HINT ON SYNDROME: ModuleNotFoundError
      The config-file "behave.ini" may contain formatter-aliases
      that refer to missing/not-installed Python packages.

    Background:
      Given an empty file named "behave4me/__init__.py"
      And a file named "behave4me/bad_formatter.py" with:
        """
        class InvalidFormatter1(object): pass    # CASE 1: Not a subclass-of Formatter
        InvalidFormatter2 = True                 # CASE 2: Not a class
        """

    @<formatter_name> @formatter.syndrome.<formatter_syndrome>
    Scenario Template: Bad Formatter with <formatter_syndrome>
      Given a file named "behave.ini" with:
        """
        [behave.formatters]
        <formatter_name> = <formatter_class>
        """
      When I run "behave --format=help"
      Then it should pass
      And the command output should contain:
        """
        UNAVAILABLE FORMATTERS:
          <formatter_name>  <formatter_syndrome>: <problem_description>
        """

      @use.with_python.min_version=3.6
      Examples: For Python >= 3.6
        | formatter_name | formatter_class                           | formatter_syndrome  | problem_description |
        | bad_formatter1 | behave4me.unknown:Formatter               | ModuleNotFoundError | No module named 'behave4me.unknown' |

      @not.with_python.min_version=3.6
      Examples: For Python < 3.6
        | formatter_name | formatter_class                           | formatter_syndrome  | problem_description |
        | bad_formatter1 | behave4me.unknown:Formatter               | ModuleNotFoundError | No module named 'unknown' |

      Examples:
        | formatter_name | formatter_class                           | formatter_syndrome  | problem_description |
        | bad_formatter2 | behave4me.bad_formatter:UnknownFormatter  | ClassNotFoundError  | behave4me.bad_formatter:UnknownFormatter |
        | bad_formatter3 | behave4me.bad_formatter:InvalidFormatter1 | InvalidClassError   | is not a subclass-of Formatter |
        | bad_formatter4 | behave4me.bad_formatter:InvalidFormatter2 | InvalidClassError   | is not a class |


    Scenario: Multiple Bad Formatters
      Given a file named "behave.ini" with:
        """
        [behave.formatters]
        bad_formatter2 = behave4me.bad_formatter:UnknownFormatter
        bad_formatter3 = behave4me.bad_formatter:InvalidFormatter1
        """
      When I run "behave --format=help"
      Then it should pass
      And the command output should contain:
        """
        UNAVAILABLE FORMATTERS:
          bad_formatter2  ClassNotFoundError: behave4me.bad_formatter:UnknownFormatter
          bad_formatter3  InvalidClassError: is not a subclass-of Formatter
        """
      And note that "the list of UNAVAILABLE FORMATTERS is sorted-by-name"
