Feature: Use substep directories

  As a behave user
  I want to use a deep, hierarchical steps dir,
  meaning steps from subdirs of the steps directory,
  So that the steps directory structure is more cleaned up.

  . HINT:
  .   If you really have so many step modules,
  .   better use step-libraries, instead (in many cases).
  .
  . REQUIRES: path.py

  Background:
    Given a new working directory
    And a file named "features/steps/use_substep_dirs.py" with:
      """
      # -- REQUIRES: path.py
      # from __future__ import absolute_import
      from behave.runner_util import load_step_modules
      from path import Path

      HERE = Path(__file__).dirname()
      SUBSTEP_DIRS = list(HERE.walkdirs())
      load_step_modules(SUBSTEP_DIRS)
      """
    And a file named "behave.ini" with:
      """
      [behave]
      default_format = pretty
      color = False
      """


  Scenario: Use one substep directory
    Given a file named "features/steps/alice_steps.py" with:
      """
      from behave import step

      @step('I know Alice')
      def step_i_know_alice(context):
          pass
      """
    And a file named "features/steps/foo/bob_steps.py" with:
      """
      from behave import step

      @step('I know Bob')
      def step_i_know_bob(context):
          pass
      """
    And a file named "features/use_substeps1.feature" with:
      """
      Feature:
        Scenario:
          Given I know Alice
          And I know Bob
      """
    When I run "behave features/use_substeps1.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature:  # features/use_substeps1.feature:1
        Scenario:            # features/use_substeps1.feature:2
          Given I know Alice # features/steps/alice_steps.py:3
          And I know Bob     # features/steps/foo/bob_steps.py:3
      """


  Scenario: Use two substep directories
    Given a file named "features/steps/alice_steps.py" with:
      """
      from behave import step

      @step('I know Alice')
      def step_i_know_alice(context):
          pass
      """
    And a file named "features/steps/foo/bob_steps.py" with:
      """
      from behave import step

      @step('I know Bob')
      def step_i_know_bob(context):
          pass
      """
    And a file named "features/steps/bar/baz/charly_steps.py" with:
      """
      from behave import step

      @step('I know Charly2')
      def step_i_know_charly2(context):
          pass
      """
    And a file named "features/use_substeps2.feature" with:
      """
      Feature:
        Scenario:
          Given I know Alice
          And I know Bob
          And I know Charly2
      """
    When I run "behave features/use_substeps2.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature:  # features/use_substeps2.feature:1
        Scenario:            # features/use_substeps2.feature:2
          Given I know Alice # features/steps/alice_steps.py:3
          And I know Bob     # features/steps/foo/bob_steps.py:3
          And I know Charly2 # features/steps/bar/baz/charly_steps.py:3
      """

  Scenario: Use one substep package directory

    Ensure that a dummy "__init__.py" does not cause any problems.

    Given a file named "features/steps/alice_steps.py" with:
      """
      from behave import step

      @step('I know Alice')
      def step_i_know_alice(context):
          pass
      """
    And an empty file named "features/steps/foo/__init__.py"
    And a file named "features/steps/foo/bob_steps.py" with:
      """
      from behave import step

      @step('I know Bobby')
      def step_i_know_bob(context):
          pass
      """
    And a file named "features/use_substeps3.feature" with:
      """
      Feature:
        Scenario:
          Given I know Alice
          And I know Bobby
      """
    When I run "behave features/use_substeps3.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    And the command output should contain:
      """
      Feature:  # features/use_substeps3.feature:1
        Scenario:            # features/use_substeps3.feature:2
          Given I know Alice # features/steps/alice_steps.py:3
          And I know Bobby   # features/steps/foo/bob_steps.py:3
      """
