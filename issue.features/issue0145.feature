@issue
Feature: Issue #145: before_feature/after_feature should not be skipped

  Hooks before_feature(), after_feature() (and before_step()) are skipped
  if --tags options select feature tag and scenario tag.

  SEE ALSO: https://github.com/cucumber/cucumber/wiki/Tags

  @setup
  Scenario: Setup
    Given a new working directory
    And a file named "features/steps/steps.py" with:
        """
        from behave import step

        @step('a step passes')
        def step_passes(context):
            pass
        """
    And a file named "features/issue0145_example.feature" with:
        """
        @feature
        Feature: Feature-145

          @scenario
          Scenario: Scenario-145
            Given a step passes
            When a step passes
            Then a step passes
        """
    And a file named "features/environment.py" with:
        """
        from __future__ import print_function

        def before_feature(context, feature):
            print("hooks.before_feature: %s called." % feature.name)

        def after_feature(context, feature):
            print("hooks.after_feature: %s called." % feature.name)
        """

  Scenario: Select only @scenario tag
    When I run "behave -f plain -T --tags=@scenario features/issue0145_example.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the behave hook "before_feature" was called
    And the behave hook "after_feature" was called

  Scenario: Select @feature tag and @scenario tag (logical-and, fails if not fixed)
    When I run "behave -f plain -T --tags=@feature --tags=@scenario features/issue0145_example.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        3 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the behave hook "before_feature" was called
    And the behave hook "after_feature" was called

