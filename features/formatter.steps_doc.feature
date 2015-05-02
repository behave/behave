@sequential
Feature: Steps Doc Formatter

    As a test writer
    I want to get a quick overview how to use a step definition
    By reading the step definition documentation (doc-stings).

    . SOLUTION: Use StepsDocFormatter in dry-run mode, like:
    .
    .       behave --dry-run -f steps.doc features/


    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/passing_steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                '''This step always passes.'''
                pass

            @step('a step fails')
            def step_fails(context):
                '''This step is expected to fail.'''
                assert False, "XFAIL-STEP"
            """
        And a file named "features/steps/alice_steps.py" with:
            """
            from behave import given, when, then

            @given('{person} lives in {city}')
            def step_given_person_lives_in_city(context, person, city):
                '''
                Setup the data where a person lives and store in the database.

                :param person:  Person's name (as string).
                :param city:    City where the person lives (as string).
                '''
                database = getattr(context, "database", None)
                if not database:
                    context.database = {}
                context.database[person] = { "city": city }

            @when('I visit {person}')
            def step_when_visit_person(context, person):
                # -- NO DOC-STRING.
                pass

            @then('I meet {person} in {city}')
            def step_then_meet_person_in_city(context, person, city):
                '''
                Checks if I can meet the person in the expected city.

                :param person:  Person's name as key (as string).
                :param city:    Expected city (as string).
                '''
                person_data = context.database.get(person, None)
                assert person_data is not None, "Person %s not found" % person
                assert person_data["city"] == city
            """
        And an empty file named "features/none.feature"


    @usecase.primary
    Scenario: Show documentation of available step definitions in dry-run mode
        When I run "behave --dry-run -f steps.doc features/"
        Then it should pass with:
          """
          @given('{person} lives in {city}')
            Function: step_given_person_lives_in_city()
            Location: features/steps/alice_steps.py:3
              Setup the data where a person lives and store in the database.

              :param person:  Person's name (as string).
              :param city:    City where the person lives (as string).

          @when('I visit {person}')
            Function: step_when_visit_person()
            Location: features/steps/alice_steps.py:16

          @then('I meet {person} in {city}')
            Function: step_then_meet_person_in_city()
            Location: features/steps/alice_steps.py:21
              Checks if I can meet the person in the expected city.

              :param person:  Person's name as key (as string).
              :param city:    Expected city (as string).

          @step('a step passes')
            Function: step_passes()
            Location: features/steps/passing_steps.py:3
              This step always passes.

          @step('a step fails')
            Function: step_fails()
            Location: features/steps/passing_steps.py:8
              This step is expected to fail.
          """
        But note that "the step definitions are ordered by file location"
        And note that "@when('I visit {person}') has no doc-string"


    @usecase.secondary
    Scenario: Show documentation of available step definitions in normal mode
        When I run "behave -f steps.doc features/"
        Then it should pass with:
          """
          @given('{person} lives in {city}')
            Function: step_given_person_lives_in_city()
            Location: features/steps/alice_steps.py:3
              Setup the data where a person lives and store in the database.

              :param person:  Person's name (as string).
              :param city:    City where the person lives (as string).

          @when('I visit {person}')
            Function: step_when_visit_person()
            Location: features/steps/alice_steps.py:16

          @then('I meet {person} in {city}')
            Function: step_then_meet_person_in_city()
            Location: features/steps/alice_steps.py:21
              Checks if I can meet the person in the expected city.

              :param person:  Person's name as key (as string).
              :param city:    Expected city (as string).

          @step('a step passes')
            Function: step_passes()
            Location: features/steps/passing_steps.py:3
              This step always passes.

          @step('a step fails')
            Function: step_fails()
            Location: features/steps/passing_steps.py:8
              This step is expected to fail.
          """
