@issue
Feature: Issue #191 Using context.execute_steps() may change context.table/.text

  . PROBLEM DESCRIPTION:
  . When you execute nested steps via "context.execute_steps()" in a
  . step implementation, the following context attributes of the current step
  . may be modified and may be longer valid:
  .   * context.text (multi-line text)
  .   * context.table


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/common_steps.py" with:
        """
        from behave import given, step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass

        @given('I define the following nested steps')
        def step_define_nested_steps(context):
            assert context.text is not None, "REQUIRE: text"
            context.nested_steps = context.text
        """
    And a file named "features/steps/table_steps.py" with:
        """
        from behave import when, then, step

        @step('I use another table with')
        def step_use_another_table_with(context):
            assert context.table, "REQUIRE: table"
            context.nested_table = context.table

        @when('I execute the nested steps and use the table')
        def step_execute_nested_steps_and_use_table(context):
            assert context.table, "REQUIRE: table"
            assert context.nested_steps, "REQUIRE: context.nested_steps"
            context.my_table1 = context.table
            context.execute_steps(context.nested_steps)
            context.my_table2 = context.table

        @then('the original table is restored after the nested steps are executed')
        def step_table_is_restored(context):
            assert context.my_table1 is not None
            assert context.my_table2 is not None
            assert context.my_table1 is context.my_table2
        """
    And a file named "features/steps/text_steps.py" with:
        """
        from behave import when, then, step

        @step('I use another step with text "{text}"')
        def step_use_another_text_with(context, text):
            assert context.text is None
            context.text = text     # -- MODIFY: context.text (emulation)

        @step('I use another text with')
        def step_use_another_text_with(context):
            assert context.text is not None, "REQUIRE: text"
            context.nested_text = context.text

        @when('I execute the nested steps and use the text')
        def step_execute_nested_steps_and_use_text(context):
            assert context.text is not None, "REQUIRE: text"
            assert context.nested_steps, "REQUIRE: context.nested_steps"
            context.my_text1 = context.text
            context.execute_steps(context.nested_steps)
            context.my_text2 = context.text

        @then('the original text is restored after the nested steps are executed')
        def step_text_is_restored(context):
            assert context.my_text1 is not None
            assert context.my_text2 is not None
            assert context.my_text1 is context.my_text2
        """

  @nested_steps.with_table
  Scenario: After executing simple nested steps the original table is restored
    Given a file named "features/example.nested_simple_steps_and_table.feature" with:
        """
        Feature:
          Scenario:
            Given I define the following nested steps:
                '''
                Given a step passes
                When another step passes
                '''
            When I execute the nested steps and use the table:
                | Name   | Age |
                | Alice  | 21  |
                | Bob    | 32  |
            Then the original table is restored after the nested steps are executed
        """
    When I run "behave -f plain -T features/example.nested_simple_steps_and_table.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  @nested_steps.with_table
  Scenario: After executing nested steps with a table the original table is restored
    Given a file named "features/example.nested_steps_and_table.feature" with:
        """
        Feature:
          Scenario:
            Given I define the following nested steps:
                '''
                Given I use another table with:
                    | Person | Registered |
                    | Anton  | true  |
                    | Barby  | false |
                '''
            When I execute the nested steps and use the table:
                | Name   | Age |
                | Charly | 41  |
                | Doro   | 52  |
            Then the original table is restored after the nested steps are executed
        """
    When I run "behave -f plain -T features/example.nested_steps_and_table.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """


  @nested_steps.with_text
  Scenario: After executing simple nested steps the original text is restored
    Given a file named "features/example.nested_simple_steps_and_text.feature" with:
        """
        Feature:
          Scenario:
            Given I define the following nested steps:
                '''
                Given a step passes
                When another step passes
                '''
            When I execute the nested steps and use the text:
                '''
                Lorem ipsum
                Ipsum lorem
                '''
            Then the original text is restored after the nested steps are executed
        """
    When I run "behave -f plain -T features/example.nested_simple_steps_and_text.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  @nested_steps.with_text
  Scenario: After executing nested steps with a text the original text is restored
    Given a file named "features/example.nested_steps_and_text.feature" with:
        """
        Feature:
          Scenario:
            Given I define the following nested steps:
                '''
                Given I use another step with text "Hello Alice"
                '''
            When I execute the nested steps and use the text:
                '''
                Lorem ipsum
                Ipsum lorem
                '''
            Then the original text is restored after the nested steps are executed
        """
    When I run "behave -f plain -T features/example.nested_steps_and_text.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
