@sequential
Feature: Default Formatter

  . SPECIFICATION:
  .  * Default defined order is used when no `--order` configuration is set.
  .  * Steps are in random order when no `--order random` configuration is set.


    Background:
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass
        """
      And a file named "features/alice.feature" with:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes
            When a step passes
            Then a step passes
          Scenario: A2
            Given a step passes
            When a step passes
            Then a step passes
        """
      And a file named "features/bob.feature" with:
        """
        Feature: Bob
          Scenario: B1
            When a step passes
            Then a step passes
          Scenario: B2
            When a step passes
            Then a step passes
        """

    @no_configfile
    Scenario: The order of the scenarios are as defined
      Given a file named "behave.ini" does not exist
      When I run "behave -c features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        4 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Alice # features/alice.feature:1
          Scenario: A1          # features/alice.feature:2
            Given a step passes # features/steps/passing_steps.py:3
            When a step passes  # features/steps/passing_steps.py:3
            Then a step passes  # features/steps/passing_steps.py:3
          Scenario: A2          # features/alice.feature:6
            Given a step passes # features/steps/passing_steps.py:3
            When a step passes  # features/steps/passing_steps.py:3
            Then a step passes  # features/steps/passing_steps.py:3

        Feature: Bob # features/bob.feature:1
          Scenario: B1         # features/bob.feature:2
            When a step passes # features/steps/passing_steps.py:3
            Then a step passes # features/steps/passing_steps.py:3
          Scenario: B2         # features/bob.feature:5
            When a step passes # features/steps/passing_steps.py:3
            Then a step passes # features/steps/passing_steps.py:3
        """

    @no_configfile
    Scenario: The order of the scenarios are as defined
      Given a file named "behave.ini" does not exist
      When I run "behave --order random:90 -c features/"
      Then it should pass with:
        """
        Randomized with seed: 90
        2 features passed, 0 failed, 0 skipped
        4 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Bob # features/bob.feature:1
          Scenario: B2         # features/bob.feature:5
            When a step passes # features/steps/passing_steps.py:3
            Then a step passes # features/steps/passing_steps.py:3
          Scenario: B1         # features/bob.feature:2
            When a step passes # features/steps/passing_steps.py:3
            Then a step passes # features/steps/passing_steps.py:3

        Feature: Alice # features/alice.feature:1
          Scenario: A2          # features/alice.feature:6
            Given a step passes # features/steps/passing_steps.py:3
            When a step passes  # features/steps/passing_steps.py:3
            Then a step passes  # features/steps/passing_steps.py:3
          Scenario: A1          # features/alice.feature:2
            Given a step passes # features/steps/passing_steps.py:3
            When a step passes  # features/steps/passing_steps.py:3
            Then a step passes  # features/steps/passing_steps.py:3
        """
