@issue
@junit
Feature: Issue #446 -- Support scenario hook-errors with JUnitReporter

  . Currently, when a hook error occurs in:
  .
  .   * before_scenario()
  .   * after_scenario()
  .
  . a sanity check in the JUnitReporter prevents sane JUnit XML output.


    @setup
    Scenario: Skip scenario without steps
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/before_scenario_failure.feature" with:
        """
        Feature: Alice
          @hook_failure.before_scenario
          Scenario: A1
            Given a step passes
        """
      And a file named "features/after_scenario_failure.feature" with:
        """
        Feature: Bob
          @hook_failure.after_scenario
          Scenario: B1
            Given another step passes
        """
      And a file named "features/environment.py" with:
        """
        def cause_hook_failure():
            raise RuntimeError("OOPS")

        def before_scenario(context, scenario):
            if "hook_failure.before_scenario" in scenario.tags:
                cause_hook_failure()

        def after_scenario(context, scenario):
            if "hook_failure.after_scenario" in scenario.tags:
                cause_hook_failure()
        """
      And a file named "behave.ini" with:
        """
        [behave]
        show_timings = false

        [behave.userdata]
        behave.reporter.junit.show_timestamp = False
        behave.reporter.junit.show_hostname = False
        """

    @not.with_python.version=3.8
    @not.with_python.version=3.9
    @not.with_python.version=3.10
    Scenario: Hook error in before_scenario() (py.version < 3.8)
      When I run "behave -f plain --junit features/before_scenario_failure.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
        HOOK-ERROR in before_scenario: RuntimeError: OOPS
        """
      And the file "reports/TESTS-before_scenario_failure.xml" should contain:
        """
        <testsuite errors="1" failures="0" name="before_scenario_failure.Alice" skipped="0" tests="1"
        """
      And the file "reports/TESTS-before_scenario_failure.xml" should contain:
        """
        <error message="HOOK-ERROR in before_scenario: RuntimeError: OOPS" type="RuntimeError">
        """
      And the file "reports/TESTS-before_scenario_failure.xml" should contain:
        """
        File "features/environment.py", line 6, in before_scenario
          cause_hook_failure()
        File "features/environment.py", line 2, in cause_hook_failure
          raise RuntimeError("OOPS")
        """
      And note that "the traceback is contained in the XML element <error/>"


    @use.with_python.version=3.8
    @use.with_python.version=3.9
    @use.with_python.version=3.10
    Scenario: Hook error in before_scenario() (py.version >= 3.8)
      When I run "behave -f plain --junit features/before_scenario_failure.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
        HOOK-ERROR in before_scenario: RuntimeError: OOPS
        """
      And the file "reports/TESTS-before_scenario_failure.xml" should contain:
        """
        <testsuite name="before_scenario_failure.Alice" tests="1" errors="1" failures="0" skipped="0"
        """
        # -- HINT FOR: Python < 3.8
        # <testsuite errors="1" failures="0" name="before_scenario_failure.Alice" skipped="0" tests="1"
      And the file "reports/TESTS-before_scenario_failure.xml" should contain:
        """
        <error type="RuntimeError" message="HOOK-ERROR in before_scenario: RuntimeError: OOPS">
        """
        # -- HINT FOR: Python < 3.8
        # <error message="HOOK-ERROR in before_scenario: RuntimeError: OOPS" type="RuntimeError">
      And the file "reports/TESTS-before_scenario_failure.xml" should contain:
        """
        File "features/environment.py", line 6, in before_scenario
          cause_hook_failure()
        File "features/environment.py", line 2, in cause_hook_failure
          raise RuntimeError("OOPS")
        """
      And note that "the traceback is contained in the XML element <error/>"


    @not.with_python.version=3.8
    @not.with_python.version=3.9
    @not.with_python.version=3.10
    Scenario: Hook error in after_scenario() (py.version < 3.8)
      When I run "behave -f plain --junit features/after_scenario_failure.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: B1
            Given another step passes ... passed
        HOOK-ERROR in after_scenario: RuntimeError: OOPS
        """
      And the file "reports/TESTS-after_scenario_failure.xml" should contain:
        """
        <testsuite errors="1" failures="0" name="after_scenario_failure.Bob" skipped="0" tests="1"
        """
      And the file "reports/TESTS-after_scenario_failure.xml" should contain:
        """
        <error message="HOOK-ERROR in after_scenario: RuntimeError: OOPS" type="RuntimeError">
        """
      And the file "reports/TESTS-after_scenario_failure.xml" should contain:
        """
        File "features/environment.py", line 10, in after_scenario
          cause_hook_failure()
        File "features/environment.py", line 2, in cause_hook_failure
          raise RuntimeError("OOPS")
        """
      And note that "the traceback is contained in the XML element <error/>"


    @use.with_python.version=3.8
    @use.with_python.version=3.9
    @use.with_python.version=3.10
    Scenario: Hook error in after_scenario() (py.version >= 3.8)
      When I run "behave -f plain --junit features/after_scenario_failure.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: B1
            Given another step passes ... passed
        HOOK-ERROR in after_scenario: RuntimeError: OOPS
        """
      And the file "reports/TESTS-after_scenario_failure.xml" should contain:
        """
        <testsuite name="after_scenario_failure.Bob" tests="1" errors="1" failures="0" skipped="0"
        """
        # -- HINT FOR: Python < 3.8
        # <testsuite errors="1" failures="0" name="after_scenario_failure.Bob" skipped="0" tests="1"
      And the file "reports/TESTS-after_scenario_failure.xml" should contain:
        """
        <error type="RuntimeError" message="HOOK-ERROR in after_scenario: RuntimeError: OOPS">
        """
        # -- HINT FOR: Python < 3.8
        # <error message="HOOK-ERROR in after_scenario: RuntimeError: OOPS" type="RuntimeError">
      And the file "reports/TESTS-after_scenario_failure.xml" should contain:
        """
        File "features/environment.py", line 10, in after_scenario
          cause_hook_failure()
        File "features/environment.py", line 2, in cause_hook_failure
          raise RuntimeError("OOPS")
        """
      And note that "the traceback is contained in the XML element <error/>"
