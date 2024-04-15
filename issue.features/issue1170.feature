@issue
Feature: Issue #1170 -- Tag Expression Auto Detection Problem

  . DESCRIPTION OF SYNDROME (OBSERVED BEHAVIOR):
  . TagExpression v2 wildcard matching does not work if one dashed-tag is used.
  .
  . WORKAROUND:
  . * Use TagExpression auto-detection in strict mode


  Background: Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from __future__ import absolute_import
      import behave4cmd0.passing_steps
      """
    And a file named "features/syndrome_1170.feature" with:
      """
      Feature: F1

        @file-test_1
        Scenario: S1
          Given a step passes

        @file-test_2
        Scenario: S2
          When another step passes

        Scenario: S3 -- Untagged
          Then some step passes
      """

  @xfailed
  Scenario: Use one TagExpression Term with Wildcard -- BROKEN
    When I run `behave --tags="file-test*" features/syndrome_1170.feature`
    Then it should pass with:
      """
      0 features passed, 0 failed, 1 skipped
      0 scenarios passed, 0 failed, 3 skipped
      """
    And note that "TagExpression auto-detection seems to select TagExpressionV1"
    And note that "no scenarios is selected/executed"
    But note that "first two scenarios should have been executed"


  Scenario: Use one TagExpression Term with Wildcard -- Strict Mode
    Given a file named "behave.ini" with:
      """
      # -- ENSURE: Only TagExpression v2 is used (with auto-detection in strict mode)
      [behave]
      tag_expression_protocol = strict
      """
    When I run `behave --tags="file-test*" features/syndrome_1170.feature`
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 1 skipped
      """
    And note that "TagExpression auto-detection seems to select TagExpressionV2"
    And note that "first two scenarios are selected/executed"
