@issue
Feature: Issue #77: Does not capture stdout from sub-processes

  . My step functions are using wrapper objects to interact with SUT.
  . Those wrappers use this kind of thing to invoke executables:
  .
  .   subprocess.check_call('myprog', ..., stderr=subprocess.STDOUT)
  .
  . However, the output from those calls does not appear in the stdout
  . captured by behave when a step fails.


  Background: Test Setup
    Given a new working directory
    Given a file named "hello.py" with:
        """
        import sys

        def hello():
            result = 0
            args = sys.argv[1:]
            if args and args[0].startswith("--fail"):
                result = 1
                args   = args[1:]
            message = " ".join(args)
            sys.stdout.write("Hello {0}\n".format(message))
            sys.exit(result)

        if __name__ == "__main__":
            hello()
        """
    And   a file named "features/steps/subprocess_call_steps.py" with:
        """
        from behave import given, when, then
        import subprocess
        import os.path
        import sys

        PYTHON = sys.executable
        HERE = os.path.dirname(__file__)

        @when(u'I make a subprocess call "hello {commandline}"')
        def step(context, commandline):
            result = subprocess_call_hello(commandline.split())
            assert result == 0

        def subprocess_call_hello(args):
            command_args = [ PYTHON, "hello.py" ] + args
            result = subprocess.check_call(command_args, stderr=subprocess.STDOUT)
            return result
            # result = subprocess.check_output(command_args, stderr=subprocess.STDOUT)
            # return result
        """

  Scenario: Subprocess call shows generated output
    Given a file named "features/issue77_hello_OK.feature" with:
        """
        Feature:
          Scenario:
            When I make a subprocess call "hello world."
        """
    When I run "behave -f plain features/issue77_hello_OK.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Hello world.
        """

  Scenario: Subprocess call fails with captured output
    Given a file named "features/issue77_hello_FAIL.feature" with:
        """
        Feature:
          Scenario:
            When I make a subprocess call "hello --fail FAIL."
        """
    When I run "behave -f plain features/issue77_hello_FAIL.feature"
    Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        0 steps passed, 1 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Hello FAIL.
        """
