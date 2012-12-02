@issue
Feature: Issue #73: the current_matcher is not predictable

    | behave provides 2 matchers: ParseMatcher (parse) and RegexpMatcher (re).
    | The ParseMatcher is used per default when the test runner starts.
    |
    | A step definition file may change the matcher several times
    | by calling `step_matcher("re")` or `step_matcher("parse")`.
    | In order to make the writing of step definitions more predictable,
    | the matcher should be reset to the default matcher
    | before loading each step definition.
    |
    | A project can define its own default matcher by calling the
    | `step_matcher(...)` in the "environment.py" hook.
    | This matcher will be used as default before a step definition is loaded.


  Scenario: Verify that ParseMatcher is the default matcher
    Given a new working directory
    And   a file named "features/steps/parse_steps.py" with:
        """
        from behave import step

        @step(u'a step {outcome:w}')
        def step_passes(context, outcome):
            assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
        """
    And   a file named "features/passing.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When  a step passes
            Then  a step passes
        """
    When I run "behave -f plain features/passing.feature"
    Then it should pass with
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """


  Scenario: Use only RegexMatcher in Step Definitions
    Given a new working directory
    And   a file named "features/environment.py" with:
        """
        from behave import step_matcher
        step_matcher("re")
        """
    And   a file named "features/steps/regexp_steps.py" with:
        """
        from behave import step

        @step(u'a step (?P<outcome>passes|fails)')
        def step_passes(context, outcome):
            assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
        """
    And   a file named "features/passing.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When  a step passes
            Then  a step passes
        """
    When I run "behave -f plain features/passing.feature"
    Then it should pass with
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """


  Scenario: Use ParseMatcher and RegexMatcher in Step Definitions (default=re)
    Given a new working directory
    And   a file named "features/environment.py" with:
        """
        from behave import step_matcher
        step_matcher("re")
        """
     And   a file named "features/steps/eparse_steps.py" with:
         """
         from behave import step, step_matcher
         step_matcher("parse")

         @step(u'an extraordinary step {outcome:w}')
         def step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
         """
    And   a file named "features/steps/regexp_steps.py" with:
        """
        from behave import step

        @step(u'a step (?P<outcome>passes|fails)')
        def step_passes(context, outcome):
            assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
        """
     And   a file named "features/steps/xparse_steps.py" with:
         """
         from behave import step, step_matcher
         step_matcher("parse")

         @step(u'another step {outcome:w}')
         def step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
         """
   And   a file named "features/passing3.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When  another step passes
            Then  an extraordinary step passes
        """
    When I run "behave -f plain features/passing3.feature"
    Then it should pass with
        """
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """


  Scenario: Mix ParseMatcher and RegexMatcher in Step Definitions (default=re)
    Given a new working directory
    And   a file named "features/environment.py" with:
        """
        from behave import step_matcher
        step_matcher("re")
        """
     And   a file named "features/steps/given_steps.py" with:
         """
         from behave import step, step_matcher

         step_matcher("parse")
         @given(u'a step {outcome:w}')
         def given_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)

         step_matcher("re")
         @given(u'another step (?P<outcome>passes|fails)')
         def given_another_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)

         step_matcher("parse")
         @given(u'an extraordinary step {outcome:w}')
         def given_extraordinary_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
         """
     And   a file named "features/steps/when_steps.py" with:
         """
         from behave import step, step_matcher

         @when(u'a step (?P<outcome>passes|fails)')
         def when_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)

         step_matcher("parse")
         @when(u'another step {outcome:w}')
         def when_another_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)

         step_matcher("re")
         @when(u'an extraordinary step (?P<outcome>passes|fails)')
         def when_extraordinary_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
         """
     And   a file named "features/steps/then_steps.py" with:
         """
         from behave import step, step_matcher

         step_matcher("parse")
         @then(u'a step {outcome:w}')
         def then_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)

         step_matcher("re")
         @then(u'another step (?P<outcome>passes|fails)')
         def then_another_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)

         step_matcher("parse")
         @then(u'an extraordinary step {outcome:w}')
         def then_extraordinary_step_passes(context, outcome):
             assert outcome == "passes", "FAIL: outcome={0}".format(outcome)
         """
   And   a file named "features/passing3.feature" with:
        """
        Feature:
          Scenario: 1
            Given a step passes
            When  another step passes
            Then  an extraordinary step passes

          Scenario: 2
            Given another step passes
            When  an extraordinary step passes
            Then  a step passes

          Scenario: 3
            Given an extraordinary step passes
            When  a step passes
            Then  another step passes
        """
    When I run "behave -c -f pretty --no-timings features/passing3.feature"
    Then it should pass with:
        """
        3 scenarios passed, 0 failed, 0 skipped
        9 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:  # features/passing3.feature:1
          Scenario: 1                         # features/passing3.feature:2
            Given a step passes               # features/steps/given_steps.py:4
            When another step passes          # features/steps/when_steps.py:8
            Then an extraordinary step passes # features/steps/then_steps.py:14

          Scenario: 2                         # features/passing3.feature:7
            Given another step passes         # features/steps/given_steps.py:9
            When an extraordinary step passes # features/steps/when_steps.py:13
            Then a step passes                # features/steps/then_steps.py:4

          Scenario: 3                          # features/passing3.feature:12
            Given an extraordinary step passes # features/steps/given_steps.py:14
            When a step passes                 # features/steps/when_steps.py:3
            Then another step passes           # features/steps/then_steps.py:9
        """