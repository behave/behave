@sequential
Feature: Steps Catalog Formatter

    As a test writer
    I want to get a quick overview how to use a step definition
    By reading the step definition documentation (doc-stings).
    However I am not interested in technical details such as
    source location and step function names.
    Also, I would prefer to view the step as they appear in a feature file.

    . SOLUTION: Use StepsDocFormatter in dry-run mode, like:
    .
    .       behave --dry-run -f steps.catalog features/


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
        When I run "behave --steps-catalog features/"
        Then it should pass with:
          """
          Given {person} lives in {city}
              Setup the data where a person lives and store in the database.

              :param person:  Person's name (as string).
              :param city:    City where the person lives (as string).

          When I visit {person}

          Then I meet {person} in {city}
              Checks if I can meet the person in the expected city.

              :param person:  Person's name as key (as string).
              :param city:    Expected city (as string).

          Given a step passes
          When a step passes
          Then a step passes
              This step always passes.

          Given a step fails
          When a step fails
          Then a step fails
              This step is expected to fail.
          """
        But note that "the step definitions are ordered by step type"
        And note that "'When I visit {person}' has no doc-string"


    Scenario: Steps catalog formatter is used for output even when other formatter is specified
        When I run "behave --steps-catalog -f plain features/"
        Then it should pass with:
          """
          Given {person} lives in {city}
              Setup the data where a person lives and store in the database.

              :param person:  Person's name (as string).
              :param city:    City where the person lives (as string).
          """

