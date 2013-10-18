Feature: Select feature files by using regular expressions (self-test)

  Use behave self-tests to ensure that --incude/--exclude options work.
  RELATED: runner.select_files_by_regexp.feature

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And an empty file named "features/steps/steps.py"
    And a file named "features/alice.feature" with:
        """
        Feature: Alice
          Scenario: A1
        """
    And a file named "features/barbi.feature" with:
        """
        Feature: Barbi
          Scenario: B1
        """
    And a file named "features/bob.feature" with:
        """
        Feature: Bob
          Scenario: B2
        """


  Scenario: Include only feature files

    Select the following feature files: barbi.feature, bob.feature

      When I run "behave --include='features/b.*' -f plain features/"
      Then it should pass with:
        """
        2 features passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Barbi
          Scenario: B1

        Feature: Bob
          Scenario: B2
        """

  Scenario: Exclude only feature files

    Select the following feature files: alice.feature

      When I run "behave --exclude='features/b.*' -f plain features/"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Alice
        """

  Scenario: Include and exclude feature files

    Select the following feature files: alice.feature

      When I run "behave --include='features/.*a.*\.feature' --exclude='.*/barbi.*' -f plain features/"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Feature: Alice
        """
