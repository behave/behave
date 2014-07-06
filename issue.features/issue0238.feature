@issue
Feature: Issue #238 Skip a Scenario in a Scenario Outline

    Scenario:
        Given a new working directory
        And a file named "features/issue238_1.feature" with:
        """
        Feature: Testing Scenario skipping
            Scenario Outline:
                Given a set of <thing>
                When I ensure <thing> != invalid
                Then it should pass
            Examples:
                | thing   |
                | valid   |
                | invalid |
        """
        And a file named "features/steps/steps.py" with:
        """
        @given("a set of {thing}")
        def step(ctx, thing):
            if thing == 'invalid':
                print(ctx.scenario)
                ctx.scenario.mark_skipped()

        @when('I ensure {thing} != invalid')
        def step(ctx, thing):
            assert thing != 'invalid'

        @then(u'it should pass')
        def step_impl(context):
            pass
        """
        When I run "behave"
        Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 1 skipped
        4 steps passed, 0 failed, 2 skipped, 0 undefined
        """
