@sequential
Feature: StepWithCode Formatter

  As a tester
  I want to know which python code is executed
  when I run my scenario steps in a Gherkin file (aka: Feature file)
  So that I can better understand how everything fits together
  And that I can inspected the step-definition source code parts

  NOTE: Primarily intended for dry-run mode.

  Rule: Good Cases
    Background: Feature Setup
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with:
          """
          from behave import step

          @step(u'{word:w} step passes')
          def step_passes(ctx, word):
              pass
          """
      And an empty file named "example4me/__init__.py"
      And a file named "example4me/calculator.py" with:
          """
          class Calculator(object):
              def __init__(self, initial_value=0):
                  self.initial_value = initial_value
                  self.result = initial_value

              def clear(self):
                  self.initial_value = 0
                  self.result = 0

              def add(self, number):
                  self.result += number
          """
      And a file named "example4me/calculator_steps.py" with:
          """
          from behave import given, when, then, step, register_type
          from behave.parameter_type import parse_number
          from example4me.calculator import Calculator
          from assertpy import assert_that

          register_type(Number=parse_number)

          @given(u'I use the calculator')
          def step_given_reset_calculator(ctx):
              ctx.calculator = Calculator()

          @when(u'I add the number "{number:Number}"')
          def step_when_add_number(ctx, number):
              ctx.calculator.add(number)

          @then(u'the calculator shows "{expected:Number}" as result')
          def step_when_add_number(ctx, expected):
              assert_that(ctx.calculator.result).is_equal_to(expected)
          """
      And a file named "features/steps/use_calculator_steps.py" with:
          """
          import example4me.calculator_steps
          """
      And a file named "features/calculator.feature" with:
          """
          Feature: Calculator
            Scenario: C1
              Given I use the calculator
              When I add the number "1"
              And  I add the number "2"
              Then the calculator shows "3" as result
          """

    Scenario: Use StepsWithCode formatter in dry-run mode
      When I run "behave -f steps.code --dry-run features/calculator.feature"
      Then it should pass with:
        """
        Feature: Calculator
          Scenario: C1
            Given I use the calculator
              # -- CODE: example4me/calculator_steps.py:8
              @given(u'I use the calculator')
              def step_given_reset_calculator(ctx):
                  ctx.calculator = Calculator()

            When I add the number "1"
              # -- CODE: example4me/calculator_steps.py:12
              @when(u'I add the number "{number:Number}"')
              def step_when_add_number(ctx, number):
                  ctx.calculator.add(number)

            And I add the number "2"
              # -- CODE: example4me/calculator_steps.py:12
              @when(u'I add the number "{number:Number}"')
              def step_when_add_number(ctx, number):
                  ctx.calculator.add(number)

            Then the calculator shows "3" as result
              # -- CODE: example4me/calculator_steps.py:16
              @then(u'the calculator shows "{expected:Number}" as result')
              def step_when_add_number(ctx, expected):
                  assert_that(ctx.calculator.result).is_equal_to(expected)
        """
      But note that "each steps contains a CODE section that shows the step implementation."

    Scenario: Use StepsWithCode formatter in normal mode
      When I run "behave -f steps.code features/calculator.feature"
      Then it should pass with:
        """
        Feature: Calculator
          Scenario: C1
            Given I use the calculator  ...  passed
              # -- CODE: example4me/calculator_steps.py:8
              @given(u'I use the calculator')
              def step_given_reset_calculator(ctx):
                  ctx.calculator = Calculator()

            When I add the number "1"  ...  passed
              # -- CODE: example4me/calculator_steps.py:12
              @when(u'I add the number "{number:Number}"')
              def step_when_add_number(ctx, number):
                  ctx.calculator.add(number)

            And I add the number "2"  ...  passed
              # -- CODE: example4me/calculator_steps.py:12
              @when(u'I add the number "{number:Number}"')
              def step_when_add_number(ctx, number):
                  ctx.calculator.add(number)

            Then the calculator shows "3" as result  ...  passed
              # -- CODE: example4me/calculator_steps.py:16
              @then(u'the calculator shows "{expected:Number}" as result')
              def step_when_add_number(ctx, expected):
                  assert_that(ctx.calculator.result).is_equal_to(expected)
        """
      But note that "each steps contains a CODE section that shows the step implementation"
      And note that "the step results are shown for each step (after execution)"

    Scenario: Use StepsWithCode formatter with step.table
      Given a file named "features/steps/table_steps.py" with:
        """
        from behave import given
        from assertpy import assert_that

        class Person(object):
            def __init__(self, name, role=None):
                self.name = name
                self.role = role

        @given(u'a company with the following persons')
        @given(u'a company with the following persons:')
        def step_given_company_with_persons(ctx):
            assert_that(ctx.table).is_not_none()
            company_persons = []
            for row in ctx.table.rows:
                name = row["Name"]
                role = row["Role"]
                person = Person(name, role)
                company_persons.append(person)
            ctx.company_persons = company_persons
        """
      And a file named "features/table_steps.feature" with:
        """
        Feature: step.table
          Scenario: S1
            Given a company with the following persons:
              | Name  | Role |
              | Alice | CEO  |
              | Bob   | Developer |
        """
      When I run "behave -f steps.code features/table_steps.feature"
      Then it should pass with:
        """
        Feature: step.table
          Scenario: S1
            Given a company with the following persons:  ...  passed
              | Name  | Role      |
              | Alice | CEO       |
              | Bob   | Developer |
              # -- CODE: features/steps/table_steps.py:9
              @given(u'a company with the following persons')
              @given(u'a company with the following persons:')
              def step_given_company_with_persons(ctx):
                  assert_that(ctx.table).is_not_none()
                  company_persons = []
                  for row in ctx.table.rows:
                      name = row["Name"]
                      role = row["Role"]
                      person = Person(name, role)
                      company_persons.append(person)
                  ctx.company_persons = company_persons
        """
      But note that "each steps contains a CODE section that shows the step implementation"
      And note that "the step results are shown for each step (after execution)"


    Scenario: Use StepsWithCode formatter with step.text
      Given a file named "features/steps/text_steps.py" with:
        """
        from behave import given
        from io import open

        @given(u'a special file named "{filename}" with')
        @given(u'a special file named "{filename}" with:')
        def step_given_file_named_with_contents(ctx, filename):
            with open(filename, "w+", encoding="UTF-8") as f:
                f.write(ctx.text)

            # -- ALTERNATIVE:
            # filename_path = Path(filename)
            # filename_path.write_text(ctx.text)
        """
      And a file named "features/text_steps.feature" with:
        '''
        Feature: step.text
          Scenario: T1
            Given a special file named "example.some_file.txt" with:
              """
              Lorem ipsum.
              Ipsum lorem ...
              """
        '''
      When I run "behave -f steps.code features/text_steps.feature"
      Then it should pass with:
        '''
        Feature: step.text
          Scenario: T1
            Given a special file named "example.some_file.txt" with:  ...  passed
              """
              Lorem ipsum.
              Ipsum lorem ...
              """
              # -- CODE: features/steps/text_steps.py:4
              @given(u'a special file named "{filename}" with')
              @given(u'a special file named "{filename}" with:')
              def step_given_file_named_with_contents(ctx, filename):
                  with open(filename, "w+", encoding="UTF-8") as f:
                      f.write(ctx.text)
     '''
      But note that "each steps contains a CODE section that shows the step implementation"
      And note that "the step results are shown for each step (after execution)"


    Scenario: Use StepsWithCode formatter with rule (in normal mode)
      Given a file named "features/with_rule.feature" with:
        """
        Feature: Calculator with Rule
          Rule: Some
            Scenario: R1
              Given I use the calculator
              When I add the number "42"
              Then the calculator shows "42" as result
        """
      When I run "behave -f steps.code features/with_rule.feature"
      Then it should pass with:
        """
        Feature: Calculator with Rule
          Rule: Some
            Scenario: R1
              Given I use the calculator  ...  passed
                # -- CODE: example4me/calculator_steps.py:8
                @given(u'I use the calculator')
                def step_given_reset_calculator(ctx):
                    ctx.calculator = Calculator()

              When I add the number "42"  ...  passed
                # -- CODE: example4me/calculator_steps.py:12
                @when(u'I add the number "{number:Number}"')
                def step_when_add_number(ctx, number):
                    ctx.calculator.add(number)

              Then the calculator shows "42" as result  ...  passed
                # -- CODE: example4me/calculator_steps.py:16
                @then(u'the calculator shows "{expected:Number}" as result')
                def step_when_add_number(ctx, expected):
                    assert_that(ctx.calculator.result).is_equal_to(expected)
        """
      But note that "each step is indented correctly"
      And note that "each step code-section is indented correctly"


    Scenario: Use StepsWithCode formatter with steps that have documentation
      INTENTION: step-function.__doc__ is not shown in code-section.

      Given a file named "features/steps/documented_steps.py" with:
        '''
        from behave import given, when, then
        from assertpy import assert_that

        @given(u'a person named "{name}"')
        def step_given_person_named(ctx, name):
            """
            __DOCSTRING_HERE: is not shown
            """
            # -- CODE: STARTS HERE.
            ctx.person_name = name

        @then(u'I have met "{expected}"')
        def step_then_met_person(ctx, expected):
            """__DOCSTRING_HERE: is not shown"""
            # -- CODE: STARTS HERE.
            assert_that(ctx.person_name).is_equal_to(expected)
        '''
      Given a file named "features/with_rule.feature" with:
        """
        Feature: Using steps with docstring (not shown)
          Scenario: D1
            Given a person named "Alice"
            Then I have met "Alice"
        """
      When I run "behave -f steps.code features/with_rule.feature"
      Then it should pass with:
        """
        Feature: Using steps with docstring (not shown)
          Scenario: D1
            Given a person named "Alice"  ...  passed
              # -- CODE: features/steps/documented_steps.py:4
              @given(u'a person named "{name}"')
              def step_given_person_named(ctx, name):
                  # -- CODE: STARTS HERE.
                  ctx.person_name = name
            Then I have met "Alice"  ...  passed
              # -- CODE: features/steps/documented_steps.py:12
              @then(u'I have met "{expected}"')
              def step_then_met_person(ctx, expected):
                  # -- CODE: STARTS HERE.
                  assert_that(ctx.person_name).is_equal_to(expected)
        """
      But note that "the step-function docstring is not shown in the code-section"


  Rule: Bad Cases
    Background: Feature Setup
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with:
          """
          from behave import step

          @step(u'{word:w} step passes')
          def step_passes(ctx, word):
              pass
          """
      And a file named "features/passing.feature" with:
          """
          Feature: Passing steps
            Scenario: P1
              Given a step passes
              When another step passes
          """

    Scenario: Use StepsWithCode formatter if some step fails
      Given a file named "features/steps/failing_steps.py" with:
          """
          from behave import step
          from assertpy import assert_that

          @step(u'{word:w} step fails')
          def step_fails(ctx, word):
              assert_that(word).is_equal_to("__ALWAYS_FAILS__")
          """
      Given a file named "features/failing.feature" with:
          """
          Feature: Failing step
            @problematic
            Scenario: F1 with failing step
              Given a step passes
              When another step fails
              Then another step passes
          """
      When I run "behave -f steps.code features/failing.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 1 skipped
        """
      And the command output should contain:
        """
        Feature: Failing step
          Scenario: F1 with failing step
            Given a step passes  ...  passed
              # -- CODE: features/steps/passing_steps.py:3
              @step(u'{word:w} step passes')
              def step_passes(ctx, word):
                  pass

            When another step fails  ...  failed
              # -- CODE: features/steps/failing_steps.py:4
              @step(u'{word:w} step fails')
              def step_fails(ctx, word):
                  assert_that(word).is_equal_to("__ALWAYS_FAILS__")

          Failing scenarios:
            features/failing.feature:3  F1 with failing step
        """
      But note that "the failing step is shown with code-section"
      And note that "the next steps after the failing step are not shown"


    Scenario: Use StepsWithCode formatter if some steps are undefined
      Given a file named "features/undefined.feature" with:
          """
          Feature: Undefined steps
            @problematic
            Scenario: With undefined step
              Given a step passes
              When a step is UNDEFINED
              Then another step passes
          """
      When I run "behave -f steps.code features/undefined.feature"
      Then it should fail with:
        """
        0 scenarios passed, 0 failed, 1 error, 0 skipped
        1 step passed, 0 failed, 1 skipped, 1 undefined
        """
      And the command output should contain:
        """
        Feature: Undefined steps
          Scenario: With undefined step
            Given a step passes  ...  passed
              # -- CODE: features/steps/passing_steps.py:3
              @step(u'{word:w} step passes')
              def step_passes(ctx, word):
                  pass

            When a step is UNDEFINED  ...  undefined

        Errored scenarios:
          features/undefined.feature:3  With undefined step
        """
      But note that "the undefined step is shown without code-section"
