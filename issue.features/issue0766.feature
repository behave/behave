@issue
@not_reproducible
Feature: Issue #766 -- UnicodeEncodeError in PrettyFormatter

  Explore the described problem.

  Scenario Outline:
    Given a step with name="<name>"

    Examples:
      | name | value | comment |
      | 😄   | 123   | Use emoticon (smiley) in a table |

  Scenario:
    Given a step with table data:
      | name | value | comment |
      | 😄   | 123   | Use emoticon (smiley) in a table |

  Scenario: Explore problem by using the pretty formatter
    Given a new working directory
    And a file named "features/syndrome_766.feature" with:
      """
      Feature: Alice
        Scenario Outline:
          Given a step with name="<name>"

          Examples:
            | name | value | comment |
            | 😄   | 123   | Use emoticon (smiley) in a table |
      """
    And a file named "features/steps/issue766_steps.py" with:
      """
      from behave import given

      @given(u'a step with name="{name}"')
      def step_with_table_data(ctx, name):
          pass
      """
    When I run "behave -f pretty features/syndrome_766.feature"
    Then it should pass with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefine
      """
    And the command output should not contain "UnicodeEncodeError"
    And the command output should not contain "Traceback"
