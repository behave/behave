Feature: Summary with Undefined Steps

  As I tester and test writer
  I want to know which scenarios were skipped and why.


    @setup
    Scenario:
      Given a new working directory
        And a file named "features/example.feature" with:
            """
            Feature:

              Scenario: Alice
                 Given a step passes
                  When another step passes
                  Then some step passes

              Scenario: Bob and Alice
                 Given some step passes

              Scenario: Bob
                 Given another step passes
            """
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass

            @step('{word:w} step fails')
            def step_fails(context, word):
                assert False, "XFAIL-STEP"
            """

    @use_hook.before_scenario
    Scenario: Show list of skipped scenarios when scenario is excluded from the test run (using: before_scenario() hook)
      Given a file named "features/environment.py" with:
            """
            import sys

            def should_exclude_scenario(context, scenario):
                if scenario.name.startswith("Alice"):
                    return True
                return False

            def before_scenario(context, scenario):
                if should_exclude_scenario(context, scenario):
                    sys.stdout.write("EXCLUDED-BY-USER: Scenario %s\n" % scenario.name)
                    scenario.skip(reason='Test')
            """
       When I run "behave -f plain -T features/example.feature --skipped-list"
       Then it should pass with:
            """
            Skipped scenarios:
              features/example.feature:3  Alice - Reason: Test

            1 feature passed, 0 failed, 0 skipped
            2 scenarios passed, 0 failed, 1 skipped
            2 steps passed, 0 failed, 3 skipped, 0 undefined
            """


    @use_hook.before_feature
    Scenario: Show list of skipped scenarios when scenario are excluded from the test run (using: before_feature() hook)
      Given a file named "features/environment.py" with:
            """
            import sys

            def should_exclude_scenario(scenario):
                if "Alice" in scenario.name:  # MATCHES: Alice, Bob and Alice
                    return True
                return False

            def before_feature(context, feature):
                # -- NOTE: walk_scenarios() flattens ScenarioOutline.scenarios
                for scenario in feature.walk_scenarios():
                    if should_exclude_scenario(scenario):
                        sys.stdout.write("EXCLUDED-BEFORE-FEATURE: Scenario %s\n" % scenario.name)
                        scenario.skip()
            """
       When I run "behave -f plain -T features/example.feature --skipped-list"
       Then it should pass with:
            """
            Skipped scenarios:
              features/example.feature:3  Alice - Reason: None
              features/example.feature:8  Bob and Alice - Reason: None

            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 2 skipped
            1 step passed, 0 failed, 4 skipped, 0 undefined
            """


    Scenario: Show list of skipped scenarios when scenario are skipped in a step

      Expect that remaining steps of the scenario are skipped.
      The skipping step is also marked as skipped
      to better detect scenarios that are partly executed and then skipped
      (otherwise a passed step would hide that the remaining steps are skipped).

      Given a file named "features/skip_scenario.feature" with:
            """
            Feature:

              Scenario: Alice2
                 Given a step passes
                 And the assumption "location:Wonderland" is not met
                 When another step passes
                 Then some step passes

              Scenario: Bob and Alice2
                 Given some step passes
                 When I skip the remaining scenario
                 Then another step passes
            """
        And a file named "features/steps/skip_scenario_steps.py" with:
            """
            from behave import given, step

            @given('the assumption "{name}" is not met')
            def step_assumption_not_met(context, name):
                context.scenario.skip("Assumption %s not met" % name)

            @step('I skip the remaining scenario')
            def step_skip_scenario(context):
                context.scenario.skip()
            """
        And a file named "features/environment.py" with:
            """
            # -- OVERRIDE WITH EMPTY-ENVIRONMENT.
            """
       When I run "behave -f plain -T features/skip_scenario.feature --skipped-list"
       Then it should pass with:
            """
            Skipped scenarios:
              features/skip_scenario.feature:3  Alice2 - Reason: Assumption location:Wonderland not met
              features/skip_scenario.feature:9  Bob and Alice2 - Reason: None

            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 2 skipped
            2 steps passed, 0 failed, 5 skipped, 0 undefined
            """
