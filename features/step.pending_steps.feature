Feature: Pending Step (Exists with NotImplementedError Marker)

   . TERMINOLOGY:
   .  * An undefined step is a step without matching step implementation.
   .  * A pending step exists,
   .    but contains only the undefined step snippet as implementation,
   .    that marks it as NotImplemented.
   .
   . RELATED TO:
   .  * step.undefined_steps.feature


    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "behave.ini" with:
        """
        [behave]
        show_skipped = false
        show_timings = false
        """
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass

        @step('{word:w} step fails')
        def step_fails(context, word):
            assert False, "XFAIL"
        """
      And a file named "features/steps/pending_steps.py" with:
        """
        from behave import given, when, then

        @given('a pending step is used')
        def step_pending_given(context):
            raise NotImplementedError('STEP: Given a pending step is used')

        @when('a pending step is used')
        def step_pending_when(context):
            raise NotImplementedError('STEP: When a pending step is used')

        @then('a pending step is used')
        def step_pending_then(context):
            raise NotImplementedError('STEP: Then a pending step is used')
        """
      And a file named "features/use_pending_steps.feature" with:
        """
        Feature:
          Scenario: 1
            Given a step passes
            And a pending step is used
            When another step passes

          Scenario: 2
            Given a step passes
            When a pending step is used
            Then some step passes

          Scenario: 3
            Given a step passes
            When another step passes
            Then a pending step is used
        """

    Scenario: Pending given step (not implemented)
      When I run "behave -f plain features/use_pending_steps.feature:2"
      Then it should fail
      And the command output should contain:
        """
        Feature:
           Scenario: 1
             Given a step passes ... passed
               And a pending step is used ... failed
        """
      But the command output should contain:
        """
        NotImplementedError: STEP: Given a pending step is used
        """
      And the command output should contain:
        """
        File "features/steps/pending_steps.py", line 5, in step_pending_given
          raise NotImplementedError('STEP: Given a pending step is used')
        """

    Scenario: Pending when step (not implemented)
      When I run "behave -f plain features/use_pending_steps.feature:7"
      Then it should fail
      And the command output should contain:
        """
        Feature:
           Scenario: 2
             Given a step passes ... passed
              When a pending step is used ... failed
        """
      But the command output should contain:
        """
        NotImplementedError: STEP: When a pending step is used
        """
      And the command output should contain:
        """
        File "features/steps/pending_steps.py", line 9, in step_pending_when
          raise NotImplementedError('STEP: When a pending step is used')
        """

    Scenario: Pending then step (not implemented)
      When I run "behave -f plain features/use_pending_steps.feature:12"
      Then it should fail
      And the command output should contain:
        """
        Feature:
          Scenario: 3
            Given a step passes ... passed
            When another step passes ... passed
            Then a pending step is used ... failed
        """
      But the command output should contain:
        """
        NotImplementedError: STEP: Then a pending step is used
        """
      And the command output should contain:
        """
        File "features/steps/pending_steps.py", line 13, in step_pending_then
          raise NotImplementedError('STEP: Then a pending step is used')
        """
