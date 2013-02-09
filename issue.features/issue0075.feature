@issue
Feature: Issue #75: behave @features_from_text_file does not work

   | Feature of Cucumber. Reading the source code, I see it partly implemented.
   |
   |   $ behave @list_of_features.txt
   |   https://github.com/jeamland/behave/blob/master/behave/runner.py#L416:L430
   |
   | However it fails because:
   |  * it does not remove the @ from the path
   |  * it does not search the steps/ directory in the parents of the feature files themselves


  Background: Test Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      from behave import given

      @given(u'a step passes')
      def step(context):
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

  Scenario: Use @feature_list_file in WORKDIR directory (above features/)
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

  Scenario: Use @feature_list_file in features/ subdirectory (Case 2)
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

  Scenario: Use @feature_list_file with some empty lines
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

  Scenario: Use @feature_list_file with some comment lines
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

  Scenario: Use empty @feature_list_file (Case 1)
    Given a file named "empty.txt" with:
      """
      """
    When I run "behave @empty.txt"
    Then it should fail with:
      """
      No steps directory in "{__WORKDIR__}"
      """

  Scenario: Use empty @feature_list_file in features subdirectory (Case 2)
    Given a file named "features/empty.txt" with:
      """
      """
    When I run "behave @features/empty.txt"
    Then it should pass with:
      """
      0 features passed, 0 failed, 0 skipped
      """

  Scenario: Use @feature_list_file with unknown feature file (Case 1)
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

  Scenario: Use @feature_list_file with unknown feature file (Case 2)
    Given a file named "features/with_unknown_feature2.txt" with:
      """
      UNKNOWN.feature
      """
    When I run "behave @features/with_unknown_feature2.txt"
    Then it should fail with:
      """
      IOError: [Errno 2] No such file or directory: '{__WORKDIR__}/features/UNKNOWN.feature'
      """

