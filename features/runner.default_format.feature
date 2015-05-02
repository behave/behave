@sequential
Feature: Default Formatter

  . SPECIFICATION:
  .  * Default formatter is used when no other formatter is specified/provided.
  .  * Default formatter uses stdout as default output/outfile.
  .  * Pretty formatter is the default formatter.
  .  * Behave configfile can specify the default formatter.


    @setup
    Scenario: Test Setup
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
        """
      And a file named "features/bob.feature" with:
        """
        Feature: Bob
          Scenario: B1
            When a step passes
            Then a step passes
        """

    @no_configfile
    Scenario: Pretty formatter is used as default formatter if no other is defined
      Given a file named "behave.ini" does not exist
      When I run "behave -c features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Alice # features/alice.feature:1
          Scenario: A1          # features/alice.feature:2
            Given a step passes # features/steps/passing_steps.py:3
            When a step passes  # features/steps/passing_steps.py:3
            Then a step passes  # features/steps/passing_steps.py:3

        Feature: Bob # features/bob.feature:1
          Scenario: B1         # features/bob.feature:2
            When a step passes # features/steps/passing_steps.py:3
            Then a step passes # features/steps/passing_steps.py:3
        """


    @with_configfile
    Scenario: Configfile can define own default formatter
      Given a file named "behave.ini" with:
        """
        [behave]
        default_format = plain
        show_timings = false
        """
      When I run "behave features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... passed
            When a step passes ... passed
            Then a step passes ... passed

        Feature: Bob
          Scenario: B1
            When a step passes ... passed
            Then a step passes ... passed
        """

    @with_configfile
    Scenario: Use default formatter with own outfile instead of stdout
      Given a file named "behave.ini" with:
        """
        [behave]
        default_format = plain
        show_timings = false
        """
      When I run "behave --outfile=output/default.out features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        """
      And the file "output/default.out" should contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... passed
            When a step passes ... passed
            Then a step passes ... passed

        Feature: Bob
          Scenario: B1
            When a step passes ... passed
            Then a step passes ... passed
        """


    @with_configfile
    Scenario: Can override default formatter from configfile on command-line
      Given a file named "behave.ini" with:
        """
        [behave]
        default_format = plain
        show_timings = false
        """
      When I run "behave -f progress features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        features/alice.feature  .
        features/bob.feature  .
        """


    # -- Some formatter are specified in configfile.
    @with_configfile
    Scenario: Default formatter is used when non is provided on command-line
      Given a file named "behave.ini" with:
        """
        [behave]
        default_format = plain
        format = progress
        outfiles = output/progress.out
        show_timings = false
        """
      And I remove the directory "output"
      When I run "behave features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... passed
            When a step passes ... passed
            Then a step passes ... passed

        Feature: Bob
          Scenario: B1
            When a step passes ... passed
            Then a step passes ... passed
        """
      And the file "output/progress.out" should contain:
        """
        features/alice.feature  .
        features/bob.feature  .
        """
