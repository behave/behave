@issue
Feature: Issue #85: AssertionError with nested regex and pretty formatter

    | When --format=pretty is used
    | an AssertationError occurs for missing optional/nested-groups.
    | When --format=plain is used, everything is fine

  Scenario: Test Setup
    Given a new working directory
    And   a file named "features/steps/regexp_steps.py" with:
        """
        from behave import given, when, then, step_matcher
        @given(u'a {re_category} regular expression "{pattern}"')
        def impl(context, re_category, pattern):
            pass

        @then(u'the parameter "{name}" is "{expected_value}"')
        def impl(context, name, expected_value):
            actual_value = getattr(context, name, None)
            if actual_value is None:
                actual_value = ""
            assert hasattr(context, name)
            assert actual_value == expected_value, "MISMATCH: actual({0}) == expected({1})".format(actual_value, expected_value)

        @then(u'the parameter "{name}" is none')
        def impl(context, name):
            actual_value = getattr(context, name, None)
            assert hasattr(context, name)
            assert actual_value is None, "MISMATCH: actual({0}) == None)".format(actual_value)

        def store_in_context(context, data):
            for name, value in data.items():
                setattr(context, name, value)

        step_matcher('re')

        @when(u'I try to match "(?P<foo>foo and more)"')
        def impl(context, **kwargs):
            kwargs["regexp_case"] = "simple"
            print "CASE UNNESTED: {0}".format(kwargs)
            store_in_context(context, kwargs)

        @when(u'I try to match "(?P<foo>foo(?P<bar>bar)?)"')
        def impl(context, **kwargs):
            kwargs["regexp_case"] = "nested"
            print "CASE NESTED: {0}".format(kwargs)
            store_in_context(context, kwargs)

        @when(u'I try to match "(?P<foo>foo) (?P<bar>bar)?"')
        def impl(context, **kwargs):
            kwargs["regexp_case"] = "optional"
            print "CASE OPTIONAL: {0}".format(kwargs)
            store_in_context(context, kwargs)
        """
    And   a file named "features/matching.feature" with:
        """
        Feature: Using regexp matcher with nested and optional parameters

            Scenario: regex, no nested groups, matching
                Given a simple regular expression "(?P<foo>foo and more)"
                When I try to match "foo and more"
                Then the parameter "regexp_case" is "simple"
                And  the parameter "foo" is "foo and more"

            Scenario: Nested groups without nested match
                Given a nested-group regular expression "(?P<foo>foo(?P<bar>bar)?)"
                When I try to match "foo"
                Then the parameter "regexp_case" is "nested"
                And  the parameter "foo" is "foo"
                And  the parameter "bar" is none

            Scenario: Nested groups with nested match
                Given a nested-group regular expression "(?P<foo>foo(?P<bar>bar)?)"
                When I try to match "foobar"
                Then the parameter "regexp_case" is "nested"
                And  the parameter "foo" is "foobar"
                And  the parameter "bar" is "bar"

            Scenario: Optional group without match
                Given a optional-group regular expression "(?P<foo>foo) (?P<bar>bar)?"
                When I try to match "foo "
                Then the parameter "regexp_case" is "optional"
                And  the parameter "foo" is "foo"
                And  the parameter "bar" is none

            Scenario: Optional group with match
                Given a optional-group regular expression "(?P<foo>foo) (?P<bar>bar)?"
                When I try to match "foo bar"
                Then the parameter "regexp_case" is "optional"
                And  the parameter "foo" is "foo"
                And  the parameter "bar" is "bar"
        """

  Scenario: Run regexp steps with --format=plain
    When I run "behave --format=plain features/matching.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        5 scenarios passed, 0 failed, 0 skipped
        24 steps passed, 0 failed, 0 skipped, 0 undefined
        """

  Scenario: Run regexp steps with --format=pretty
    When I run "behave -c --format=pretty features/matching.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        5 scenarios passed, 0 failed, 0 skipped
        24 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And  the command output should not contain
        """
        assert isinstance(text, unicode)
        """
    And  the command output should not contain
        """
        AssertationError
        """
