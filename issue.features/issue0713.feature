@issue
Feature: Issue #713 -- Background section doesn't support descriptive paragraphs



  Background: Setup
    Given a new working directory
    And a file named "features/syndrome_713.feature" with:
      """
      Feature: Background Section Contains Descriptive text
        Per the documentation, behave supports the Gherkin standard
        The gherkin standard says that the Background section can contain descriptive text.
        (See: https://docs.cucumber.io/gherkin/reference/#descriptions )

        Background: Short Description is Here
          The A longer description should be permitted here.
          However, as of this writing, behave throws an error instead

          Given a step passes

        Scenario: Short Description Here
          This scenario is here to satisfy the syntactic requirements for a feature file.

          Given another step passes
      """
    And a file named "features/steps/use_step_library.py" with:
      """
      # -- REUSE STEPS:
      import behave4cmd0.passing_steps
      """

  Scenario: Use Background with Description
    When I run "behave -f plain features/syndrome_713.feature"
    Then it should pass with:
      """
      Feature: Background Section Contains Descriptive text
        Background: Short Description is Here

        Scenario: Short Description Here
          Given a step passes ... passed
          Given another step passes ... passed

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should not contain "Parser failure in state"
    And note that "the Background description was parsed."
