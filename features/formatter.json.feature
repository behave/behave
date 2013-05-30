@sequential
Feature: JSON Formatter

    In order to process data with other tools
    As a tester
    I want that behave generates test run data in JSON format.


    @setup
    Scenario: Feature Setup
        Given a new working directory
        And a file named "features/steps/steps.py" with:
            """
            from behave import step

            @step('a step passes')
            def step_passes(context):
                pass

            @step('a step fails')
            def step_fails(context):
                assert False, "XFAIL-STEP"
            """

    Scenario: Use JSON formatter on simple feature
        Given a file named "features/simple_feature_with_name.feature" with:
            """
            Feature: Simple, empty Feature
            """
        When I run "behave -f json.pretty features/simple_feature_with_name.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            [
              {
                "keyword": "Feature",
                "location": "features/simple_feature_with_name.feature:1",
                "name": "Simple, empty Feature",
                "status": "skipped",
                "tags": []
              }
            ]
            """

    Scenario: Use JSON formatter on simple feature with description
        Given a file named "features/simple_feature_with_description.feature" with:
            """
            Feature: Simple feature with description

                First feature description line.
                Second feature description line.

                Third feature description line (following an empty line).
            """
        When I run "behave -f json.pretty features/simple_feature_with_description.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            [
              {
                "description": [
                  "First feature description line.",
                  "Second feature description line.",
                  "Third feature description line (following an empty line)."
                ],
                "keyword": "Feature",
                "location": "features/simple_feature_with_description.feature:1",
                "name": "Simple feature with description",
                "status": "skipped",
                "tags": []
              }
            ]
            """

    Scenario: Use JSON formatter on simple feature with tags
        Given a file named "features/simple_feature_with_tags.feature" with:
            """
            @foo @bar
            Feature: Simple feature with tags
            """
        When I run "behave -f json.pretty features/simple_feature_with_tags.feature"
        Then it should pass with:
            """
            0 features passed, 0 failed, 1 skipped
            0 scenarios passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            [
              {
                "keyword": "Feature",
                "location": "features/simple_feature_with_tags.feature:2",
                "name": "Simple feature with tags",
                "status": "skipped",
                "tags": [
                  "foo",
                  "bar"
                ]
              }
            ]
            """

    Scenario: Use JSON formatter with feature and one scenario without steps
        Given a file named "features/simple_scenario.feature" with:
            """
            Feature:
              Scenario: Simple scenario without steps
            """
        When I run "behave -f json.pretty features/simple_scenario.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            [
              {
                "elements": [
                  {
                    "keyword": "Scenario",
                    "location": "features/simple_scenario.feature:2",
                    "name": "Simple scenario without steps",
                    "steps": [],
                    "tags": [],
                    "type": "scenario"
                  }
                ],
                "keyword": "Feature",
                "location": "features/simple_scenario.feature:1",
                "name": "",
                "status": "passed",
                "tags": []
              }
            ]
            """

    Scenario: Use JSON formatter with feature and one scenario with description
        Given a file named "features/simple_scenario_with_description.feature" with:
            """
            Feature:
              Scenario: Simple scenario with description but without steps

                First scenario description line.
                Second scenario description line.

                Third scenario description line (after an empty line).
            """
        When I run "behave -f json.pretty features/simple_scenario_with_description.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            [
              {
                "elements": [
                  {
                    "description": [
                      "First scenario description line.",
                      "Second scenario description line.",
                      "Third scenario description line (after an empty line)."
                    ],
                    "keyword": "Scenario",
                    "location": "features/simple_scenario_with_description.feature:2",
                    "name": "Simple scenario with description but without steps",
                    "steps": [],
                    "tags": [],
                    "type": "scenario"
                  }
                ],
                "keyword": "Feature",
                "location": "features/simple_scenario_with_description.feature:1",
                "name": "",
                "status": "passed",
                "tags": []
              }
            ]
            """

    Scenario: Use JSON formatter with feature and one scenario with tags
        Given a file named "features/simple_scenario_with_tags.feature" with:
            """
            Feature:

              @foo
              @bar
              Scenario: Simple scenario with tags but without steps
            """
        When I run "behave -f json.pretty features/simple_scenario_with_tags.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            [
              {
                "elements": [
                  {
                    "keyword": "Scenario",
                    "location": "features/simple_scenario_with_tags.feature:5",
                    "name": "Simple scenario with tags but without steps",
                    "steps": [],
                    "tags": [
                      "foo",
                      "bar"
                    ],
                    "type": "scenario"
                  }
                ],
                "keyword": "Feature",
                "location": "features/simple_scenario_with_tags.feature:1",
                "name": "",
                "status": "passed",
                "tags": []
              }
            ]
            """

    @xfail
    @regression_problem.with_duration
    Scenario: Use JSON formatter with feature and one scenario with steps
        Given a file named "features/scenario_with_steps.feature" with:
            """
            Feature:
              Scenario: Simple scenario with with steps
                  Given a step passes
                  When a step passes
                  Then a step passes
                  And a step passes
                  But a step passes
            """
        When I run "behave -f json.pretty features/scenario_with_steps.feature"
        Then it should pass with:
            """
            1 feature passed, 0 failed, 0 skipped
            1 scenario passed, 0 failed, 0 skipped
            """
        And the command output should contain:
            """
            "steps": [
                {
                  "keyword": "Given",
                  "location": "features/scenario_with_steps.feature:2",
                  "match": {
                    "arguments": [],
                    "location": "features/steps/steps.py:3"
                  },
                  "name": "a step passes",
                  "result": {
                    "duration": XXX,
                    "status": "passed",
                  }
                  "step_type": "given",
                },
                {
                  "keyword": "When",
                  "location": "features/scenario_with_steps.feature:3",
                  "match": {
                    "arguments": [],
                    "location": "features/steps/steps.py:3"
                  },
                  "name": "a step passes",
                  "result": {
                    "duration": XXX,
                    "status": "passed",
                  }
                  "step_type": "when",
                },
                {
                  "keyword": "Then",
                  "location": "features/scenario_with_steps.feature:4",
                  "match": {
                    "arguments": [],
                    "location": "features/steps/steps.py:3"
                  },
                  "name": "a step passes",
                  "result": {
                    "duration": XXX,
                    "status": "passed",
                  }
                  "step_type": "then",
                },
                {
                  "keyword": "And",
                  "location": "features/scenario_with_steps.feature:5",
                  "match": {
                    "arguments": [],
                    "location": "features/steps/steps.py:3"
                  },
                  "name": "a step passes",
                  "result": {
                    "duration": XXX,
                    "status": "passed",
                  }
                  "step_type": "then",
                },
                {
                  "keyword": "But",
                  "location": "features/scenario_with_steps.feature:6",
                  "match": {
                    "arguments": [],
                    "location": "features/steps/steps.py:3"
                  },
                  "name": "a step passes",
                  "result": {
                    "duration": XXX,
                    "status": "passed",
                  }
                  "step_type": "then",
                }
            ],
            """

    @wip
    Scenario: Use JSON formatter with feature and two scenarios

    @wip
    Scenario: Use JSON formatter with feature and background

    @wip
    Scenario: Use JSON formatter with feature and scenario outline without steps
    Scenario: Use JSON formatter with feature and scenario outline with description
    Scenario: Use JSON formatter with feature and scenario outline with tags
    Scenario: Use JSON formatter with feature and scenario outline with steps
    Scenario: Use JSON formatter with feature and scenario outline with steps and examples


