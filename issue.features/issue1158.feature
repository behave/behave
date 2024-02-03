@issue @mistaken
Feature: Issue #1158 -- ParseMatcher failing on steps with type annotations

  . DESCRIPTION OF SYNDROME (OBSERVED BEHAVIOR):
  .  * AmbiguousStep exception occurs when using the ParseMatcher
  .  * MISTAKEN: No such problem exists
  .  * PROBABLY: Error on the user side

  Scenario: Check Syndrome
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from __future__ import absolute_import, print_function
      from behave import then, register_type, use_step_matcher
      from parse_type import TypeBuilder
      from enum import Enum

      class CommunicationState(Enum):
          ALIVE = 1
          SUSPICIOUS = 2
          DEAD = 3
          UNKNOWN = 4

      parse_communication_state = TypeBuilder.make_enum(CommunicationState)
      register_type(CommunicationState=parse_communication_state)
      use_step_matcher("parse")

      @then(u'the SCADA reports that the supervisory controls communication status is {com_state:CommunicationState}')
      def step1_reports_communication_status(ctx, com_state):
          print("STEP_1: com_state={com_state}".format(com_state=com_state))

      @then(u'the SCADA finally reports that the supervisory controls communication status is {com_state:CommunicationState}')
      def step2_finally_reports_communication_status(ctx, com_state):
          print("STEP_2: com_state={com_state}".format(com_state=com_state))
      """
    And a file named "features/syndrome_1158.feature" with:
      """
      Feature: F1
        Scenario Outline: STEP_1 and STEP_2 with com_state=<communication_state>
          Then the SCADA reports that the supervisory controls communication status is <communication_state>
          And  the SCADA finally reports that the supervisory controls communication status is <communication_state>

          Examples:
            | communication_state |
            | ALIVE       |
            | SUSPICIOUS  |
            | DEAD        |
            | UNKNOWN     |
      """
    When I run "behave features/syndrome_1158.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      4 scenarios passed, 0 failed, 0 skipped
      8 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "AmbiguousStep"
