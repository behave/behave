@issue
Feature: Issue #92: Output from --format=plain shows skipped steps in next scenario

    . DUPLICATED, FIXED-BY: issue #35 solution.
    .
    . Given a feature has more than one scenario
    . When the --format=plain option is used
    .   and a middle step of a scenario fails
    . Then the skipped steps appear under the next scenario


  Scenario:
    Given a new working directory
    And   a file named "features/issue92_syndrome.feature" with:
        """
        Feature: Testing Plain Output
            Reproduces bug where output from previous scenario appears before current.

            Scenario: First example
                Given this step works
                When this step fails
                Then this step appears in the wrong place

            Scenario: Second example
                Given this step works
                When this step fails
                Then this step appears in the wrong place
        """
    And   a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step(u'this step works')
        def working(context):
            pass


        @step(u'this step fails')
        def failing(context):
            assert False, 'step failed'


        @step(u'this step appears in the wrong place')
        def missing(context):
            pass
        """
    When I run "behave --no-timings --format=plain features/issue92_syndrome.feature"
    Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 2 failed, 0 skipped
        2 steps passed, 2 failed, 2 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature: Testing Plain Output
           Scenario: First example
               Given this step works ... passed
                When this step fails ... failed
           Assertion Failed: step failed

           Scenario: Second example
               Given this step works ... passed
                When this step fails ... failed
           Assertion Failed: step failed
        """
