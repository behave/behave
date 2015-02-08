Feature: Multiple Formatter with different outputs

  . SPECIFICATION: Command-line option --format
  .  * Each --format option specifies one formatter to use.
  .
  . SPECIFICATION: Command-line option --outfile
  .  * Multiple --outfile options can be provided
  .  * The nth --outfile option is used for the nth formatter
  .  * If less --outfile options are provided than formatter,
  .    the remaining formatter use stdout as output stream.
  .    Therefore, the last formatter should in general use stdout.
  .
  . SPECIFICATION: Configuration file
  .  * Option format with one or more formatters can be used (optional).
  .  * Formatters specified in the configuration file are always executed.
  .  * If not enough outfiles are specified, the outfiles list is extended
  .    by using an outfile "${format}.output" for each missing outfile.
  .
  . RELATED TO:
  .  * issue #47  Formatter chain is broken


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
    Scenario: One formatter, no outfile (use stdout instead)
      Given a file named "behave.ini" does not exist
      When I run "behave -f plain -T features/"
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

    @no_configfile
    Scenario: One formatter, one outfile
      Given a file named "behave.ini" does not exist
      When I run "behave -f plain --outfile=output/plain.out -T features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should not contain:
        """
        Feature: Alice
          Scenario: A1
        """
      But a file named "output/plain.out" should exist
      And the file "output/plain.out" should contain:
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

    @no_configfile
    Scenario: Two formatter, one outfile
      Given a file named "behave.ini" does not exist
      When I run "behave -f plain -o output/plain.out -f progress -T features/"
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
      But a file named "output/plain.out" should exist
      And the file "output/plain.out" should contain:
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


    @no_configfile
    Scenario: More outfiles than formatter should fail with CONFIG-ERROR
      Given a file named "behave.ini" does not exist
      When I run "behave -f plain -o plain.output -o xxx.output features/"
      Then it should fail with:
        """
        CONFIG-ERROR: More outfiles (2) than formatters (1).
        """

    @with_configfile
    Scenario: Use default formatter and outfile from behave configuration file
      Given a file named "behave.ini" with:
        """
        [behave]
        format   = plain
        outfiles = output/plain.out
        show_timings = false
        """
      And I remove the directory "output"
      When I run "behave features/"
      Then it should pass
      And the command output should not contain:
        """
        Feature: Alice
          Scenario: A1
        """
      But a file named "output/plain.out" should exist
      And the file "output/plain.out" should contain:
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
    Scenario: Use default formatter and another without outfile from behave configuration file
      Given a file named "behave.ini" with:
        """
        [behave]
        default_format = plain
        format = progress
        # -- OOPS: No outfile specified => Use "${format}.output" as outfile
        show_timings = false
        """
      And I remove the directory "output"
      When I run "behave features/"
      Then it should pass
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
      And a file named "progress.output" should exist
      And the file "progress.output" should contain:
        """
        features/alice.feature  .
        features/bob.feature  .
        """


    @with_configfile
    Scenario: Command-line formatter/outfile extend behave configuration file args
      Given a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
        format   = plain
        outfiles = output/plain.out
        """
      And I remove the directory "output"
      When I run "behave -c -f pretty -o output/pretty.out -f progress -o output/progress.out features/"
      Then it should pass
      And the file "output/progress.out" should contain:
        """
        features/alice.feature  .
        features/bob.feature  .
        """
      And the file "output/pretty.out" should contain:
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
      And a file named "output/plain.out" should exist
      And the file "output/plain.out" should contain:
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
    Scenario: Combination of formatter from configfile and command-line cannot cause outfile offsets
      Given a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
        format = plain
        # -- OOPS: No outfiles defined => Use "${format}.output" as outfile.
        """
      And I remove the directory "output"
      When I run "behave -f progress -o output/progress.out features/"
      Then it should pass
      And the command output should not contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... passed
            When a step passes ... passed
            Then a step passes ... passed
        """
      But the file "plain.output" should contain:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes ... passed
            When a step passes ... passed
            Then a step passes ... passed
        """
      And the file "output/progress.out" should contain:
        """
        features/alice.feature  .
        features/bob.feature  .
        """
