Feature: Pending Step (Step exists with StepNotImplementedError Marker)

   . TERMINOLOGY:
   .  * A pending step exists and is registered in the step-registry.
   .  * BUT: step-function is not implemented yet (StepNotImplementedError)
   .
   . SPECIFICATION:
   .  * A pending step exists and is registered in the step-registry.
   .  * Therefore, a binding exists between the step-pattern and step-function.
   .  * A pending step raises a StepNotImplemented exception.
   .  * A pending step is passed if its scenario has a @wip tag.
   .  * A pending step is passed if its scenario inherits a @wip tag.
   .  * A pending step fails with error otherwise.
   .  * Pending steps are not detected in dry-run mode
   .    (because the step-function is not executed)
   .
   . EXCEPTION(s) FOR PENDING STEPS:
   .  * StepNotImplementedError
   .  * PendingStepError (alternative; derived from: StepNotImplementedError)
   .
   . RELATED: Undefined steps
   .  * An undefined step is not found in the step-registry.
   .  * Therefore, no binding exists between step-pattern and step-function.
   .
   . SEE ALSO:
   .  * step.undefined_steps.feature

    Background:
      Given a new working directory
      And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        show_timings = false
        """
      And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.passing_steps
        """
      And a file named "features/steps/pending_steps.py" with:
        """
        from behave import given, when, then
        from behave.api.pending_step import StepNotImplementedError

        @given(u'a pending step is used')
        def step_pending_given(context):
            raise StepNotImplementedError('Given a pending step is used')

        @when(u'a pending step is used')
        def step_pending_when(context):
            raise StepNotImplementedError('When a pending step is used')

        @then(u'a pending step is used')
        def step_pending_then(context):
            raise StepNotImplementedError('Then a pending step is used')
        """

    Rule: Pending Step passes in wip-mode

      Scenario: Pending steps pass if scenario has @wip tag
        Given a file named "features/use_wip_sceanrio_and_pending.feature" with:
          """
          Feature:
            @wip
            Scenario: Alice (has @wip tag)
              Given a step passes
              And a pending step is used
              When another step passes
          """
        When I run "behave -f plain features/use_wip_sceanrio_and_pending.feature"
        Then it should pass with:
          """
          1 scenario passed, 0 failed, 0 skipped
          2 steps passed, 0 failed, 0 skipped, 1 pending_warn
          """
        And the command output should contain:
          """
          Scenario: Alice (has @wip tag)
            Given a step passes ... passed
            And a pending step is used ... pending_warn
            When another step passes ... passed
          """

      Scenario: Pending steps pass if scenario has inherited @wip tag
        Given a file named "features/use_wip_feature_and_pending.feature" with:
          """
          @wip
          Feature:
            Scenario: Bob (inherits @wip tag)
              Given a step passes
              And a pending step is used
              When another step passes
          """
        When I run "behave -f plain features/use_wip_feature_and_pending.feature"
        Then it should pass with:
          """
          1 scenario passed, 0 failed, 0 skipped
          2 steps passed, 0 failed, 0 skipped, 1 pending_warn
          """
        And the command output should contain:
          """
          Scenario: Bob (inherits @wip tag)
            Given a step passes ... passed
            And a pending step is used ... pending_warn
            When another step passes ... passed
          """

      Scenario: Pending steps pass with --wip option
        Given a file named "features/use_pending.feature" with:
          """
          Feature:
            @wip
            Scenario: Charly
              Given a step passes
              And a pending step is used
              When another step passes

            Scenario: Doro
              Given a step passes
              And a pending step is used
              When another step passes
          """
        When I run "behave -f plain --wip features/use_pending.feature"
        Then it should pass with:
          """
          1 scenario passed, 0 failed, 1 skipped
          2 steps passed, 0 failed, 3 skipped, 1 pending_warn
          """
        And the command output should contain:
          """
          Scenario: Charly
            Given a step passes ... passed
            And a pending step is used ... pending_warn
            When another step passes ... passed
          """
        And note that "the --wip option automatically selects @wip tags"

    Rule: Pending Step fails with error in non wip-mode
      Background:
        And a file named "features/use_pending_steps.feature" with:
          """
          Feature:
            Scenario: One
              Given a step passes
              And a pending step is used
              When another step passes

            Scenario: Two
              Given a step passes
              When a pending step is used
              Then some step passes

            Scenario: Three
              Given a step passes
              When another step passes
              Then a pending step is used
          """

      Scenario: Pending given step causes scenario to fail with error
        When I run "behave -f plain features/use_pending_steps.feature:2"
        Then it should fail
        And the command output should contain:
          """
          Feature:
             Scenario: One
               Given a step passes ... passed
               And a pending step is used ... pending
          """
        But the command output should contain:
          """
          StepNotImplementedError: Given a pending step is used
          """
        # And the command output should contain:
        #  """
        #  File "features/steps/pending_steps.py", line 5, in step_pending_given
        #    raise StepNotImplementedError('Given a pending step is used')
        #  """

      Scenario: Pending when step causes scenario to fail with error
        When I run "behave -f plain features/use_pending_steps.feature:8"
        Then it should fail with:
          """
          0 scenarios passed, 0 failed, 1 error, 2 skipped
          1 step passed, 0 failed, 7 skipped, 1 pending
          """
        And the command output should contain:
          """
          Feature:
             Scenario: Two
               Given a step passes ... passed
                When a pending step is used ... pending
          """
        But the command output should contain:
          """
          StepNotImplementedError: When a pending step is used
          """
        # And the command output should contain:
        #  """
        #  File "features/steps/pending_steps.py", line 9, in step_pending_when
        #    raise StepNotImplementedError('When a pending step is used')
        #  """

      Scenario: Pending then step causes scenario to fail with error
        When I run "behave -f plain features/use_pending_steps.feature:13"
        Then it should fail
        And the command output should contain:
          """
          Feature:
            Scenario: Three
              Given a step passes ... passed
              When another step passes ... passed
              Then a pending step is used ... pending
          """
        But the command output should contain:
          """
          StepNotImplementedError: Then a pending step is used
          """
        # And the command output should contain:
        #  """
        #  File "features/steps/pending_steps.py", line 13, in step_pending_then
        #    raise StepNotImplementedError('Then a pending step is used')
        #  """
