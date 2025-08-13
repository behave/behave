@issue
Feature: Issue #1239 -- AmbiguousStep error on step import

  AFFECTED: behave v1.3.0, v1.2.6.dev6
  PYTHON.version: 3.12
  PLATFORM: Ubuntu 24.04

  . DESCRIPTION:
  . Using step matcher "re", I get AmbiguousStep exception when I run behave.
  .
  . * Reproducible if I reimport a step-module by another step-module or python module
  . * NOTE: This is normally a "smell" that your step-modules are not "good structured".
  .
  . OTHERWISE: For first scenario
  .
  . * Only reproducible if I replace @given/@then step decorators with @step decorator.
  .
  . BUT THEN:
  .   An AmbiguousStep error exists now,
  .   because the regular-expression of the first step is too greedy.
  .
  . REMEDIES:
  .   * Change the ordering of both steps: Move the longer, more specific step in front of the other.
  .   * Use double-quotes around your step parameters to mark where the step parameter ends.
  .   * Use better, more specific patterns than MATCH-ANYTHING (aka: `.*`)

  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1239
  .   * THIS_FILE: https://github.com/behave/behave/blob/release/v1.3.x/issue.features/issue1239.feature

  Background:
    Given a new working directory
    And a file named "features/steps/syndrome_steps.py" with:
      """
      from behave import given, then, step

      @given('the file (?P<path>.*)')
      def step_given_the_file(context, path):
          print("path: {};".format(path))

      @then('the file (?P<path>.*) contains:')
      def step_then_the_file_contains(context, path):
          print("path: {};".format(path))
      """
    And a file named "features/environment.py" with:
      """
      from behave import use_step_matcher

      use_step_matcher("re")
      """
    And a file named "features/syndrome_1239.feature" with:
      '''
      Feature: Syndrome
        Scenario: S1
          Given the file one/two/three.txt
          And the file four/five.txt
          Then the file one/two/three.txt contains:
            """
            BOGUS-FILE-CONTENTS: One two three
            """
      '''


  Scenario: Check the syndrome
    When I run "behave -f plain features/syndrome_1239.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "AmbiguousStep:"
    And the command output should contain:
      '''
      Feature: Syndrome
        Scenario: S1
          Given the file one/two/three.txt ... passed
          And the file four/five.txt ... passed
          Then the file one/two/three.txt contains: ... passed
            """
            BOGUS-FILE-CONTENTS: One two three
            """
      '''


  Scenario: Check the syndrome with reimported step-module
    Given a file named "features/steps/reimport_syndrome_steps.py" with:
      """
      import syndrome_steps
      """
    When I run "behave -f plain features/syndrome_1239.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "AmbiguousStep:"
    And the command output should contain:
      '''
      Feature: Syndrome
        Scenario: S1
          Given the file one/two/three.txt ... passed
          And the file four/five.txt ... passed
          Then the file one/two/three.txt contains: ... passed
            """
            BOGUS-FILE-CONTENTS: One two three
            """
      '''

