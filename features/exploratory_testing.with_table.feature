Feature: Exploratory Testing with Tables and Table Annotations

   As a tester
   I want sometimes to explore a problem domain
   And see not only the expected results
   But also the actual results in a table.

    . HINT: Does not work with monochrome format in pretty formatter:
    .   behave -f pretty --no-color ...
    .   behave -c ...


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And   a file named "features/steps/explore_with_table_steps.py" with:
      """
      from behave import given, when, then, step

      database = {
          "Alice": { "age": 10 },
          "Bob":   { "age": 11 },
      }

      @when('I query the database with')
      def step_query_database_and_update_table(context):
          assert context.table, "REQUIRE: table"
          context.table.require_column("Name")
          age_index = context.table.ensure_column_exists("Age")
          for index, row in enumerate(context.table.rows):
              name = row["Name"]
              person = database.get(name, None)
              if person:
                  row.cells[age_index] = str(person["age"])
          context.current_table = context.table

      @when('I add {number:n} to column "{column}"')
      def step_query_and_annotate_database(context, number, column):
          assert context.current_table, "REQUIRE: current_table"
          age_index = context.current_table.ensure_column_exists("Age")
          for row in context.current_table.rows:
              value = int(row.cells[age_index]) or 0
              row.cells[age_index] = str(value + number)

      @step('note that the "{name}" column was added to the table')
      def step_note_that_column_was_added(context, name):
          assert context.current_table.has_column(name)

      @then('note that the "{name}" column was modified in the table')
      def step_note_that_column_was_modified(context, name):
          pass

      @then('I inspect the table')
      def step_inspect_table(context):
          assert context.current_table
          context.table = context.current_table

      @then('the table contains')
      def step_inspect_table(context):
          assert context.table, "REQUIRE: table"
          assert context.current_table, "REQUIRE: current_table"
          assert context.table == context.current_table
      """


    Scenario: Add table column with new data in a step and ensure changes are shown
      Given a file named "features/table.set_column_data.feature" with:
        """
        Feature:
          Scenario:
            When I query the database with:
              | Name  |
              | Alice |
              | Bob   |
            Then note that the "Age" column was added to the table
        """
      When I run "behave -f plain features/table.set_column_data.feature"
      Then it should pass with:
         """
         1 scenario passed, 0 failed, 0 skipped
         2 steps passed, 0 failed, 0 skipped, 0 undefined
         """
      And the command output should contain:
         """
         | Name  | Age |
         | Alice | 10  |
         | Bob   | 11  |
         """
      But note that "the Age table column was added by the step"


    Scenario: Modify table cells in a column and ensure changes are shown
      Given a file named "features/table.modify_column.feature" with:
        """
        Feature:
          Scenario:
            When I query the database with:
               | Name  | Age  |
               | Alice | 222  |
               | Bob   | 333  |
            Then note that the "Age" column was modified in the table
            Then the table contains:
               | Name  | Age |
               | Alice | 10  |
               | Bob   | 11  |
        """
      When I run "behave -f plain features/table.modify_column.feature"
      Then it should pass with:
         """
         1 scenario passed, 0 failed, 0 skipped
         3 steps passed, 0 failed, 0 skipped, 0 undefined
         """
      And the command output should contain:
         """
         | Name  | Age |
         | Alice | 10  |
         | Bob   | 11  |
         """
      But note that "the Age column was modified in the table"
      And the command output should not contain:
         """
         | Name  | Age |
         | Alice | 222 |
         | Bob   | 333 |
         """


    Scenario: Modify table cells in a column (formatter=pretty with colors)
      When I run "behave -f pretty features/table.modify_column.feature"
      Then it should pass with:
         """
         1 scenario passed, 0 failed, 0 skipped
         3 steps passed, 0 failed, 0 skipped, 0 undefined
         """
      And the command output should contain:
         """
         | Name  | Age |
         | Alice | 10  |
         | Bob   | 11  |
         """
      But note that "the Age column was modified in the table"
