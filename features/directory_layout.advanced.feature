Feature: Advanced, more complex directory layout (Variant 2)

  As a story/test writer
  I want a deeper, more structured directory structure when many feature files exist
  So that I have the parts better under control (more managable)

  | ADVANCED, MORE COMPLEX DIRECTORY LAYOUT STRUCTURE:
  |     features/
  |       +-- group1.features/
  |       |      +-- *.feature
  |       +-- group2.features/
  |       |      +-- *.feature
  |       +-- steps/*.py          # Step definitions or step-library imports.
  |       +-- environment.py      # OPTIONAL: environment setup/hooks.
  |
  | SEE ALSO:
  |   * http://pythonhosted.org/behave/gherkin.html#layout-variations
  |
  | RELATED:
  |   * issue #99: Layout variation "a directory containing your feature files" ...

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
        And a file named "features/steps/environment_steps.py" with:
            """
            from behave import step

            @step('environment setup was done')
            def step_ensure_environment_setup(context):
                assert context.setup_magic == 42
            """
        And a file named "features/environment.py" with:
            """
            def before_all(context):
                context.setup_magic = 42
            """
        And a file named "features/group1/alice.feature" with:
            """
            Feature: Alice
                Scenario: A1
                  Given a step passes
                  When another step passes
                  Then a step passes

                Scenario: A2
                  Then environment setup was done
            """
        And a file named "features/group1/bob.feature" with:
            """
            Feature: Bob
                Scenario: B1
                  When a step passes
                  Then another step passes
            """
        And a file named "features/group2/charly.feature" with:
            """
            Feature: Charly
                Scenario: C1
                  Given another step passes
                  Then a step passes
            """


    Scenario: Run behave with feature directory
        When I run "behave -f progress features/"
        Then it should pass with:
            """
            3 features passed, 0 failed, 0 skipped
            4 scenarios passed, 0 failed, 0 skipped
            8 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Run behave with feature subdirectory (CASE 1)
        When I run "behave -f progress features/group1/"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 0 skipped
            6 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Run behave with feature subdirectory (CASE 2)
        When I run "behave -f progress features/group2/"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            2 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Run behave with one feature file
        When I run "behave -f progress features/group1/alice.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 0 skipped
            4 steps passed, 0 failed, 0 skipped, 0 undefined
            """
        When I run "behave -f progress features/group2/charly.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            2 steps passed, 0 failed, 0 skipped, 0 undefined
            """


    Scenario: Run behave with two feature files (CASE 1)
        Given a file named "one.featureset" with:
            """
            features/group1/alice.feature
            features/group2/charly.feature
            """
        When I run "behave -f progress @one.featureset"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 0 skipped
            6 steps passed, 0 failed, 0 skipped, 0 undefined
            """

    Scenario: Run behave with two feature files (CASE 2: different ordering)
        Given a file named "two.featureset" with:
            """
            features/group2/charly.feature
            features/group1/alice.feature
            """
        When I run "behave -f progress @two.featureset"
        Then it should pass with:
            """
            2 features passed, 0 failed, 0 skipped
            3 scenarios passed, 0 failed, 0 skipped
            6 steps passed, 0 failed, 0 skipped, 0 undefined
            """
