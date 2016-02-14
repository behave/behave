@issue
Feature: Issue #302: Cannot escape pipe in table field value

  Support escaped-pipe characters in cells of a table.

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import then, step
        from hamcrest import assert_that, equal_to

        @step(u'I use table data with')
        def step_use_table_data_with_table(context):
            assert context.table, "REQUIRE: context.table is provided"
            context.table.require_columns(["name", "value"])

            context.table_data = {}
            for row in context.table.rows:
                name = row["name"]
                value = row["value"]
                context.table_data[name] = value

        @then(u'table data "{name}" is "{value}"')
        def step_table_data_name_is_value(context, name, value):
            table_data = context.table_data
            actual_value = table_data[name]
            assert_that(actual_value, equal_to(value))
        """

  Scenario: Escaped-pipes in table cell
    Given a file named "features/issue0302_example.feature" with:
        """
        Feature:
            Scenario: Use a table
             Given I use table data with:
                 | name  | value |
                 | alice | one\|two\|three\|four  |
             Then table data "alice" is "one|two|three|four"
        """
    When I run "behave -f plain features/issue0302_example.feature"
    Then it should pass
    And the command output should not contain:
        """
        Traceback (most recent call last):
        """


  Scenario: Leading escaped-pipe in table cell
    Given a file named "features/issue0302_example2.feature" with:
        """
        Feature:
            Scenario: Use a table
             Given I use table data with:
                 | name  | value |
                 | bob   |\|one  |
             Then table data "bob" is "|one"
        """
    When I run "behave -f plain features/issue0302_example2.feature"
    Then it should pass


  Scenario: Trailing escaped-pipe in table cell
    Given a file named "features/issue0302_example3.feature" with:
        """
        Feature:
            Scenario: Use a table
             Given I use table data with:
                 | name   | value |
                 | charly | one\||
             Then table data "charly" is "one|"
        """
    When I run "behave -f plain features/issue0302_example3.feature"
    Then it should pass


  Scenario: Double escaped-pipe in table cell
    Given a file named "features/issue0302_example4.feature" with:
        """
        Feature:
            Scenario: Use a table
             Given I use table data with:
                 | name   | value |
                 | doro   | one\\|two |
             Then table data "doro" is "one\|two"
        """
    When I run "behave -f plain features/issue0302_example4.feature"
    Then it should pass


