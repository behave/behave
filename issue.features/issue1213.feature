@issue
@not_reproducible
Feature: Issue #1213 -- Scenario Outline is not expanding Example value when using filtering via --name

  . DESCRIPTION:
  .   * Scenario Outline/Template expansion seems not to be working if "--name" option is used
  .   * DISCOVERED WITH: behave v1.2.6
  .   * NOT-REPRODUCIBLE WITH: behave v1.2.6 and v1.2.7.dev6
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1213

  Background:
    Given a new working directory
    And a file named "features/steps/some_steps.py" with:
      """
      from __future__ import absolute_import, print_function
      from behave import given, when, then, step

      @given(u'I am in "{directory}" directory')
      def step_given_in_directory(ctx, directory):
          pass

      @given(u'I have temporary $HOME in "{directory}"')
      def step_given_temporary_homedir_in_directory(ctx, directory):
          pass

      @when(u'I run "partcad {cmdline}"')
      def step_run_pardcad(ctx, cmdline):
          pass

      @then(u'the command should exit with a status code of "{exit_code:d}"')
      def step_run_pardcad(ctx, exit_code):
          pass

      @step(u'a file named "{filename}" does not exist')
      def step_file_named_does_not_exits(ctx, filename):
          pass

      @step(u'a file named "{filename}" should be created')
      def step_file_named_should_be_created(ctx, filename):
          pass

      @then(u'STDOUT should contain "{text}"')
      def step_stdout_should_contain(ctx, text):
          pass

      @then(u'STDOUT should not contain "{text}"')
      def step_stdout_should_not_contain(ctx, text):
          pass
      """
    And a file named "features/syndrome_1213.feature" with:
      '''
      Feature: `pc render` command

        Background: Sandbox
          Given I am in "/tmp/sandbox/behave" directory
          Given I have temporary $HOME in "/tmp/sandbox/home"
          Given a file named "partcad.yaml" does not exist

        Scenario Outline: `pc render` command
          When I run "partcad -p /workspaces/partcad/examples render --package /produce_assembly_assy -t <type> -O ./ -a :logo_embedded"
          Then the command should exit with a status code of "0"
          Then a file named "<filename>" should be created
          Given a file named "partcad.yaml" does not exist
          Then STDOUT should contain "DONE: Render: this:"
          Then STDOUT should not contain "WARN:"

        @type-text
        Examples: Media Types: Text
          |    type | filename              |
          |  readme | README.md             |
      '''

  Scenario: Verify Placeholders are replaced with their values
    When I run `behave -f plain features/syndrome_1213.feature`
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      9 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Scenario Outline: `pc render` command -- @1.1 Media Types: Text
        Given I am in "/tmp/sandbox/behave" directory ... passed
        Given I have temporary $HOME in "/tmp/sandbox/home" ... passed
        Given a file named "partcad.yaml" does not exist ... passed
        When I run "partcad -p /workspaces/partcad/examples render --package /produce_assembly_assy -t readme -O ./ -a :logo_embedded" ... passed
        Then the command should exit with a status code of "0" ... passed
        Then a file named "README.md" should be created ... passed
        Given a file named "partcad.yaml" does not exist ... passed
        Then STDOUT should contain "DONE: Render: this:" ... passed
        Then STDOUT should not contain "WARN:" ... passed
      """
    But the command output should not contain "<type>"
    And the command output should not contain "<filename>"
    And note that "all Examples table placeholders are replaced"

  Scenario: Use --name option
    When I run `behave -f plain --name "`pc render` command -- @1.1 Media Types: Text" features/syndrome_1213.feature`
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      9 steps passed, 0 failed, 0 skipped
      """
    And the command output should contain:
      """
      Scenario Outline: `pc render` command -- @1.1 Media Types: Text
        Given I am in "/tmp/sandbox/behave" directory ... passed
        Given I have temporary $HOME in "/tmp/sandbox/home" ... passed
        Given a file named "partcad.yaml" does not exist ... passed
        When I run "partcad -p /workspaces/partcad/examples render --package /produce_assembly_assy -t readme -O ./ -a :logo_embedded" ... passed
        Then the command should exit with a status code of "0" ... passed
        Then a file named "README.md" should be created ... passed
        Given a file named "partcad.yaml" does not exist ... passed
        Then STDOUT should contain "DONE: Render: this:" ... passed
        Then STDOUT should not contain "WARN:" ... passed
      """
    But the command output should not contain "<type>"
    And the command output should not contain "<filename>"
    And note that "all Examples table placeholders are replaced"
