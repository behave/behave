@issue
Feature: Issue #99: Layout variation "a directory containing your feature files" is broken for running single features

    | When I use a layout as described in the 1.2.2 documentation,
    | I can only specify a whole directory of feature files to run.
    | Specifying a single feature file results in an error from behave:
    |
    |   $ behave -v tests/feature/webui/features/feature_under_test.feature
    |    ...
    |    Supplied path: "tests/feature/webui/features/feature_under_test.feature"
    |    Primary path is to a file so using its directory
    |    Trying base directory: .../tests/feature/webui/features
    |    Trying base directory: .../tests/feature/webui
    |    ERROR: Could not find "steps" directory in your specified path ".../tests/feature/webui/features"
    |    No steps directory in ".../tests/feature/webui/features"
    |
    | My directory layout is as follows:
    |
    |   .../tests/feature/webui/
    |       +-- features/
    |       +-- steps/
    |       +-- environment.py
    |
    | SEE ALSO:
    |   * http://packages.python.org/behave/gherkin.html#layout-variations


  Background:
    Given a new working directory
    And   a file named "root/steps/steps.py" with:
        """
        from behave import step

        @step(u'a step passes')
        def step_passes(context):
            pass
        """
    And   a file named "root/features/alice.feature" with:
        """
        Feature: Alice
          Scenario:
            Given a step passes
        """
    And   a file named "root/features/bob.feature" with:
        """
        Feature: Bob
          Scenario:
            Given a step passes
        """
    And   a file named "root/features2/charly.feature" with:
        """
        Feature: Charly
          Scenario:
            When a step passes
        """

  Scenario: Run features with root directory
    When I run "behave -f plain --no-timings root"
    Then it should pass with:
        """
        3 features passed, 0 failed, 0 skipped
        3 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature: Alice
          Scenario:
            Given a step passes ... passed
        Feature: Bob
          Scenario:
            Given a step passes ... passed
        Feature: Charly
          Scenario:
            When a step passes ... passed
        """

  Scenario: Run features with root/features directory
    When I run "behave -f plain --no-timings root/features"
    Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature: Alice
          Scenario:
            Given a step passes ... passed
        Feature: Bob
          Scenario:
            Given a step passes ... passed
        """

  Scenario: Run features with feature files
    When I run "behave -f plain --no-timings root/features/alice.feature root/features2/charly.feature"
    Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature: Alice
          Scenario:
            Given a step passes ... passed
        Feature: Charly
          Scenario:
            When a step passes ... passed
        """

  Scenario: Run features with feature dir and feature files (other ordering)
    When I run "behave -f plain --no-timings root/features2 root/features/alice.feature"
    Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature: Charly
          Scenario:
            When a step passes ... passed
        Feature: Alice
          Scenario:
            Given a step passes ... passed
        """
