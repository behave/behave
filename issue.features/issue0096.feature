@issue
Feature: Issue #96: Sub-steps failed without any error info to help debug issue

    . I am trying to run execute_steps. One of them fails, but the error output
    . from behave has no details whatsoever. It is virtually impossible
    . to figure out why it failed. as no error output is present except the
    . final error message
    .
    .   def before_scenario(context,scenario):
    .       context.execute_steps(u'''
    .           When "admin:admin" sends POST "/tasks/testStart"
    .           Then I expect HTTP code 200
    .       ''')
    .
    . File ".../behave/runner.py", line 262, in execute_steps
    .  assert False, "FAILED SUB-STEP: %s" % step
    .  AssertionError: FAILED SUB-STEP: When "admin:admin" sends POST "/tasks/testStart"
    .
    .  All we get is the "sub-step failed" but no info whatsoever
    .  as to why it failed...



  Background:
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
        """
        from behave import step
        import sys

        @step(u'a step passes')
        def step_passes(context):
            pass

        @step(u'a step fails')
        def step_fails(context):
            assert False, 'EXPECT: Step fails.'

        @step(u'a step fails with stdout "{message}"')
        def step_fails_with_stdout(context, message):
            sys.stdout.write("%s\n" % message)
            assert False, 'EXPECT: Step fails with stdout.'

        @step(u'a step fails with stderr "{message}"')
        def step_fails_with_stderr(context, message):
            sys.stderr.write("%s\n" % message)
            assert False, 'EXPECT: Step fails with stderr.'

        @step(u'a step raises an error "{message}"')
        def step_raises_exception(context, message):
            raise RuntimeError(message)

        @step(u'the following steps should pass')
        def step_following_steps_should_pass(context):
            context.execute_steps(context.text.strip())
        """

  Scenario: Execute steps and one fails (EXPECTATION-MISMATCH: Assert fails)
    Given a file named "features/issue96_case1.feature" with:
        '''
        Feature:
            Scenario:
                When the following steps should pass:
                   """
                   Given a step passes
                   When  a step fails
                   Then  a step passes
                   """
        '''
    When I run "behave -c features/issue96_case1.feature"
    Then it should fail with:
        """
        Assertion Failed: FAILED SUB-STEP: When a step fails
        Substep info: Assertion Failed: EXPECT: Step fails.
        """

  Scenario: Execute steps and error occurs (UNEXPECTED: exception is raised)
    Given a file named "features/issue96_case2.feature" with:
        '''
        Feature:
            Scenario:
                When the following steps should pass:
                   """
                   Given a step passes
                   When a step raises an error "Alice is alive"
                   Then a step passes
                   """
        '''
    When I run "behave -c features/issue96_case2.feature"
    Then it should fail with:
        """
        RuntimeError: Alice is alive
        """
    And the command output should contain:
        """
        Assertion Failed: FAILED SUB-STEP: When a step raises an error "Alice is alive"
        Substep info: Traceback (most recent call last):
        """

  Scenario: Execute steps and one fails with stdout capture
    Given a file named "features/issue96_case3.feature" with:
        '''
        Feature:
            Scenario:
                When the following steps should pass:
                   """
                   Given a step passes
                   When a step fails with stdout "STDOUT: Alice is alive"
                   Then a step passes
                   """
        '''
    When I run "behave -c features/issue96_case3.feature"
    Then it should fail with:
        """
        Assertion Failed: FAILED SUB-STEP: When a step fails with stdout "STDOUT: Alice is alive"
        Substep info: Assertion Failed: EXPECT: Step fails with stdout.
        """
    And the command output should contain:
        """
        Captured stdout:
        STDOUT: Alice is alive
        """


  Scenario: Execute steps and one fails with stderr capture
    Given a file named "features/issue96_case4.feature" with:
        '''
        Feature:
            Scenario:
                When the following steps should pass:
                   """
                   Given a step passes
                   When a step fails with stderr "STDERR: Alice is alive"
                   Then a step passes
                   """
        '''
    When I run "behave -c features/issue96_case4.feature"
    Then it should fail with:
        """
        Assertion Failed: FAILED SUB-STEP: When a step fails with stderr "STDERR: Alice is alive"
        Substep info: Assertion Failed: EXPECT: Step fails with stderr.
        """
    And the command output should contain:
        """
        Captured stderr:
        STDERR: Alice is alive
        """

  Scenario: Execute steps and fail in before_scenario hook
    Given a file named "features/issue96_case5.feature" with:
        """
        Feature:
            Scenario:
                Given a step passes
                When  a step passes
                Then  a step passes
        """
    And a file named "features/environment.py" with:
        """
        def before_scenario(context, scenario):
            context.execute_steps(u'''
               Given a step passes
               When a step passes
               Then a step fails
            ''')
        """
    When I run "behave -c features/issue96_case5.feature"
    Then it should fail with:
        """
        HOOK-ERROR in before_scenario: AssertionError: FAILED SUB-STEP: Then a step fails
        Substep info: Assertion Failed: EXPECT: Step fails.
        """

