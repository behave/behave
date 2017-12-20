@issue
Feature: Issue #384 -- Active Tags fail with ScenarioOutline

  . ScenarioOutline can currently not be used with active-tag(s).
  . REASON: Template mechanism transforms active-tag into invalid active-tag per example row.
  .
  . RELATED: features/tag.active_tags.feature


    Background:
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass

        # -- REUSE: Step definitions.
        from behave4cmd0 import note_steps
        """
      And a file named "features/environment.py" with:
        """
        from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
        import sys

        # -- ACTIVE TAG SUPPORT: @use.with_{category}={value}, ...
        active_tag_value_provider = {
            "browser":   "chrome",
            "webserver": "apache",
        }
        active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

        def before_all(context):
            setup_active_tag_values(active_tag_value_provider, context.config.userdata)

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                sys.stdout.write("ACTIVE-TAG DISABLED: Scenario %s\n" % scenario.name)
                scenario.skip(active_tag_matcher.exclude_reason)
        """
      And a file named "behave.ini" with:
        """
        [behave]
        default_format = pretty
        show_timings = no
        show_skipped = no
        color = no
        """
      And a file named "features/outline.active_tags.feature" with:
        """
        Feature:

          @use.with_browser=chrome
          Scenario Outline: Alice -- <name>, <language>
            Given a step passes
            But note that "<name> can speak <language>"

            Examples:
              | name     | language |
              | Anna     | German   |
              | Arabella | English  |
        """


    Scenario: ScenarioOutline with enabled active-tag is executed
      When I run "behave -D browser=chrome features/outline.active_tags.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        @use.with_browser=chrome
        Scenario Outline: Alice -- Anna, German -- @1.1   # features/outline.active_tags.feature:10
          Given a step passes                             # features/steps/pass_steps.py:3
          But note that "Anna can speak German"           # ../behave4cmd0/note_steps.py:15

        @use.with_browser=chrome
        Scenario Outline: Alice -- Arabella, English -- @1.2   # features/outline.active_tags.feature:11
          Given a step passes                                  # features/steps/pass_steps.py:3
          But note that "Arabella can speak English"           # ../behave4cmd0/note_steps.py:15
        """
      And the command output should not contain "ACTIVE-TAG DISABLED: Scenario Alice"
      But note that "we check now for the specific syndrome"
      And the command output should not contain "@use.with_browserchrome"
      But the command output should contain "@use.with_browser=chrome"


    Scenario: ScenarioOutline with disabled active-tag is skipped
      When I run "behave -D browser=other features/outline.active_tags.feature"
      Then it should pass with:
        """
        0 scenarios passed, 0 failed, 2 skipped
        0 steps passed, 0 failed, 4 skipped, 0 undefined
        """
      And the command output should contain:
        """
        ACTIVE-TAG DISABLED: Scenario Alice -- Anna, German -- @1.1
        ACTIVE-TAG DISABLED: Scenario Alice -- Arabella, English -- @1.2
        """
