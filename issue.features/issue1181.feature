@question
Feature: Issue #1181 -- Can I add a Formatter in the before_all() Hook

  . WARNING:
  .   * BEWARE: This is not a valid use case.
  .   * Adding another formatter from the "environment.py" file is a hack
  .   * You should never really need to do this.
  .
  . SEE ALSO:
  .   * https://github.com/behave-contrib/behave-html-pretty-formatter/issues/72


  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
      """
      from __future__ import absolute_import
      import behave4cmd0.passing_steps
      """
    And a file named "features/environment.py" with:
      """
      from __future__ import absolute_import, print_function
      from behave.formatter.base import StreamOpener
      from behave.formatter.progress import ScenarioStepProgressFormatter

      def before_all(ctx):
          stream_opener = StreamOpener("build/report4me.txt")
          new_formatter = ScenarioStepProgressFormatter(stream_opener, ctx.config)
          ctx._runner.formatters.append(new_formatter)
      """
    And a file named "features/example.feature" with:
      """
      Feature: Example
        Scenario: E1 -- Ensure that all steps pass
          Given a step passes
          When another step passes
          Then some step passes

        Scenario: E2 -- Now every step must pass
          When some step passes
          Then another step passes
      """


  Scenario: Use new Formatter from the Environment (as POC)
    When I run `behave -f plain features/example.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      5 steps passed, 0 failed, 0 skipped
      """
    And a file named "build/report4me.txt" should exist
    And the file "build/report4me.txt" should contain:
      """
      Example    # features/example.feature
        E1 -- Ensure that all steps pass  ...
        E2 -- Now every step must pass  ..
      """
    And note that "the formatter from the environment could write its report"
