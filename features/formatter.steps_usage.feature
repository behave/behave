@sequential
Feature: Steps Usage Formatter

    As a test writer
    I want to get an overview which step definitions are used and where
    To simplify the refactoring of step definitions (and features).

    | SOLUTION: Use StepsUsageFormatter in dry-run mode, like:
    |
    |       behave --dry-run -f steps.usage features/
    |
    | NOTE: This formatter corresponds to the "usage" formatter in cucumber.


    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/passing_steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass
            """
        And a file named "features/steps/unused_steps.py" with:
            """
            from behave import step

            @step('an unused step')
            def step_unused(context):
                pass

            @step('another unused step')
            def step_another_unused(context):
                pass
            """
        And a file named "features/steps/alice_steps.py" with:
            """
            from behave import given, when, then

            @given('{person} lives in {city}')
            def step_given_person_lives_in_city(context, person, city):
                pass

            @when('I visit {person}')
            def step_when_visit_person(context, person):
                pass

            @then('I meet {person} in {city}')
            def step_then_meet_person_in_city(context, person, city):
                pass
            """
        And a file named "features/steps/charly_steps.py" with:
            """
            from behave import given, when, then

            @given('{person} works for {company}')
            def step_given_person_works_for_company(context, person, company):
                pass

            @when('I plan a meeting with {person}')
            def step_when_plan_meeting_with_person(context, person):
                pass

            @then('I meet him at the {company} office')
            def step_then_meet_him_at_company_office(context, company):
                pass
            """
        And a file named "features/alice.feature" with:
            """
            Feature:
              Scenario: Visit Alice
                Given Alice lives in Paris
                When I visit Alice
                Then I meet Alice in Paris

              Scenario: Visit Bob
                Given Bob lives in Berlin
                When I visit Bob
                Then I meet Bob in Berlin
            """
        And a file named "features/bob.feature" with:
            """
            Feature:
              Scenario: Visit Bob
                Given Bob lives in Barcelona
                When I visit Bob
                Then I meet Bob in Barcelona
                And a step passes
            """
        And a file named "features/charly.feature" with:
            """
            Feature:
              Scenario: Meeting with Charly
                Given Charly works for ACME
                When I plan a meeting with Charly
                Then I meet him at the ACME office
            """


    @usecase.primary
    Scenario: Show step definitions usage with all features in dry-run mode
        When I run "behave --dry-run -f steps.usage features/"
        Then it should pass with:
          """
          @given('{person} lives in {city}')        # features/steps/alice_steps.py:3
            Given Alice lives in Paris              # features/alice.feature:3
            Given Bob lives in Berlin               # features/alice.feature:8
            Given Bob lives in Barcelona            # features/bob.feature:3

          @when('I visit {person}')                 # features/steps/alice_steps.py:7
            When I visit Alice                      # features/alice.feature:4
            When I visit Bob                        # features/alice.feature:9
            When I visit Bob                        # features/bob.feature:4

          @then('I meet {person} in {city}')        # features/steps/alice_steps.py:11
            Then I meet Alice in Paris              # features/alice.feature:5
            Then I meet Bob in Berlin               # features/alice.feature:10
            Then I meet Bob in Barcelona            # features/bob.feature:5

          @given('{person} works for {company}')    # features/steps/charly_steps.py:3
            Given Charly works for ACME             # features/charly.feature:3

          @when('I plan a meeting with {person}')   # features/steps/charly_steps.py:7
            When I plan a meeting with Charly       # features/charly.feature:4

          @then('I meet him at the {company} office')  # features/steps/charly_steps.py:11
            Then I meet him at the ACME office         # features/charly.feature:5

          @step('a step passes')                    # features/steps/passing_steps.py:3
            And a step passes                       # features/bob.feature:6

          UNUSED STEP DEFINITIONS[2]:
            @step('an unused step')                 # features/steps/unused_steps.py:3
            @step('another unused step')            # features/steps/unused_steps.py:7
          """
        And note that "the UNUSED STEP DEFINITIONS are ordered by file location"
        But note that "step definitions from unused_steps.py are not used by any feature"


    @usecase.primary
    Scenario: Show step definitions usage with one feature (dry-run mode)
        When I run "behave --dry-run -f steps.usage features/alice.feature"
        Then it should pass with:
          """
          @given('{person} lives in {city}')        # features/steps/alice_steps.py:3
            Given Alice lives in Paris              # features/alice.feature:3
            Given Bob lives in Berlin               # features/alice.feature:8

          @when('I visit {person}')                 # features/steps/alice_steps.py:7
            When I visit Alice                      # features/alice.feature:4
            When I visit Bob                        # features/alice.feature:9

          @then('I meet {person} in {city}')        # features/steps/alice_steps.py:11
            Then I meet Alice in Paris              # features/alice.feature:5
            Then I meet Bob in Berlin               # features/alice.feature:10

          UNUSED STEP DEFINITIONS[6]:
            @given('{person} works for {company}')       # features/steps/charly_steps.py:3
            @when('I plan a meeting with {person}')      # features/steps/charly_steps.py:7
            @then('I meet him at the {company} office')  # features/steps/charly_steps.py:11
            @step('a step passes')                       # features/steps/passing_steps.py:3
            @step('an unused step')                      # features/steps/unused_steps.py:3
            @step('another unused step')                 # features/steps/unused_steps.py:7
          """
        But note that "step definitions from charly_steps.py, passing_steps.py are now no longer used"


    @usecase.primary
    Scenario: Show step definitions usage with two features (dry-run mode)
        When I run "behave --dry-run -f steps.usage features/alice.feature features/charly.feature"
        Then it should pass with:
          """
          @given('{person} lives in {city}')        # features/steps/alice_steps.py:3
            Given Alice lives in Paris              # features/alice.feature:3
            Given Bob lives in Berlin               # features/alice.feature:8

          @when('I visit {person}')                 # features/steps/alice_steps.py:7
            When I visit Alice                      # features/alice.feature:4
            When I visit Bob                        # features/alice.feature:9

          @then('I meet {person} in {city}')        # features/steps/alice_steps.py:11
            Then I meet Alice in Paris              # features/alice.feature:5
            Then I meet Bob in Berlin               # features/alice.feature:10

          @given('{person} works for {company}')    # features/steps/charly_steps.py:3
            Given Charly works for ACME             # features/charly.feature:3

          @when('I plan a meeting with {person}')   # features/steps/charly_steps.py:7
            When I plan a meeting with Charly       # features/charly.feature:4

          @then('I meet him at the {company} office')  # features/steps/charly_steps.py:11
            Then I meet him at the ACME office         # features/charly.feature:5

          UNUSED STEP DEFINITIONS[3]:
            @step('a step passes')                  # features/steps/passing_steps.py:3
            @step('an unused step')                 # features/steps/unused_steps.py:3
            @step('another unused step')            # features/steps/unused_steps.py:7
          """
        But note that "step definitions from passing_steps.py, unused_steps.py are not used by any feature"


    @usecase.secondary
    Scenario: Show step definitions usage with all features in normal mode
        When I run "behave -f steps.usage features/"
        Then it should pass with:
          """
          @given('{person} lives in {city}')        # features/steps/alice_steps.py:3
            Given Alice lives in Paris              # features/alice.feature:3
            Given Bob lives in Berlin               # features/alice.feature:8
            Given Bob lives in Barcelona            # features/bob.feature:3

          @when('I visit {person}')                 # features/steps/alice_steps.py:7
            When I visit Alice                      # features/alice.feature:4
            When I visit Bob                        # features/alice.feature:9
            When I visit Bob                        # features/bob.feature:4

          @then('I meet {person} in {city}')        # features/steps/alice_steps.py:11
            Then I meet Alice in Paris              # features/alice.feature:5
            Then I meet Bob in Berlin               # features/alice.feature:10
            Then I meet Bob in Barcelona            # features/bob.feature:5

          @given('{person} works for {company}')    # features/steps/charly_steps.py:3
            Given Charly works for ACME             # features/charly.feature:3

          @when('I plan a meeting with {person}')   # features/steps/charly_steps.py:7
            When I plan a meeting with Charly       # features/charly.feature:4

          @then('I meet him at the {company} office')  # features/steps/charly_steps.py:11
            Then I meet him at the ACME office         # features/charly.feature:5

          @step('a step passes')                    # features/steps/passing_steps.py:3
            And a step passes                       # features/bob.feature:6

          UNUSED STEP DEFINITIONS[2]:
            @step('an unused step')                 # features/steps/unused_steps.py:3
            @step('another unused step')            # features/steps/unused_steps.py:7
          """

    @corner.case
    Scenario: StepsUsageFormatter shows undefined steps
        Given a file named "features/undefined.feature" with:
          """
          Feature: With undefined steps
            Scenario:
              Given a step is undefined
              Then another step is undefined
          """
        When I run "behave --dry-run -f steps.usage features/alice.feature features/undefined.feature"
        Then it should fail with:
          """
          0 features passed, 0 failed, 0 skipped, 2 untested
          0 scenarios passed, 0 failed, 0 skipped, 3 untested
          0 steps passed, 0 failed, 0 skipped, 2 undefined, 6 untested
          """
        And the command output should contain:
          """
          @given('{person} lives in {city}')        # features/steps/alice_steps.py:3
            Given Alice lives in Paris              # features/alice.feature:3
            Given Bob lives in Berlin               # features/alice.feature:8

          @when('I visit {person}')                 # features/steps/alice_steps.py:7
            When I visit Alice                      # features/alice.feature:4
            When I visit Bob                        # features/alice.feature:9

          @then('I meet {person} in {city}')        # features/steps/alice_steps.py:11
            Then I meet Alice in Paris              # features/alice.feature:5
            Then I meet Bob in Berlin               # features/alice.feature:10

          UNUSED STEP DEFINITIONS[6]:
            @given('{person} works for {company}')       # features/steps/charly_steps.py:3
            @when('I plan a meeting with {person}')      # features/steps/charly_steps.py:7
            @then('I meet him at the {company} office')  # features/steps/charly_steps.py:11
            @step('a step passes')                       # features/steps/passing_steps.py:3
            @step('an unused step')                      # features/steps/unused_steps.py:3
            @step('another unused step')                 # features/steps/unused_steps.py:7

          UNDEFINED STEPS[2]:
            Given a step is undefined               # features/undefined.feature:3
            Then another step is undefined          # features/undefined.feature:4
          """

