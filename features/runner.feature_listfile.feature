@sequential
Feature: Feature Listfile (List of feature filenames/directories)

    As a tester
    I want to run a list of features together
    And I do not want to provide the list each time
    But provide a text file that contains the list of features.

    . SPECIFICATION: behave file args
    .  * Prepend an '@' char (AT) to the feature configfile name to classify it.
    .
    . SPECIFICATION: Feature listfile (text file)
    .  * Each line contains a feature filename or directory with features
    .  * Feature filenames/dirnames are relative to the feature configfile
    .  * Empty lines are removed while reading
    .  * Comment lines are removed while reading (start with '#' char)
    .  * Wildcards are expanded to select 0..N files or directories.
    .  * Wildcards for file locations are not supported (only filenames or dirs).
    .
    . SPECIFICATION: Runner
    .  * Feature configfile with unknown/not found feature files
    .    cause runner to fail.
    .
    . NOTE: Also supported by Cucumber.
    . RELATED: issue #75


  @setup
  Scenario: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('a step passes')
      def step_passes(context):
          pass
      """
    And   a file named "features/alice.feature" with:
      """
      Feature: Alice
        Scenario:
          Given a step passes
      """
    And   a file named "features/bob.feature" with:
      """
      Feature: Bob
        Scenario:
          Given a step passes
      """


  Scenario: Use @feature_listfile in WORKDIR directory (above features/)
    Given a file named "alice_and_bob2.txt" with:
      """
      features/alice.feature
      features/bob.feature
      """
    When I run "behave @alice_and_bob2.txt"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """


  Scenario: Use @feature_listfile in features/ subdirectory (Case 2)
    Given a file named "features/alice_and_bob.txt" with:
      """
      alice.feature
      bob.feature
      """
    When I run "behave @features/alice_and_bob.txt"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Use @feature_listfile with some empty lines
    Given a file named "features/alice_and_bob_with_empty_lines.txt" with:
      """
      alice.feature

      bob.feature
      """
    When I run "behave @features/alice_and_bob_with_empty_lines.txt"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Use @feature_listfile with some comment lines
    Given a file named "features/alice_and_bob_with_comment_lines.txt" with:
      """
      alice.feature
      # -- USE: bob (comment line)
      bob.feature
      """
    When I run "behave @features/alice_and_bob_with_comment_lines.txt"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  Scenario: Use @feature_listfile with wildcards (Case 1)

    Use feature list-file with wildcard pattern to select features.

    Given a file named "with_wildcard_feature.txt" with:
      """
      features/a*.feature
      """
    When I run "behave -f plain --no-timings @with_wildcard_feature.txt"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Feature: Alice

        Scenario:
          Given a step passes ... passed
      """

  Scenario: Use @feature_listfile with wildcards (Case 2)

    Use feature list-file with:
      - normal filename
      - wildcard pattern to select features

    Given a file named "with_wildcard_feature2.txt" with:
      """
      features/alice.feature
      features/b*.feature
      """
    When I run "behave -f plain --no-timings @with_wildcard_feature2.txt"
    Then it should pass with:
      """
      2 features passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
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

  Scenario: Use @feature_listfile with wildcards for file location (not supported)

    Note that wildcards are not supported when file locations are used.

    Given a file named "with_wildcard_location.txt" with:
      """
      features/a*.feature:3
      """
    When I run "behave -f plain --no-timings @with_wildcard_location.txt"
    Then it should fail with:
      """
      ConfigError: No steps directory in '{__WORKDIR__}'
      """


  Scenario: Use empty @feature_listfile (Case 1)
    Given an empty file named "empty.txt"
    When I run "behave @empty.txt"
    Then it should fail with:
      """
      No steps directory in '{__WORKDIR__}'
      """

  Scenario: Use empty @feature_listfile in features subdirectory (Case 2)
    Given an empty file named "features/empty.txt"
    When I run "behave @features/empty.txt"
    Then it should pass with:
      """
      0 features passed, 0 failed, 0 skipped
      """

  Scenario: Use @feature_listfile with unknown feature file (Case 1)
    Given a file named "with_unknown_feature.txt" with:
      """
      features/alice.feature
      features/UNKNOWN.feature
      """
    When I run "behave @with_unknown_feature.txt"
    Then it should fail with:
      """
      Error: [Errno 2] No such file or directory: '{__WORKDIR__}/features/UNKNOWN.feature'
      """

  Scenario: Use @feature_listfile with unknown feature file (Case 2)
    Given a file named "features/with_unknown_feature2.txt" with:
      """
      UNKNOWN.feature
      """
    When I run "behave @features/with_unknown_feature2.txt"
    Then it should fail with:
      """
      Error: [Errno 2] No such file or directory: '{__WORKDIR__}/features/UNKNOWN.feature'
      """

  Scenario: Use unknown @feature_listfile
    When I run "behave @unknown_feature_configfile.txt"
    Then it should fail with:
      """
      FileNotFoundError: unknown_feature_configfile.txt
      """
