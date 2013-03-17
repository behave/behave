@issue
Feature: Issue #81: Allow defining steps in a separate library

    | The current design forces steps.py to be in a particular folder.
    | This does not allow to reuse a common library of BDD steps across
    | multiple software projects in a company.
    | It would be great if one could define a separate lib with common steps
    | (e.g. steps4mycompany.py)


  Background: Test Setup
    Given a new working directory
    And   an empty file named "step_library42/__init__.py"
    And   a file named "step_library42/alice_steps.py" with:
        """
        # -- ALICE-STEPS: Anonymous step names.
        from behave import given, when, then

        @given(u'I use the step library "{library}"')
        def step(context, library):
            pass

        @when(u'I use steps from this step library')
        def step(context):
            pass

        @then(u'these steps are executed')
        def step(context):
            pass
        """
    And   a file named "features/use_step_library.feature" with:
        """
        Feature:
          Scenario:
            Given I use the step library "alice"
            When  I use steps from this step library
            Then  these steps are executed
        """

  Scenario: Proof of Concept
    Given a file named "features/steps/use_step_libs.py" with:
        """
        from step_library42.alice_steps import *
        """
    When I run "behave --no-timings -f plain features/use_step_library.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
           Scenario:
             Given I use the step library "alice" ... passed
              When I use steps from this step library ... passed
              Then these steps are executed ... passed
        """

  Scenario: With --format=pretty
    Given a file named "features/steps/use_step_libs.py" with:
        """
        from step_library42.alice_steps import *
        """
    When I run "behave -c -f pretty features/use_step_library.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:  # features/use_step_library.feature:1
          Scenario:                                 # features/use_step_library.feature:2
            Given I use the step library "alice"    # step_library42/alice_steps.py:4
            When I use steps from this step library # step_library42/alice_steps.py:8
            Then these steps are executed           # step_library42/alice_steps.py:12
        """

  Scenario: Selective step import from step library
    Given a file named "step_library42/bob_steps.py" with:
        """
        # -- BOB-STEPS: Explicit step function names (otherwise same as alice).
        from behave import given, when, then

        @given(u'I use the step library "{library}"')
        def given_I_use_the_step_library(context, library):
            pass

        @when(u'I use steps from this step library')
        def when_I_use_steps_from_this_step_library(context):
            pass

        @then(u'these steps are executed')
        def then_these_steps_are_executed(context):
            pass
        """
    And a file named "features/steps/use_step_libs.py" with:
        """
        from step_library42.bob_steps import given_I_use_the_step_library
        from step_library42.bob_steps import when_I_use_steps_from_this_step_library
        from step_library42.bob_steps import then_these_steps_are_executed
        """
    When I run "behave -c -f pretty features/use_step_library.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:  # features/use_step_library.feature:1
          Scenario:                                 # features/use_step_library.feature:2
            Given I use the step library "alice"    # step_library42/bob_steps.py:4
            When I use steps from this step library # step_library42/bob_steps.py:8
            Then these steps are executed           # step_library42/bob_steps.py:12
        """

  Scenario: Import step library in "environment.py"
    Given a file named "features/environment.py" with:
        """
        from step_library42.alice_steps import *
        """
    And   an empty file named "features/steps/__init__.py"
    When I run "behave -c -f pretty features/use_step_library.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:  # features/use_step_library.feature:1
          Scenario:                                 # features/use_step_library.feature:2
            Given I use the step library "alice"    # step_library42/alice_steps.py:4
            When I use steps from this step library # step_library42/alice_steps.py:8
            Then these steps are executed           # step_library42/alice_steps.py:12
        """
