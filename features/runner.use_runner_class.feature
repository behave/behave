Feature: User-provided Test Runner Class (extension-point)

  As a user/developer
  I want sometimes replace behave's default runner with an own runner class
  So that I easily support special use cases where a different test runner is needed.

  . NOTES:
  .  * This extension-point was already available internally
  .  * Now you can specify the runner_class in the config-file
  .    or as a command-line option.


  Background:
    Given a new working directory
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
        """
        import behave4cmd0.passing_steps
        import behave4cmd0.failing_steps
        """
     And a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function

        def before_all(ctx):
            print_test_runner_class(ctx._runner)

        def print_test_runner_class(runner):
            print("TEST_RUNNER_CLASS=%s::%s" % (runner.__class__.__module__,
                                           runner.__class__.__name__))
        """
#    And a file named "features/environment.py" with:
#        """
#        from __future__ import print_function
#        import os
#
#        def print_environment(pattern=None):
#            names = ["PYTHONPATH", "PATH"]
#            for name in names:
#                value = os.environ.get(name, None)
#                print("DIAG: env: %s = %r" % (name, value))
#
#        def before_all(ctx):
#            print_environment()
#        """
    And a file named "features/passing.feature" with:
      """
      @pass
      Feature: Alice
        Scenario: A1
          Given a step passes
          When another step passes

        Scenario: A2
          When some step passes
      """


  @default_runner
  Rule: Use default runner

    Scenario: Use default runner
      Given a file named "behave.ini" does not exist
      When I run "behave features/"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        TEST_RUNNER_CLASS=behave.runner::Runner
        """
      And note that "the DEFAULT TEST_RUNNER CLASS is used"

    Scenario: Use default runner from config-file (case: ITestRunner subclass)
      Given a file named "behave_example1.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.api.runner import ITestRunner
        from behave.runner import Runner as CoreRunner

        class MyRunner(ITestRunner):
            def __init__(self, config, **kwargs):
                super(MyRunner, self).__init__(config)
                self._runner = CoreRunner(config)

            def run(self):
                print("THIS_RUNNER_CLASS=%s::%s" % (self.__class__.__module__,
                                                    self.__class__.__name__))
                return self._runner.run()

            @property
            def undefined_steps(self):
                return self._runner.undefined_steps
        """
      And a file named "behave.ini" with
        """
        [behave]
        runner = behave_example1:MyRunner
        """
      When I run "behave features/"
      Then it should pass with:
        """
        THIS_RUNNER_CLASS=behave_example1::MyRunner
        """
      And note that "my own TEST_RUNNER CLASS is used"

    Scenario: Use default runner from config-file (case: ITestRunner.register)
      Given a file named "behave_example2.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.runner import Runner as CoreRunner

        class MyRunner2(object):
            def __init__(self, config, **kwargs):
                self.config = config
                self._runner = CoreRunner(config)

            def run(self):
                print("THIS_RUNNER_CLASS=%s::%s" % (self.__class__.__module__,
                                                    self.__class__.__name__))
                return self._runner.run()

            @property
            def undefined_steps(self):
                return self._runner.undefined_steps

        # -- REGISTER AS TEST-RUNNER:
        from behave.api.runner import ITestRunner
        ITestRunner.register(MyRunner2)
        """
      And a file named "behave.ini" with
        """
        [behave]
        runner = behave_example2:MyRunner2
        """
      When I run "behave features/"
      Then it should pass with:
        """
        THIS_RUNNER_CLASS=behave_example2::MyRunner2
        """
      And note that "my own TEST_RUNNER CLASS is used"


    Scenario: Use default runner from config-file (using: runner-name)
      Given a file named "behave_example3.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.api.runner import ITestRunner
        from behave.runner import Runner as CoreRunner

        class MyRunner(ITestRunner):
            def __init__(self, config, **kwargs):
                super(MyRunner, self).__init__(config)
                self._runner = CoreRunner(config)

            def run(self):
                print("THIS_RUNNER_CLASS=%s::%s" % (self.__class__.__module__,
                                                    self.__class__.__name__))
                return self._runner.run()

            @property
            def undefined_steps(self):
                return self._runner.undefined_steps
        """
      And a file named "behave.ini" with
        """
        [behave]
        runner = some_runner

        [behave.runners]
        some_runner = behave_example3:MyRunner
        """
      When I run "behave features/"
      Then it should pass with:
        """
        THIS_RUNNER_CLASS=behave_example3::MyRunner
        """
      And note that "the runner-name/alias from the config-file was used"


  @own_runner
  Rule: Use own Test Runner (GOOD CASE)

    Scenario Template: Use --runner=NORMAL_<case> on command-line (without config-file)
      Given a file named "behave.ini" does not exist
      When I run "behave --runner=<runner_value> features"
      Then it should pass with:
        """
        TEST_RUNNER_CLASS=behave.runner::Runner
        """
      And note that "the NORMAL RUNNER CLASS is used"

      Examples:
        | case         | runner_value         |
        | RUNNER_NAME  | default              |
        | RUNNER_CLASS | behave.runner:Runner |


    Scenario: Use --runner=RUNNER_CLASS on command-line without config-file
      Given a file named "behave.ini" does not exist
      And a file named "behave_example/good_runner.py" with:
        """
        from __future__ import print_function
        from behave.runner import Runner

        class MyRunner1(Runner): pass
        """
      And an empty file named "behave_example/__init__.py"
      When I run "behave --runner=behave_example.good_runner:MyRunner1"
      Then it should pass with:
        """
        TEST_RUNNER_CLASS=behave_example.good_runner::MyRunner1
        """


    Scenario: Use --runner=RUNNER_NAME on command-line with config-file
      Given a file named "behave_example/good_runner.py" with:
        """
        from __future__ import print_function
        from behave.runner import Runner

        class MyRunner1(Runner): pass
        """
      And an empty file named "behave_example/__init__.py"
      And a file named "behave.ini" with:
        """
        [behave.runners]
        runner1 = behave_example.good_runner:MyRunner1
        """
      When I run "behave --runner=runner1 features"
      Then it should pass with:
        """
        TEST_RUNNER_CLASS=behave_example.good_runner::MyRunner1
        """

    Scenario: Runner option on command-line overrides config-file
      Given a file named "behave_example/good_runner.py" with:
        """
        from __future__ import print_function
        from behave.runner import Runner

        class MyRunner1(Runner): pass
        class MyRunner2(Runner): pass
        """
      And an empty file named "behave_example/__init__.py"
      Given a file named "behave.ini" with:
        """
        [behave]
        runner = behave_example.good_runner:MyRunner1
        """
      When I run "behave --runner=behave_example.good_runner:MyRunner2"
      Then it should pass with:
        """
        TEST_RUNNER_CLASS=behave_example.good_runner::MyRunner2
        """


  Rule: Use own Test Runner-by-Class (BAD CASES)

    Background: Bad runner classes
      Given a file named "behave_example/bad_runner.py" with:
        """
        from behave.api.runner import ITestRunner

        class NotRunner1(object): pass
        class NotRunner2(object):
            run = True

        CONSTANT_1 = 42

        def return_none(*args, **kwargs):
            return None
        """
      And a file named "behave_example/incomplete.py" with:
        """
        from behave.api.runner import ITestRunner

        class IncompleteRunner1(ITestRunner): # NO-CTOR
            def run(self): pass

            @property
            def undefined_steps(self):
                return []

        class IncompleteRunner2(ITestRunner): # NO-RUN-METHOD
            def __init__(self, config):
                self.config = config

            @property
            def undefined_steps(self):
                return []

        class IncompleteRunner3(ITestRunner): # MISSING: undefined_steps
            def __init__(self, config):
                self.config = config
            def run(self): pass

        class IncompleteRunner4(ITestRunner): # BAD-RUN-METHOD
            def __init__(self, config):
                self.config = config
            run = True

            @property
            def undefined_steps(self):
                return []
        """
      And an empty file named "behave_example/__init__.py"

    Scenario Template: Use BAD-RUNNER-CLASS with --runner=<runner_class> (<syndrome>)
      When I run "behave --runner=<runner_class>"
      Then it should fail
      And the command output should match:
        """
        <failure_message>
        """
      But note that "problem: <case>"

      Examples: BAD_CASE
        | syndrome         | runner_class                     | failure_message                                                          | case                                            |
        | UNKNOWN_MODULE   | unknown:Runner1                  | ModuleNotFoundError: No module named 'unknown'                           | Python module does not exist (or was not found) |
        | UNKNOWN_CLASS    | behave_example:UnknownClass      | ClassNotFoundError: behave_example:UnknownClass                                      | Runner class does not exist in module.          |
        | UNKNOWN_CLASS    | behave_example.bad_runner:42     | ClassNotFoundError: behave_example.bad_runner:42                                    | runner_class=number                             |
        | BAD_CLASS        | behave_example.bad_runner:NotRunner1        | InvalidClassError: is not a subclass-of 'behave.api.runner:ITestRunner'  | Specified runner_class is not a runner.         |
        | BAD_CLASS        | behave_example.bad_runner:NotRunner2        | InvalidClassError: is not a subclass-of 'behave.api.runner:ITestRunner'  | Runner class does not behave properly.          |
        | BAD_FUNCTION     | behave_example.bad_runner:return_none       | InvalidClassError: is not a class                                        | runner_class is a function.                     |
        | BAD_VALUE        | behave_example.bad_runner:CONSTANT_1        | InvalidClassError: is not a class                                        | runner_class is a constant number.              |
        | INCOMPLETE_CLASS | behave_example.incomplete:IncompleteRunner1 | TypeError: Can't instantiate abstract class IncompleteRunner1 with abstract method(s)? __init__ | Constructor is missing  |
        | INCOMPLETE_CLASS | behave_example.incomplete:IncompleteRunner2 | TypeError: Can't instantiate abstract class IncompleteRunner2 with abstract method(s)? run      | run() method is missing |
        | INVALID_CLASS    | behave_example.incomplete:IncompleteRunner4 | InvalidClassError: run\(\) is not callable                                 | run is a bool-value (no method) |

      @use.with_python.min_version=3.3
      Examples: BAD_CASE2
        | syndrome         | runner_class                                | failure_message                                                          | case                                            |
        | INCOMPLETE_CLASS | behave_example.incomplete:IncompleteRunner3 | TypeError: Can't instantiate abstract class IncompleteRunner3 with abstract method(s)? undefined_steps  | undefined_steps property is missing |

        # -- PYTHON VERSION SENSITIVITY on INCOMPLETE_CLASS with API TypeError exception:
        # Since Python 3.9: "... methods ..." is only used in plural case (if multiple methods are missing).
        #   "TypeError: Can't instantiate abstract class <CLASS_NAME> with abstract method <METHOD_NAME>" ( for Python.version >= 3.9)
        #   "TypeError: Can't instantiate abstract class <CLASS_NAME> with abstract methods <METHOD_NAME>" (for Python.version < 3.9)


  Rule: Use own Test Runner-by-Name (BAD CASES)

    Scenario Template: Use UNKNOWN-RUNNER-NAME with --runner=<runner_name> (ConfigError)
      Given an empty file named "behave.ini"
      When I run "behave --runner=<runner_name>"
      Then it should fail
      And the command output should contain:
        """
        <syndrome>: <failure_message>
        """

      Examples:
        | runner_name    | syndrome     | failure_message                      |
        | UNKNOWN_NAME   | ConfigError  | runner=UNKNOWN_NAME (RUNNER-ALIAS NOT FOUND)   |
        | 42             | ConfigError  | runner=42 (RUNNER-ALIAS NOT FOUND)   |
        | 4.23           | ConfigError  | runner=4.23 (RUNNER-ALIAS NOT FOUND) |
        | true           | ConfigError  | runner=true (RUNNER-ALIAS NOT FOUND) |


    Scenario Template: Use BAD-RUNNER-NAME with --runner=<runner_name> (<syndrome>)
      Given a file named "behave_example/bad_runner.py" with:
        """
        from behave.api.runner import ITestRunner

        class NotRunner1(object): pass
        class NotRunner2(object):
            run = True

        CONSTANT_1 = 42

        def return_none(*args, **kwargs):
            return None
        """
      And an empty file named "behave_example/__init__.py"
      And a file named "behave.ini" with:
        """
        [behave.runners]
        <runner_name> = <runner_class>
        """
      When I run "behave --runner=<runner_name>"
      Then it should fail
      And the command output should contain:
        """
        BAD_RUNNER_CLASS: FAILED to load runner.class=<runner_class> (<syndrome>)
        """
      And the command output should match:
        """
        <syndrome>: <problem_description>
        """

      Examples: BAD_CASE
        | runner_name        | runner_class                                | syndrome            | problem_description                                   | case                                            |
        | NAME_FOR_UNKNOWN_MODULE     | unknown:Runner1                             | ModuleNotFoundError | No module named 'unknown'                             | Python module does not exist (or was not found) |
        | NAME_FOR_UNKNOWN_CLASS_1    | behave_example:UnknownClass                 | ClassNotFoundError  | behave_example:UnknownClass                           | Runner class does not exist in module.          |
        | NAME_FOR_UNKNOWN_CLASS_2    | behave_example.bad_runner:42                | ClassNotFoundError  | behave_example.bad_runner:42                          | runner_class=number                             |
        | NAME_FOR_BAD_CLASS_1        | behave_example.bad_runner:NotRunner1        | InvalidClassError   | is not a subclass-of 'behave.api.runner:ITestRunner'  | Specified runner_class is not a runner.         |
        | NAME_FOR_BAD_CLASS_2        | behave_example.bad_runner:NotRunner2        | InvalidClassError   | is not a subclass-of 'behave.api.runner:ITestRunner'  | Runner class does not behave properly.          |
        | NAME_FOR_BAD_CLASS_3        | behave_example.bad_runner:return_none       | InvalidClassError   | is not a class                                        | runner_class is a function.                     |
        | NAME_FOR_BAD_CLASS_4        | behave_example.bad_runner:CONSTANT_1        | InvalidClassError   | is not a class                                        | runner_class is a constant number.              |


    Scenario Template: Use INCOMPLETE-RUNNER-NAME with --runner=<runner_name> (<syndrome>)
      Given a file named "behave_example/incomplete.py" with:
        """
        from behave.api.runner import ITestRunner

        class IncompleteRunner1(ITestRunner): # NO-CTOR
            def run(self): pass

            @property
            def undefined_steps(self):
                return []

        class IncompleteRunner2(ITestRunner): # NO-RUN-METHOD
            def __init__(self, config):
                self.config = config

            @property
            def undefined_steps(self):
                return []

        class IncompleteRunner3(ITestRunner): # MISSING: undefined_steps
            def __init__(self, config):
                self.config = config
            def run(self): pass

        class IncompleteRunner4(ITestRunner): # BAD-RUN-METHOD
            def __init__(self, config):
                self.config = config
            run = True

            @property
            def undefined_steps(self):
                return []
        """
      And an empty file named "behave_example/__init__.py"
      And a file named "behave.ini" with:
        """
        [behave.runners]
        <runner_name> = <runner_class>
        """
      When I run "behave --runner=<runner_name>"
      Then it should fail
      And the command output should match:
        """
        <syndrome>: <problem_description>
        """

      Examples: BAD_CASE
        | runner_name                 | runner_class                                | syndrome            | problem_description                                   | case                                            |
        | NAME_FOR_INCOMPLETE_CLASS_1 | behave_example.incomplete:IncompleteRunner1 | TypeError           | Can't instantiate abstract class IncompleteRunner1 with abstract method(s)? __init__ | Constructor is missing  |
        | NAME_FOR_INCOMPLETE_CLASS_2 | behave_example.incomplete:IncompleteRunner2 | TypeError           | Can't instantiate abstract class IncompleteRunner2 with abstract method(s)? run      | run() method is missing |
        | NAME_FOR_INCOMPLETE_CLASS_4 | behave_example.incomplete:IncompleteRunner4 | InvalidClassError   | run\(\) is not callable                               | run is a bool-value (no method) |

      @use.with_python.min_version=3.3
      Examples: BAD_CASE2
        | runner_name                 | runner_class                                | syndrome            | problem_description                                   | case                                            |
        | NAME_FOR_INCOMPLETE_CLASS_3 | behave_example.incomplete:IncompleteRunner3 | TypeError           | Can't instantiate abstract class IncompleteRunner3 with abstract method(s)? undefined_steps | missing-property |
