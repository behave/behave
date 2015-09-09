@issue
@not_reproducible
Feature: Issue #302: Cannot escape pipe in table field value


  Scenario:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import given, when, then, step

        @then('use table data with')
        def step_impl(context):
            assert context.table.rows[0].cells[0] == "one|two|three|four"
        """
    And a file named "features/issue0302_example.feature" with:
        """
        Feature:
            Scenario: Use a table
             Then use table data with:
                 | data                  | value |
                 | one\|two\|three\|four | false |
        """
    When I run "behave -f json features/issue0302_example.feature"
    Then it should pass
    And the command output should not contain:
        """
        Traceback (most recent call last):
        """



