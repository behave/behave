@issue
Feature: Issue #111: Comment following @wip tag results in scenario being ignored

    . If a comment is placed after the @wip tag, the following scenario
    . is ignored by behave:
    .
    .   @wip # comment: this is work in progress
    .   Scenario: test scenario
    .
    . results in behave -w not running the "test scenario".
    . After removing the comment, it runs as expected.


  Scenario: Test Setup
    Given a new working directory
    And   a file named "features/steps/passing_steps.py" with:
        """
        from behave import step

        @step(u'a step passes')
        def step_passes(context):
            pass
        """
    And   a file named "features/syndrome111.feature" with:
        """
        Feature:

          @wip  # Comment: blabla
          Scenario: S1
            Given a step passes

          @wip  @one    # Comment: foobar
          Scenario: S2
            Given a step passes
        """

  Scenario: Scenario w/ comment on tag-line should run as normal
    When I run "behave --wip features/syndrome111.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """

  Scenario: Ensure 2nd scenario can be selected with other tag
    When I run "behave -f plain --tags=one features/syndrome111.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 1 skipped
        1 step passed, 0 failed, 1 skipped, 0 undefined
        """
