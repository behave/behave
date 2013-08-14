Feature: Basic directory layout (Variant 1)

  As a story/test writer
  I want a simple, non-deep directory structure
  So that I can easily get an overview which stories/tests exist

  | BASIC DIRECTORY LAYOUT STRUCTURE:
  |     features/
  |       +-- steps/*.py          # Step definitions or step-library imports.
  |       +-- *.feature           # Feature files.
  |       +-- environment.py      # OPTIONAL: environment setup/hooks.
  |
  | SEE ALSO:
  |   * http://pythonhosted.org/behave/gherkin.html#layout-variations


    @setup
    Scenario: Setup directory structure
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass

            @step('{word:w} step fails')
            def step_fails(context, word):
                assert False, "XFAIL-STEP"
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice
                Scenario: A1
                  Given a step passes
                  When another step passes
                  Then a step passes
            """
        And a file named "features/bob.feature" with:
            """
            Feature: Bob
                Scenario: B1
                  When a step passes
                  Then another step passes
            """


    Scenario: Run behave with feature directory
        When I run "behave -f progress features/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 0 skipped
            5 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Run behave with one feature file
        When I run "behave -f progress features/alice.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            3 steps passed, 0 failed, 0 skipped, 0 undefined
            """


    Scenario: Run behave with two feature files
        When I run "behave -f progress features/alice.feature features/bob.feature"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 0 skipped
            5 steps passed, 0 failed, 0 skipped, 0 undefined
            """
