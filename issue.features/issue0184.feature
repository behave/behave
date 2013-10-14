@issue
Feature: Issue #184: TypeError when running behave with --include option

  | Running behave with option '--include' causes fail with following error:
  |
  |  Traceback (most recent call last):
  |   File "/.../bin/behave", line 8, in
  |     load_entry_point('behave==1.2.3', 'console_scripts', 'behave')()
  |   File "/.../lib/python2.7/site-packages/behave/__main__.py", line 111, in main
  |   ...
  |   File "/.../lib/python2.7/site-packages/behave/runner.py", line 490, in run_with_paths
  |     if not self.config.exclude(filename) ]
  |   File "/.../lib/python2.7/site-packages/behave/configuration.py", line 488, in exclude
  |     if self.include_re and self.include_re.search(filename) is None:
  |   TypeError: expected string or buffer
  |
  | RELATED:
  |  * features/runner.select_files_by_regexp.feature
  |  * features/runner.select_files_by_regexp2.feature

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/passing_steps.py" with:
      """
      from behave import step

      @step('{word:w} step passes')
      def step_passes(context, word):
          pass
      """
    And a file named "features/alice.feature" with:
      """
      Feature: Alice
        Scenario: A1
          Given a step passes
      """
    And a file named "features/bob.feature" with:
      """
      Feature: Bob
        Scenario: B1
          When another step passes

        Scenario: B2
          Then another step passes
      """

  Scenario: Use --include command-line option to select some features
    When I run "behave -f plain --include='features/a.*\.feature'"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature: Alice
      """
    But the command output should not contain:
      """
      Feature: Bob
      """


  Scenario: Use --include command-line option to select all features
    When I run "behave -f plain --include='.*\.feature'"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      3 scenarios passed, 0 failed, 0 skipped
      """


  Scenario: Use --exclude command-line option
    When I run "behave -f plain --exclude='features/a.*\.feature'"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature: Bob
      """
    But the command output should not contain:
      """
      Feature: Alice
      """


  Scenario: Use --include and --exclude command-line options
    When I run "behave -f plain --include='.*\.feature' --exclude='features/a.*\.feature'"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature: Bob
      """
    But the command output should not contain:
      """
      Feature: Alice
      """

  Scenario: Use --include command-line option with file location
    When I run "behave -f plain --include='features/a.*\.feature' features/alice.feature:3"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature: Alice
      """
    But the command output should not contain:
      """
      Feature: Bob
      """

  Scenario: Use --exclude command-line option with feature list file
    Given a file named "selected.txt" with:
      """
      # -- FEATURE-LIST FILE:
      features/alice.feature:3
      features/bob.feature:7
      """
    When I run "behave -f plain --no-skipped --exclude='.*/a.*\.feature' @selected.txt"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 1 skipped
      """
    And the command output should contain:
      """
      Feature: Bob
        Scenario: B2
      """
    But the command output should not contain:
      """
      Feature: Alice
      """
