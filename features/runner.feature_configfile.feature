@sequential
Feature: Feature-Configfile (List of feature filenames/directories)

    As a tester
    I want to run a list of features together
    And I do not want to provide the list each time
    But provide a text file that contains the list of features.

    | SPECIFICATION: behave file args
    |  * Prepend an '@' char (AT) to the feature configfile name to classify it.
    |
    | SPECIFICATION: Feature configfile (text file)
    |  * Each line contains a feature filename or directory with features
    |  * Feature filenames/dirnames are relative to the feature configfile
    |  * Empty lines are removed while reading
    |  * Comment lines are removed while reading (start with '#' char)
    |
    | SPECIFICATION: Runner
    |  * Feature configfile with unknown/not found feature files
    |    cause runner to fail.
    |
    | NOTE: Also supported by Cucumber.
    | RELATED:
    |  * issue #75


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


  Scenario: Use @feature_configfile in WORKDIR directory (above features/)
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


  Scenario: Use @feature_configfile in features/ subdirectory (Case 2)
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

  Scenario: Use @feature_configfile with some empty lines
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

  Scenario: Use @feature_configfile with some comment lines
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

  Scenario: Use empty @feature_configfile (Case 1)
    Given an empty file named "empty.txt"
    When I run "behave @empty.txt"
    Then it should fail with:
      """
      No steps directory in "{__WORKDIR__}"
      """

  Scenario: Use empty @feature_configfile in features subdirectory (Case 2)
    Given an empty file named "features/empty.txt"
    When I run "behave @features/empty.txt"
    Then it should pass with:
      """
      0 features passed, 0 failed, 0 skipped
      """

  Scenario: Use @feature_configfile with unknown feature file (Case 1)
    Given a file named "with_unknown_feature.txt" with:
      """
      features/alice.feature
      features/UNKNOWN.feature
      """
    When I run "behave @with_unknown_feature.txt"
    Then it should fail with:
      """
      IOError: [Errno 2] No such file or directory: '{__WORKDIR__}/features/UNKNOWN.feature'
      """

  Scenario: Use @feature_configfile with unknown feature file (Case 2)
    Given a file named "features/with_unknown_feature2.txt" with:
      """
      UNKNOWN.feature
      """
    When I run "behave @features/with_unknown_feature2.txt"
    Then it should fail with:
      """
      IOError: [Errno 2] No such file or directory: '{__WORKDIR__}/features/UNKNOWN.feature'
      """

  Scenario: Use unknown @feature_configfile
    When I run "behave @unknown_feature_configfile.txt"
    Then it should fail with:
      """
      FileNotFoundError: unknown_feature_configfile.txt
      """
