Feature: Default Tags with tag-expressions v1

  As a tester
  I want to define a number of default tags in a configuration file
  So that I do not have to specify these tags each time on the command-line.

  . NOTES:
  .   * default tags are normally used to exclude/disable tag(s)
  .   * command-line tags override the default tags
  .   * default tags can be disabled by using the following expression
  .     on the command-line: behave --tags=-xxx ... (where xxx is an unknown tag)


    @setup
    Scenario: Test Setup
      Given a new working directory
      And a file named "features/one.feature" with:
        """
        Feature:
          @not_implemented
          Scenario: Alice
            Given missing step passes

          @foo
          Scenario: Bob
            Given another step passes
            Then a step passes
        """
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """

  Scenario: Use default tags with one tag
    Given a file named "behave.ini" with:
      """
      [behave]
      show_skipped = false
      default_tags = -@not_implemented
      """
    When I run "behave -f plain features"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 1 skipped, 0 undefined
      """
    And the command output should contain "Scenario: Bob"
    But the command output should not contain "Scenario: Alice"


  Scenario: Override default tag on command-line
    Given a file named "behave.ini" with:
      """
      [behave]
      show_skipped = false
      default_tags = -@not_implemented
      """
    When I run "behave -f plain --tags=not_implemented features"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 1 skipped
      1 step passed, 0 failed, 2 skipped, 0 undefined
      """
    And the command output should contain "Scenario: Alice"
    But the command output should not contain "Scenario: Bob"

  @xfail
  Scenario: Use default tags with two tags
    Given a file named "behave.ini" with:
      """
      [behave]
      show_skipped = false
      default_tags = -@xfail,-@not_implemented
      # tag logic := not @not_implemented and not @xfail
      """
    When I run "behave -f plain features"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 1 skipped, 0 undefined
      """
    And the command output should contain "Scenario: Bob"
    But the command output should not contain "Scenario: Alice"


  Scenario: Override default tags on command-line
    Given a file named "behave.ini" with:
      """
      [behave]
      show_skipped = false
      default_tags = -@xfail,-@not_implemented
      # tag logic := not @not_implemented and not @xfail
      """
    When I run "behave -f plain --tags=not_implemented,foo features"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain "Scenario: Alice"
    But the command output should contain "Scenario: Bob"
