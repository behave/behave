@sequential
Feature: Steps Formatter (Step Definitions Formatter)

    As a test writer
    I want to get a quick overview which step definitions exist
    To simplify the writing of feature tests.

    | SOLUTION: Use StepsFormatter in dry-run mode, like:
    |
    |       behave --dry-run -f steps features/
    |
    | NOTE: This formatter is similar to the "stepdefs" formatter in cucumber.


    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/passing_steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass

            @step('a step fails')
            def step_fails(context):
                assert False, "XFAIL-STEP"
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
        And a file named "features/steps/bob_steps.py" with:
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
        And an empty file named "features/none.feature"


    @usecase.primary
    Scenario: Show available step definitions in dry-run mode
        When I run "behave --dry-run -f steps features/"
        Then it should pass with:
          """
          GIVEN STEP DEFINITIONS[4]:
            Given {person} lives in {city}            # features/steps/alice_steps.py:3
            Given {person} works for {company}        # features/steps/bob_steps.py:3
            Given a step passes                       # features/steps/passing_steps.py:3
            Given a step fails                        # features/steps/passing_steps.py:7

          WHEN STEP DEFINITIONS[4]:
            When I visit {person}                     # features/steps/alice_steps.py:7
            When I plan a meeting with {person}       # features/steps/bob_steps.py:7
            When a step passes                        # features/steps/passing_steps.py:3
            When a step fails                         # features/steps/passing_steps.py:7

          THEN STEP DEFINITIONS[4]:
            Then I meet {person} in {city}            # features/steps/alice_steps.py:11
            Then I meet him at the {company} office   # features/steps/bob_steps.py:11
            Then a step passes                        # features/steps/passing_steps.py:3
            Then a step fails                         # features/steps/passing_steps.py:7

          GENERIC STEP DEFINITIONS[2]:
            * a step passes                           # features/steps/passing_steps.py:3
            * a step fails                            # features/steps/passing_steps.py:7
          """
        But note that "the GENERIC STEP DEFINITIONS can be used as given/when/then steps"


    @usecase.secondary
    Scenario: Show available step definitions in normal mode
        When I run "behave -f steps features/"
        Then it should pass with:
          """
          GIVEN STEP DEFINITIONS[4]:
            Given {person} lives in {city}            # features/steps/alice_steps.py:3
            Given {person} works for {company}        # features/steps/bob_steps.py:3
            Given a step passes                       # features/steps/passing_steps.py:3
            Given a step fails                        # features/steps/passing_steps.py:7

          WHEN STEP DEFINITIONS[4]:
            When I visit {person}                     # features/steps/alice_steps.py:7
            When I plan a meeting with {person}       # features/steps/bob_steps.py:7
            When a step passes                        # features/steps/passing_steps.py:3
            When a step fails                         # features/steps/passing_steps.py:7

          THEN STEP DEFINITIONS[4]:
            Then I meet {person} in {city}            # features/steps/alice_steps.py:11
            Then I meet him at the {company} office   # features/steps/bob_steps.py:11
            Then a step passes                        # features/steps/passing_steps.py:3
            Then a step fails                         # features/steps/passing_steps.py:7

          GENERIC STEP DEFINITIONS[2]:
            * a step passes                           # features/steps/passing_steps.py:3
            * a step fails                            # features/steps/passing_steps.py:7
          """


    @language
    Scenario: Show available step definitions for language=de (German)
        When I run "behave --dry-run -f steps --lang=de features/"
        Then it should pass with:
          """
          GIVEN STEP DEFINITIONS[4]:
            Angenommen {person} lives in {city}       # features/steps/alice_steps.py:3
            Angenommen {person} works for {company}   # features/steps/bob_steps.py:3
            Angenommen a step passes                  # features/steps/passing_steps.py:3
            Angenommen a step fails                   # features/steps/passing_steps.py:7

          WHEN STEP DEFINITIONS[4]:
            Wenn I visit {person}                     # features/steps/alice_steps.py:7
            Wenn I plan a meeting with {person}       # features/steps/bob_steps.py:7
            Wenn a step passes                        # features/steps/passing_steps.py:3
            Wenn a step fails                         # features/steps/passing_steps.py:7

          THEN STEP DEFINITIONS[4]:
            Dann I meet {person} in {city}            # features/steps/alice_steps.py:11
            Dann I meet him at the {company} office   # features/steps/bob_steps.py:11
            Dann a step passes                        # features/steps/passing_steps.py:3
            Dann a step fails                         # features/steps/passing_steps.py:7

          GENERIC STEP DEFINITIONS[2]:
            * a step passes                           # features/steps/passing_steps.py:3
            * a step fails                            # features/steps/passing_steps.py:7
          """
        But note that "this may fail depending on the language you use with your features"


    @language
    Scenario: Show available step definitions for language=fr (French)
        When I run "behave --dry-run -f steps --lang=fr features/"
        Then it should pass with:
          """
          GIVEN STEP DEFINITIONS[4]:
            Soit {person} lives in {city}             # features/steps/alice_steps.py:3
            Soit {person} works for {company}         # features/steps/bob_steps.py:3
            Soit a step passes                        # features/steps/passing_steps.py:3
            Soit a step fails                         # features/steps/passing_steps.py:7

          WHEN STEP DEFINITIONS[4]:
            Quand I visit {person}                    # features/steps/alice_steps.py:7
            Quand I plan a meeting with {person}      # features/steps/bob_steps.py:7
            Quand a step passes                       # features/steps/passing_steps.py:3
            Quand a step fails                        # features/steps/passing_steps.py:7

          THEN STEP DEFINITIONS[4]:
            Alors I meet {person} in {city}           # features/steps/alice_steps.py:11
            Alors I meet him at the {company} office  # features/steps/bob_steps.py:11
            Alors a step passes                       # features/steps/passing_steps.py:3
            Alors a step fails                        # features/steps/passing_steps.py:7

          GENERIC STEP DEFINITIONS[2]:
            * a step passes                           # features/steps/passing_steps.py:3
            * a step fails                            # features/steps/passing_steps.py:7
          """
        But note that "this may fail depending on the language you use with your features"
