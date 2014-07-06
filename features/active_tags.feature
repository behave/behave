Feature: Active Tags

  As a test writer
  I want that some tags are evaluated at runtime
  So that some features/scenarios automatically excluded from the run-set.

  | CONCEPT: Active tag
  |   An active tag is evaluated at runtime.
  |   An active tag is either enabled or disabled (decided by runtime decision logic).
  |   A disabled active tag causes that its feature/scenario is excluded from the run-set.
  |
  | RATIONALE:
  |   Some aspects of the runtime environment are only known
  |   when the tests are running. Therefore, it many cases it is simpler
  |   to use such a mechanism as "active tags" instead of moving this decision
  |   to the build-script that runs the tests.
  |
  |   This allows to automatically skip some tests (scenarios, features)
  |   that would otherwise fail anyway.
  |
  | NOTE:
  |   * An "@only.with_{category}={value}" tag schema for active tags is presented here.
  |   * DRY-RUN MODE: Hooks are not called in dry-run mode.


    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """

    Scenario: Use "@only.with_{category}" tag schema with one category
      Given a file named "features/example1.active_tags.feature" with:
        """
        Feature:

          @only.with_browser=chrome
          Scenario: Alice (Run only with Web-Browser Chrome)
            Given a step passes
            When another step passes

          @only.with_browser=safari
          Scenario: Bob (Run only with Web-Browser Safari)
            Given some step passes
        """
      And a file named "features/environment.py" with:
        """
        from behave.tag_matcher import OnlyWithCategoryTagMatcher
        import sys

        # -- MATCHES TAGS: @only.with_{category}=*  =>  @only.with_browser=*
        current_browser = "chrome"  #< SIMPLIFIED
        active_tag_matcher = OnlyWithCategoryTagMatcher("browser", current_browser)

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                sys.stdout.write("ACTIVE-TAG DISABLED: Scenario %s\n" % scenario.name)
                scenario.mark_skipped()   #< LATE-EXCLUDE from run-set.
        """
      When I run "behave -f plain -T features/example1.active_tags.feature"
      Then it should pass with:
        """
        1 scenario passed, 0 failed, 1 skipped
        2 steps passed, 0 failed, 1 skipped, 0 undefined
        """
      And the command output should contain:
        """
        ACTIVE-TAG DISABLED: Scenario Bob
        """
      But the command output should not contain:
        """
        ACTIVE-TAG DISABLED: Scenario Alice
        """


    Scenario: Use "@only.with_{category}" tag schema with many categories
      Given a file named "features/example2.active_tags.feature" with:
        """
        Feature:

          @only.with_webserver=apache
          Scenario: Alice (Run only with Apache Web-Server)
            Given a step passes
            When another step passes

          @only.with_browser=safari
          Scenario: Bob (Run only with Safari Web-Browser)
            Given some step passes
        """
      And a file named "features/environment.py" with:
        """
        from behave.tag_matcher import OnlyWithAnyCategoryTagMatcher
        import sys

        # -- MATCHES ANY TAGS: @only.with_{category}={value}
        # SIMPLIFIED: category_value_provider provides active category values.
        category_value_provider = {
            "browser":   "chrome",
            "webserver": "apache",
        }
        active_tag_matcher = OnlyWithAnyCategoryTagMatcher(category_value_provider)

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                sys.stdout.write("ACTIVE-TAG DISABLED: Scenario %s\n" % scenario.name)
                scenario.mark_skipped()   #< LATE-EXCLUDE from run-set.
        """
      When I run "behave -f plain -T features/example2.active_tags.feature"
      Then it should pass with:
        """
        1 scenario passed, 0 failed, 1 skipped
        2 steps passed, 0 failed, 1 skipped, 0 undefined
        """
      And the command output should contain:
        """
        ACTIVE-TAG DISABLED: Scenario Bob
        """
      But the command output should not contain:
        """
        ACTIVE-TAG DISABLED: Scenario Alice
        """
