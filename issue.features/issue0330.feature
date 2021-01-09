@issue
Feature: Issue #330: Skipped scenarios are included in junit reports when --no-skipped is used

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import step

      @step('{word:w} step passes')
      def step_passes(context, word):
          pass
      """
    And a file named "features/alice.feature" with:
      """
      @tag1
      Feature: Alice
        Scenario: Alice1
          Given a step passes
      """
    And a file named "features/bob.feature" with:
      """
      Feature: Bob
        Scenario: Bob1
          Given another step passes
      """
    And a file named "features/charly.feature" with:
      """
      Feature: Charly

        @tag1
        Scenario: Charly1
          Given some step passes

        Scenario: Charly2
          When another step passes
      """
    And a file named "alice_and_bob.featureset" with:
      """
      features/alice.feature
      features/bob.feature
      """
    And a file named "behave.ini" with:
      """
      [behave]
      default_format  = plain
      junit_directory = test_results

      [behave.userdata]
      behave.reporter.junit.show_timestamp = false
      behave.reporter.junit.show_hostname = false
      """

  Scenario: Junit report for skipped feature is not created with --no-skipped
    When I run "behave --junit -t @tag1 --no-skipped @alice_and_bob.featureset"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 1 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-bob.xml" does not exist
    And the command output should contain:
      """
      Feature: Alice
        Scenario: Alice1
          Given a step passes ... passed
      """
    But the command output should not contain "Feature: Bob"
    And note that "bob.feature is skipped"


  @not.with_python.version=3.8
  @not.with_python.version=3.9
  @not.with_python.version=3.10
  Scenario: Junit report for skipped feature is created with --show-skipped (py.version < 3.8)
    When I run "behave --junit -t @tag1 --show-skipped @alice_and_bob.featureset"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 1 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-bob.xml" exists
    And the file "test_results/TESTS-bob.xml" should contain:
      """
      <testsuite errors="0" failures="0" name="bob.Bob" skipped="1" tests="1" time="0.0">
      """

  @use.with_python.version=3.8
  @use.with_python.version=3.9
  @use.with_python.version=3.10
  Scenario: Junit report for skipped feature is created with --show-skipped (py.version >= 3.8)
    When I run "behave --junit -t @tag1 --show-skipped @alice_and_bob.featureset"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 1 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-bob.xml" exists
    And the file "test_results/TESTS-bob.xml" should contain:
      """
      <testsuite name="bob.Bob" tests="1" errors="0" failures="0" skipped="1" time="0.0">
      """
      # -- HINT FOR: Python < 3.8
      # <testsuite errors="0" failures="0" name="bob.Bob" skipped="1" tests="1" time="0.0">

  @not.with_python.version=3.8
  @not.with_python.version=3.9
  @not.with_python.version=3.10
  Scenario: Junit report for skipped scenario is neither shown nor counted with --no-skipped (py.version < 3.8)
    When I run "behave --junit -t @tag1 --no-skipped"
    Then it should pass with:
      """
      2 features passed, 0 failed, 1 skipped
      2 scenarios passed, 0 failed, 2 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-charly.xml" exists
    And the file "test_results/TESTS-charly.xml" should contain:
      """
      <testsuite errors="0" failures="0" name="charly.Charly" skipped="0" tests="1"
      """
    And the file "test_results/TESTS-charly.xml" should not contain:
      """
      <testcase classname="charly.Charly" name="Charly2"
      """
    And note that "Charly2 is the skipped scenarion in charly.feature"

  @use.with_python.version=3.8
  @use.with_python.version=3.9
  @use.with_python.version=3.10
  Scenario: Junit report for skipped scenario is neither shown nor counted with --no-skipped (py.version >= 3.8)
    When I run "behave --junit -t @tag1 --no-skipped"
    Then it should pass with:
      """
      2 features passed, 0 failed, 1 skipped
      2 scenarios passed, 0 failed, 2 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-charly.xml" exists
    And the file "test_results/TESTS-charly.xml" should contain:
      """
      <testsuite name="charly.Charly" tests="1" errors="0" failures="0" skipped="0"
      """
      # -- HINT FOR: Python < 3.8
      # <testsuite errors="0" failures="0" name="charly.Charly" skipped="0" tests="1"
    And the file "test_results/TESTS-charly.xml" should not contain:
      """
      <testcase classname="charly.Charly" name="Charly2"
      """
    And note that "Charly2 is the skipped scenarion in charly.feature"


  @not.with_python.version=3.8
  @not.with_python.version=3.9
  @not.with_python.version=3.10
  Scenario: Junit report for skipped scenario is shown and counted with --show-skipped (py.version < 3.8)
    When I run "behave --junit -t @tag1 --show-skipped"
    Then it should pass with:
      """
      2 features passed, 0 failed, 1 skipped
      2 scenarios passed, 0 failed, 2 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-charly.xml" exists
    And the file "test_results/TESTS-charly.xml" should contain:
      """
      <testsuite errors="0" failures="0" name="charly.Charly" skipped="1" tests="2"
      """
    And the file "test_results/TESTS-charly.xml" should contain:
      """
      <testcase classname="charly.Charly" name="Charly2" status="skipped"
      """
    And note that "Charly2 is the skipped scenarion in charly.feature"


  @use.with_python.version=3.8
  @use.with_python.version=3.9
  @use.with_python.version=3.10
  Scenario: Junit report for skipped scenario is shown and counted with --show-skipped (py.version >= 3.8)
    When I run "behave --junit -t @tag1 --show-skipped"
    Then it should pass with:
      """
      2 features passed, 0 failed, 1 skipped
      2 scenarios passed, 0 failed, 2 skipped
      """
    And a file named "test_results/TESTS-alice.xml" exists
    And a file named "test_results/TESTS-charly.xml" exists
    And the file "test_results/TESTS-charly.xml" should contain:
      """
      <testsuite name="charly.Charly" tests="2" errors="0" failures="0" skipped="1"
      """
      # HINT: Python < 3.8
      # <testsuite errors="0" failures="0" name="charly.Charly" skipped="1" tests="2"
    And the file "test_results/TESTS-charly.xml" should contain:
      """
      <testcase classname="charly.Charly" name="Charly2" status="skipped"
      """
    And note that "Charly2 is the skipped scenarion in charly.feature"

