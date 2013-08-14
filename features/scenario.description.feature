Feature: Scenario Description

    As a tester
    I want to explain the rationale of a test scenario or scenario outline
    Before I actually execute the steps.

    | SPECIFICATION: Scenario Description
    |   * Scenario descriptions are in optional section between
    |     Scenario line and the first step.
    |   * All description lines are added to the scenario description.
    |   * Empty lines are not part of the scenario description (are removed).
    |   * Comment lines are not part of the scenario description (are removed).
    |   * A Scenario/ScenarioOutline with a scenario description,
    |     but without steps is valid (to support preparation of scenarios).
    |
    | SPECIFICATION: A scenario description line...
    |   * must not start with step keywords, like:
    |
    |       Given, When, Then, And, But, etc.
    |       (including lower-case versions)
    |
    |   * must not start with '*' (ASTERISK) due to generic step keyword ambiguity
    |   * must not start with '@' (AT) due to tag ambiguity
    |     (supporting: scenario without steps but with step description).
    |   * may start with '|' (table-cell-separator).
    |   * does not contain only whitespace chars (empty line, filtered-out).
    |   * does not start with '#' (HASH) after whitespace chars (comment line).
    |
    | GRAMMAR STRUCTURE:
    |   Scenario-Line : 1
    |       Scenario-Description-Line : 0 .. N
    |       Step-Line : 0 .. N
    |
    |   Scenario-Line := Scenario-Keyword ':' Scenario-Name
    |   Scenario-Description-Line := Line does not start with Step-Keyword
    |   Step-Line := Step-Keyword Words+


    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "features/steps/steps.py" with:
        """
        from behave import step
        import sys

        @step('a step passes')
        def step_passes(context):
            pass

        @step('a step passes with "{comment}"')
        def step_passes(context, comment):
            sys.stdout.write("PASSING-STEP: %s;\n" % comment)

        @step('a step fails')
        def step_fails(context):
            assert False, "XFAIL-STEP"
        """


    Scenario: First Example for a Scenario Description
      Given a file named "features/example_description1.feature" with:
        """
        Feature:
          Scenario: E1

            This is a simple scenario description before the steps start.
            It explains why this scenario is important.

            Here another scenario description line after an empty line.

                Given a step passes with "Alice"
                When a step passes with "Bob"
                Then a step passes with "Charly"
        """
      When I run "behave -f plain -T features/example_description1.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Feature:
          Scenario: E1
            Given a step passes with "Alice" ... passed
            When a step passes with "Bob" ... passed
            Then a step passes with "Charly" ... passed
        """


    Scenario: Inspect the Scenario Description by using JSON
      Given a file named "features/example_description1.feature" exists
      When I run "behave -f json.pretty -o example1.json -f plain -T features/example_description1.feature"
      Then it should pass
      And the file "example1.json" should contain:
        """
            "description": [
              "This is a simple scenario description before the steps start.",
              "It explains why this scenario is important.",
              "Here another scenario description line after an empty line."
            ],
            "keyword": "Scenario",
            "location": "features/example_description1.feature:2",
            "name": "E1",
        """


    Scenario: Second Example with 2 scenario with scenario descriptions
      Given a file named "features/example_description2.feature" with:
        """
        @one
        Feature: F2

           Feature description line 1.
           Feature description line 2.

          @foo
          Scenario: S2.1

            Scenario description line S2.1-1.
              Scenario description line S2.1-2 (indentation is removed).

                Given a step passes with "Alice"
                Then a step passes with "Charly"

          @foo
          @bar @baz
          Scenario: S2.2

            Scenario description line S2.2-1.

                When a step passes with "Bob"
        """
      When I run "behave -f json.pretty -o example2.json -f plain -T features/example_description2.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Feature: F2
          Scenario: S2.1
            Given a step passes with "Alice" ... passed
            Then a step passes with "Charly" ... passed

          Scenario: S2.2
            When a step passes with "Bob" ... passed
        """
      And the file "example2.json" should contain:
        """
            "description": [
              "Scenario description line S2.1-1.",
              "Scenario description line S2.1-2 (indentation is removed)."
            ],
            "keyword": "Scenario",
            "location": "features/example_description2.feature:8",
            "name": "S2.1",
        """
      And the file "example2.json" should contain:
        """
            "description": [
              "Scenario description line S2.2-1."
            ],
            "keyword": "Scenario",
            "location": "features/example_description2.feature:18",
            "name": "S2.2",
        """
