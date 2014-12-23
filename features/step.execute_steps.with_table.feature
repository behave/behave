Feature: Execute nested steps that use a table

  Scenario:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then, step
      import six
      @given('the following nested steps')
      def step_given_following_nested_steps(context):
          assert context.text, "ENSURE: multi-line text is provided."
          context.nested_steps = six.text_type(context.text)

      @step('I execute the nested steps {comment}')
      def step_execute_nested_steps_with_table(context, comment):
          assert context.nested_steps, "ENSURE: nested steps are provided."
          context.execute_steps(context.nested_steps)

      @then('the step "{expected_step}" was called')
      def then_step_was_called(context, expected_step):
          assert context.steps_called, "ENSURE: steps_called is provided."
          assert expected_step in context.steps_called

      @then('the table should be equal to')
      def then_table_should_be_equal_to(context):
          assert context.table, "ENSURE: table is provided."
          expected_table = context.table
          actual_table   = context.the_table
          assert actual_table == expected_table

      # -- SPECIAL-STEP:
      @step('I setup an address book with')
      def step_setup_address_book_with_friends(context):
          assert context.table, "ENSURE: table is provided."
          if not hasattr(context, "steps_called"):
              context.steps_called = []
          context.steps_called.append("I setup an address book with")
          context.the_table = context.table
      """
    And a file named "features/execute_nested_steps_with_table.feature" with:
      '''
      Feature:
        Scenario:
          Given the following nested steps:
            """
            When I setup an address book with:
              | Name  | Telephone Number |
              | Alice | 555 1111         |
              | Bob   | 555 2222         |
            """
          When I execute the nested steps with a table
          Then the step "I setup an address book with" was called
          And  the table should be equal to:
              | Name  | Telephone Number |
              | Alice | 555 1111         |
              | Bob   | 555 2222         |
      '''
    When I run "behave -f plain features/execute_nested_steps_with_table.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped, 0 undefined
        """

