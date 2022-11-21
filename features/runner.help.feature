Feature: Runner Help

  As a tester
  I want to know which test runner classes are supported
  To be able to select one.

  . SPECIFICATION: Using "behave --runner=help" on command line
  .   * Shows list of available test runner classes
  .   * Good test runner-aliases are shown in "AVAILABLE RUNNERS" section
  .   * Bad test runner-aliases are shown in "UNAVAILABLE RUNNERS" section
  .   * Bad test runner syndromes are:
  .     ModuleNotFoundError, ClassNotFoundError, InvalidClassError
  .
  . TEST RUNNER ALIASES:
  .   * You can specify runner-aliases for user-defined test runner classes
  .     under the section "[behave.runners]" in the config-file.

  Background:
    Given a new working directory

  Rule: Good Runners are shown in "AVAILABLE RUNNERS" Section

    Scenario: Good case (with builtin runners)
      Given an empty file named "behave.ini"
      When I run "behave --runner=help"
      Then it should pass
      And the command output should contain:
        """
        AVAILABLE RUNNERS:
          default  = behave.runner:Runner
        """

    Scenario: Good Runner by using a Runner-Alias
      Given an empty file named "behave4me/__init__.py"
      And a file named "behave4me/good_runner.py" with:
        """
        from behave.api.runner import ITestRunner
        from behave.runner import Runner as CoreRunner

        class SomeRunner(ITestRunner):
            def __init__(self, config, **kwargs):
                super(ITestRunner, self).__init__(config)
                self.config = config
                self._runner = CoreRunner(config)

            def run(self):
                return self._runner.run()
        """
      And a file named "behave.ini" with:
        """
        [behave.runners]
        some = behave4me.good_runner:SomeRunner
        """
      When I run "behave --runner=help"
      Then it should pass
      And the command output should contain:
        """
        default  = behave.runner:Runner
        some     = behave4me.good_runner:SomeRunner
        """
      And note that "the new runner appears in the sorted list of runners"
      But the command output should not contain "UNAVAILABLE RUNNERS"


  Rule: Bad Runners are shown in "UNAVAILABLE RUNNERS" Section

    HINT ON SYNDROME: ModuleNotFoundError
      The config-file "behave.ini" may contain runner-aliases
      that refer to missing/not-installed Python packages.

    Background:
      Given an empty file named "behave4me/__init__.py"
      And a file named "behave4me/bad_runner.py" with:
        """
        class InvalidRunner1(object): pass    # CASE 1: Not a subclass-of ITestRunner
        InvalidRunner2 = True                 # CASE 2: Not a class
        """

    @<runner_name> @runner.syndrome.<runner_syndrome>
    Scenario Template: Bad Runner with <runner_syndrome>
      Given a file named "behave.ini" with:
        """
        [behave.runners]
        <runner_name> = <runner_class>
        """
      When I run "behave --runner=help"
      Then it should pass
      And the command output should contain:
        """
        UNAVAILABLE RUNNERS:
          <runner_name>    <runner_syndrome>: <problem_description>
        """

      @use.with_python.min_version=3.0
      Examples: For Python >= 3.0
        | runner_name | runner_class                           | runner_syndrome  | problem_description |
        | bad_runner1 | behave4me.unknown:Runner               | ModuleNotFoundError | No module named 'behave4me.unknown' |

      @not.with_python.min_version=3.0
      Examples: For Python < 3.0
        | runner_name | runner_class                           | runner_syndrome  | problem_description |
        | bad_runner1 | behave4me.unknown:Runner               | ModuleNotFoundError | No module named 'unknown' |

      Examples:
        | runner_name | runner_class                           | runner_syndrome  | problem_description |
        | bad_runner2 | behave4me.bad_runner:UnknownRunner  | ClassNotFoundError  | behave4me.bad_runner:UnknownRunner |
        | bad_runner3 | behave4me.bad_runner:InvalidRunner1 | InvalidClassError   | is not a subclass-of 'behave.api.runner:ITestRunner' |
        | bad_runner4 | behave4me.bad_runner:InvalidRunner2 | InvalidClassError   | is not a class |


    Scenario: Multiple Bad Runners
      Given a file named "behave.ini" with:
        """
        [behave.runners]
        bad_runner3 = behave4me.bad_runner:InvalidRunner1
        bad_runner2 = behave4me.bad_runner:UnknownRunner
        """
      When I run "behave --runner=help"
      Then it should pass
      And the command output should contain:
        """
        UNAVAILABLE RUNNERS:
          bad_runner2    ClassNotFoundError: behave4me.bad_runner:UnknownRunner
          bad_runner3    InvalidClassError: is not a subclass-of 'behave.api.runner:ITestRunner'
        """
      And note that "the list of UNAVAILABLE RUNNERS is sorted-by-name"
