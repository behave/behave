Feature: Issue # "behave crashes when adding a step definition with optional parts"

    Scenario:
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            import parse
            from behave import step, register_type, use_step_matcher

            @parse.with_pattern(r'optional\s+')
            def parse_optional_word(text):
                return text.strip()

            register_type(opt_=parse_optional_word)

            use_step_matcher('cfparse')

            @step(u'some {:opt_?}word')
            def step_impl(context, opt_):
                pass
            """
        And a file named "features/alice.feature" with:
            """
            Feature: Alice
              Scenario: Bob
                Given some optional word
            """
        When I run "behave -f plain features/alice.feature"
        Then it should pass
