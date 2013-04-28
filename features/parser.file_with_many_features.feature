@not_implemented
@not_supported
Feature: Parse Feature File that contains several Features

    | BEHARE: The parsers supports only one feature per feature file.


    @setup
    Scenario: Test Setup
      Given a new working directory
      And a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass
        """

    @parser.with_parse_error
    Scenario: Feature file with 2 features
      Given a file named "features/two_features.feature" with:
        """
        Feature: F1
          Scenario: F1.1
            Given a step passes
            When a step passes
            Then a step passes

        Feature: F2
          Scenario: F2.1
            Given a step passes
            Then a step passes
        """
      When I run "behave -f plain features/two_features.feature"
      Then it should fail with:
        """
        Failed to parse "{__WORKDIR__}/features/two_features.feature": Parser failure in state steps at line 7
        """
