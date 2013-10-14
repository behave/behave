@issue
Feature: Issue #152: Fix encoding issues

    | I fixed two encoding issues in pretty formatter and in JUnit serialization.
    | Now it's possible to use accented letters in feature files and
    | create JUnit reports from the tests.


  Scenario: Ensure JUnit reports can be created from a foreign language
    Given a new working directory
    And an empty file named "features/steps/steps.py"
    And a file named "features/eins.feature" with:
        """
        # language: de
        Funktionalität: Die Welt ist schön
            Szenario: Was wäre wenn die schöne, neue Welt untergeht
        """
    When I run "behave -f plain --junit --no-timings features/eins.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      0 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Funktionalität: Die Welt ist schön
         Szenario: Was wäre wenn die schöne, neue Welt untergeht
      """


  @reuse.colocated_test
  Scenario: Ensure JUnit reports can be created from a foreign language
    Given I use the current directory as working directory
    When I run "behave -f plain --junit --no-timings tools/test-features/french.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      5 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Fonctionnalité: testing stuff
         Scénario: test stuff
           Etant donné I am testing stuff ... passed
           Quand I exercise it work ... passed
           Alors it will work ... passed
         Scénario: test more stuff
            Etant donné I am testing stuff ... passed
            Alors it will work ... passed
      """
