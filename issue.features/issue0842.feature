@issue
@formatter.json
Feature: Issue #842 -- JSON file does not contain current feature results if run is aborted

  . DESCRIPTION:
  .   If a test run is aborted by raising a KeyboardInterrupt
  .   (for example: in the "after_scenario" hook),
  .   the JSON formatter output excludes the current (aborted) feature.
  .   With only one feature, the JSON file is empty ("[]").
  .
  . FIXED IN: behave v1.3.0 (since: behave v1.2.7.dev7)
  .   A KeyboardInterrupt in a hook is now handled as hook-error
  .   that aborts the test run. The formatters are finished properly.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/842

  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.passing_steps
        import behave4cmd0.failing_steps
        """
    And a file named "features/steps/abort_steps.py" with:
        """
        from behave import step

        @step(u'{word:w} step aborts the test run')
        def step_abort_test_run(context, word):
            raise KeyboardInterrupt()
        """

  Scenario: Abort test run in after_scenario hook (original problem)
    Given a file named "features/environment.py" with:
        """
        from behave.model_core import Status

        def after_scenario(context, scenario):
            if scenario.status == Status.failed and "abort_on_fail" in scenario.tags:
                raise KeyboardInterrupt()
        """
    And a file named "features/abort.feature" with:
        """
        Feature: Alice
          @abort_on_fail
          Scenario: Alice1 aborts on failure
            Given a step passes
            When another step fails
            Then a step passes
        """
    When I run "behave -f json.pretty -o build/result.json features/abort.feature"
    Then it should fail with:
        """
        ABORTED: By user.
        """
    And the file "build/result.json" should contain:
        """
        "name": "Alice",
        """
    And the file "build/result.json" should contain:
        """
        "name": "Alice1 aborts on failure",
        """
    And the file "build/result.json" should contain:
        """
        "status": "hook_error",
        """

  Scenario: Abort test run in a step of the second feature
    Given a file named "features/a1_first.feature" with:
        """
        Feature: Alice
          Scenario: Alice1
            Given a step passes
        """
    And a file named "features/a2_second.feature" with:
        """
        Feature: Bob
          Scenario: Bob1
            Given a step passes
            When a step aborts the test run
            Then another step passes

          Scenario: Bob2 is never run
            Given a step passes
        """
    When I run "behave -f json.pretty -o build/result.json features/"
    Then it should fail with:
        """
        ABORTED: By user.
        """
    And the file "build/result.json" should contain:
        """
        "name": "Alice",
        """
    And the file "build/result.json" should contain:
        """
        "name": "Bob",
        """
    And the file "build/result.json" should contain:
        """
        "name": "Bob1",
        """
    But the file "build/result.json" should not contain:
        """
        "name": "Bob2 is never run",
        """
