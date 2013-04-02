@issue
@not_reproducible
Feature: Issue #142: --junit flag fails to output with step table data: TypeError: <Row [u'data', u'value']> is not JSON serializable

      DUPLICATES: issue #67 (already fixed).

  Scenario:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import given, when, then, step

        @then('use table data with')
        def step_impl(context):
            pass
        """
    And a file named "features/issue0142_example.feature" with:
        """
        Feature:
            Scenario: Use a table
             Then use table data with:
                 | data                             | value |
                 | behave outputs junit with tables | false |
        """
    When I run "behave --junit -f json features/issue0142_example.feature"
    Then it should pass
    But the command output should not contain:
        """
        TypeError: <Row [u'behave outputs junit with tables', u'false']> is not JSON serializable
        """
    And the command output should not contain:
        """
        Traceback (most recent call last):
        """



