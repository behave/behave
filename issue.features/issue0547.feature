@issue
Feature: Issue 547 -- behave crashes when adding a step definition with optional parts

  . NOTE: cfparse/parse matcher conflict issue w/ CTOR init code.

    Scenario: Syndrome w/ cfparse
      Given a new working directory
      And a file named "features/environment.py" with:
        """
        from behave import register_type, use_step_matcher
        import parse

        @parse.with_pattern(r"optional\s+")
        def parse_optional_word(text):
            return text.strip()

        use_step_matcher("cfparse")
        register_type(opt_=parse_optional_word)
        """
      And a file named "features/steps/steps.py" with:
          """
          from behave import step

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
      And the command output should not contain:
        """
        ValueError: format spec u'opt_?' not recognised
        """
