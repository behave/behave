@issue
Feature: Issue #1170 -- Tag Expression Auto Detection Problem

  . DESCRIPTION OF SYNDROME (OBSERVED BEHAVIOR):
  . TagExpression v2 wildcard matching does not work if one dashed-tag is used.
  .
  . WORKAROUND-UNTIL-FIXED:
  . * Use TagExpression auto-detection in v2 mode (or strict mode)


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


  Scenario: Use one TagExpression Term with Wildcard in default mode (AUTO-DETECT)
    When I run `behave --tags="file-test*" features/syndrome_1170.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 1 skipped
      """
    And note that "TagExpression auto-detection should to select TagExpressionV2"
    And note that "first two scenarios should have been executed"
    But note that "last scenario should be skipped"


  Scenario: Use one TagExpression Term with Wildcard in AUTO Mode (explicit: auto-detect)
    Given a file named "behave.ini" with:
      """
      # -- ENSURE: Use TagExpression v1 or v2 (with auto-detection)
      [behave]
      tag_expression_protocol = auto_detect
      """
    When I run `behave --tags="file-test*" features/syndrome_1170.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 1 skipped
      """
    And note that "TagExpression auto-detection should to select TagExpressionV2"
    And note that "first two scenarios should have been executed"
    But note that "last scenario should be skipped"


  Scenario: Use one TagExpression Term with Wildcard in V2 Mode
    Given a file named "behave.ini" with:
      """
      # -- ENSURE: Only TagExpressions v2 is used
      [behave]
      tag_expression_protocol = v2
      """
    When I run `behave --tags="file-test*" features/syndrome_1170.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 1 skipped
      """
    And note that "TagExpressions v2 are used"
    And note that "first two scenarios are selected/executed"


  Scenario: Use one TagExpression Term with Wildcard in STRICT Mode
    Given a file named "behave.ini" with:
      """
      # -- ENSURE: Only TagExpressions v2 is used with strict mode
      [behave]
      tag_expression_protocol = strict
      """
    When I run `behave --tags="file-test*" features/syndrome_1170.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 1 skipped
      """
    And note that "TagExpressions v2 are used"
    And note that "first two scenarios are selected/executed"
