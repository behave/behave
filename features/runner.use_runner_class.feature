Feature: User-provided runner class (extension-point)

  As a user/developer
  I want sometimes replace behave's default runner with an own runner class
  So that I easily support special use cases where a different test runner is needed.

  . NOTES:
  .  * This extension-point was already available internally
  .  * Now you can specify the runner_class in the config-file
  .    or as a command-line option.
  .
  . XXX_TODO: runner-alias(es)


  Background:
    Given a new working directory
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
        """
        import behave4cmd0.passing_steps
        import behave4cmd0.failing_steps
        import behave4cmd0.note_steps
        """
    And a file named "features/environment.py" with:
        """
        from __future__ import print_function
        import os
        from fnmatch import fnmatch

        def print_environment(pattern=None):
            names = ["PYTHONPATH", "PATH"]
            for name in names:
                value = os.environ.get(name, None)
                print("DIAG: env: %s = %r" % (name, value))

        def before_all(ctx):
            print_environment()
        """
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


  Rule: Use the default runner if no runner is specified

    @cmdline
    @default_runner
    @default_runner.<short_id>
    Scenario Outline: Use default runner option (<short_id>)
      Given a file named "behave.ini" does not exist
      When I run "behave -f plain <runner_options> features"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And note that "<case>"

      Examples:
        | short_id       | runner_options                | case |
        | NO_RUNNER      |                               | no runner options are used on cmdline and config-fule. |
        | DEFAULT_RUNNER | --runner=behave.runner:Runner | runner option with default runner class is used on cmdline. |


  @own_runner
  Rule: Use own runner class

    Background: Provide own Runner Classes
      Given a file named "my/good_example.py" with:
        """
        from __future__ import print_function
        from behave.runner import Runner

        class MyRunner1(Runner):
            def run(self):
                print("RUNNER=MyRunner1")
                return super(MyRunner1, self).run()

        class MyRunner2(Runner):
            def run(self):
                print("RUNNER=MyRunner2")
                return super(MyRunner2, self).run()
        """
      And an empty file named "my/__init__.py"

    @own_runner
    @cmdline
    Scenario: Use own runner on cmdline
      Given a file named "behave.ini" does not exist
      When I run "behave -f plain --runner=my.good_example:MyRunner1"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        RUNNER=MyRunner1
        """

    @own_runner
    @config_file
    Scenario: Use runner in config-file
      Given a file named "behave.ini" with:
        """
        [behave]
        runner = my.good_example:MyRunner2
        """
      When I run "behave -f plain features"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        RUNNER=MyRunner2
        """

    @own_runner
    @cmdline
    @config_file
    Scenario: Runner on command-line overrides runner in config-file
      Given a file named "behave.ini" with:
        """
        [behave]
        runner = my.good_example:MyRunner2
        """
      When I run "behave -f plain --runner=my.good_example:MyRunner1"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        RUNNER=MyRunner1
        """


  Rule: Bad cases on command-line
    Background: Bad runner classes
      Given a file named "my/bad_example.py" with:
        """
        from behave.api.runner import ITestRunner
        class NotRunner1(object): pass
        class NotRunner2(object):
            run = True

        class IncompleteRunner1(ITestRunner): # NO-CTOR
            def run(self): pass

        class IncompleteRunner2(ITestRunner): # NO-RUN-METHOD
            def __init__(self, config):
                self.config = config

        class IncompleteRunner3(ITestRunner): # BAD-RUN-METHOD
            def __init__(self, config):
                self.config = config
            run = True

        CONSTANT_1 = 42

        def return_none(*args, **kwargs):
            return None
        """
      And an empty file named "my/__init__.py"

    Scenario Outline: Bad cmdline with --runner=<runner_class> (<syndrome>)
      When I run "behave -f plain --runner=<runner_class>"
      Then it should fail
      And the command output should match:
        """
        <failure_message>
        """
      But note that "problem: <case>"

      Examples:
        | syndrome         | runner_class                     | failure_message                                                                                 | case                                            |
        | UNKNOWN_MODULE   | unknown:Runner1                  | ModuleNotFoundError: No module named 'unknown'                                                  | Python module does not exist (or was not found) |
        | UNKNOWN_CLASS    | my:UnknownClass                  | ClassNotFoundError: my:UnknownClass                                                             | Runner class does not exist in module.          |
        | UNKNOWN_CLASS    | my.bad_example:42                | ClassNotFoundError: my.bad_example:42                                                           | runner_class=number                             |
        | BAD_CLASS        | my.bad_example:NotRunner1        | InvalidClassError: my.bad_example:NotRunner1: not subclass-of behave.api.runner.ITestRunner     | Specified runner_class is not a runner.         |
        | BAD_CLASS        | my.bad_example:NotRunner2        | InvalidClassError: my.bad_example:NotRunner2: not subclass-of behave.api.runner.ITestRunner     | Runner class does not behave properly.          |
        | BAD_FUNCTION     | my.bad_example:return_none       | InvalidClassError: my.bad_example:return_none: not a class                                      | runner_class is a function.                     |
        | BAD_VALUE        | my.bad_example:CONSTANT_1        | InvalidClassError: my.bad_example:CONSTANT_1: not a class                                       | runner_class is a constant number.              |
        | INCOMPLETE_CLASS | my.bad_example:IncompleteRunner1 | TypeError: Can't instantiate abstract class IncompleteRunner1 with abstract method(s)? __init__ | Constructor is missing  |
        | INCOMPLETE_CLASS | my.bad_example:IncompleteRunner2 | TypeError: Can't instantiate abstract class IncompleteRunner2 with abstract method(s)? run      | run() method is missing |

        # -- PYTHON VERSION SENSITIVITY on INCOMPLETE_CLASS with API TypeError exception:
        # Since Python 3.9: "... methods ..." is only used in plural case (if multiple methods are missing).
        #   "TypeError: Can't instantiate abstract class <CLASS_NAME> with abstract method <METHOD_NAME>" ( for Python.version >= 3.9)
        #   "TypeError: Can't instantiate abstract class <CLASS_NAME> with abstract methods <METHOD_NAME>" (for Python.version < 3.9)


    Scenario Outline: Weird cmdline with --runner=<runner_class> (<syndrome>)
      When I run "behave -f plain --runner=<runner_class>"
      Then it should fail with:
        """
        <failure_message>
        """
      But note that "problem: <case>"

      Examples:
        | syndrome | runner_class   | failure_message                 | case |
        | NO_CLASS | 42             | ConfigError: runner=42 (RUNNER-ALIAS NOT FOUND)   | runner_class.module=number  |
        | NO_CLASS | 4.23           | ConfigError: runner=4.23 (RUNNER-ALIAS NOT FOUND) | runner_class.module=floating-point-number  |
        | NO_CLASS | True           | ConfigError: runner=True (RUNNER-ALIAS NOT FOUND) | runner_class.module=bool  |
        | INVALID_CLASS | my.bad_example:IncompleteRunner3 | InvalidClassError: my.bad_example:IncompleteRunner3: run() is not callable | run is a bool-value (no method) |


  Rule: Bad cases with config-file

    Background:
      Given a file named "my/bad_example.py" with:
        """
        from behave.api.runner import ITestRunner
        class NotRunner1(object): pass
        class NotRunner2(object):
            run = True

        class IncompleteRunner1(ITestRunner): # NO-CTOR
            def run(self): pass

        class IncompleteRunner2(ITestRunner): # NO-RUN-METHOD
            def __init__(self, config):
                self.config = config

        class IncompleteRunner3(ITestRunner): # BAD-RUN-METHOD
            def __init__(self, config):
                self.config = config
            run = True

        CONSTANT_1 = 42

        def return_none(*args, **kwargs):
            return None
        """
      And an empty file named "my/__init__.py"

    Scenario Outline: Bad config-file.runner=<runner_class> (<syndrome>)
      Given a file named "behave.ini" with:
        """
        [behave]
        runner = <runner_class>
        """
      When I run "behave -f plain"
      Then it should fail with:
        """
        <failure_message>
        """
      But note that "problem: <case>"

      Examples:
        | syndrome       | runner_class               | failure_message                                                                             | case                                            |
        | UNKNOWN_MODULE | unknown:Runner1            | ModuleNotFoundError: No module named 'unknown'                                              | Python module does not exist (or was not found) |
        | UNKNOWN_CLASS  | my:UnknownClass            | ClassNotFoundError: my:UnknownClass                                                         | Runner class does not exist in module.          |
        | BAD_CLASS      | my.bad_example:NotRunner1  | InvalidClassError: my.bad_example:NotRunner1: not subclass-of behave.api.runner.ITestRunner | Specified runner_class is not a runner.         |
        | BAD_CLASS      | my.bad_example:NotRunner2  | InvalidClassError: my.bad_example:NotRunner2: not subclass-of behave.api.runner.ITestRunner | Runner class does not behave properly.          |
        | BAD_FUNCTION   | my.bad_example:return_none | InvalidClassError: my.bad_example:return_none: not a class                                  | runner_class=function                           |
        | BAD_VALUE      | my.bad_example:CONSTANT_1  | InvalidClassError: my.bad_example:CONSTANT_1: not a class                                   | runner_class=number                             |
