Feature: Active Tags

  As a test writer
  I want that some tags are evaluated at runtime
  So that some features/scenarios automatically excluded from the run-set.

  . SPECIFICATION: Active tag
  .   * An active tag is evaluated at runtime.
  .   * An active tag is either enabled or disabled (decided by runtime decision logic).
  .   * A disabled active tag causes that its feature/scenario is excluded from the run-set.
  .   * If several active tags are used for a feature/scenario/scenario outline,
  .     the following tag logic is used:
  .
  .     enabled = enabled1 and enabled2 and ...
  .
  . ACTIVE TAG SCHEMA (dialect1):
  .     @active.with_{category}={value}
  .     @not_active.with_{category}={value}
  .
  . ACTIVE TAG SCHEMA (dialect2):
  .     @use.with_{category}={value}
  .     @not.with_{category}={value}
  .     @only.with_{category}={value}
  .
  . RATIONALE:
  .   Some aspects of the runtime environment are only known
  .   when the tests are running. Therefore, it many cases it is simpler
  .   to use such a mechanism as "active tags" instead of moving this decision
  .   to the build-script that runs the tests.
  .
  .   This allows to automatically skip some tests (scenarios, features)
  .   that would otherwise fail anyway.
  .
  . NOTE:
  .   * DRY-RUN MODE: Hooks are not called in dry-run mode.


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
      And a file named "features/environment.py" with:
        """
        from behave.tag_matcher import ActiveTagMatcher
        import sys

        # -- ACTIVE TAG SUPPORT: @use.with_{category}={value}, ...
        active_tag_value_provider = {
            "browser":   "chrome",
            "webserver": "apache",
        }
        active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)

        def setup_active_tag_values(userdata):
            for key in active_tag_value_provider.keys():
                if key in userdata:
                    active_tag_value_provider[key] = userdata[key]

        def before_all(context):
            setup_active_tag_values(context.config.userdata)

        def before_scenario(context, scenario):
            if active_tag_matcher.should_exclude_with(scenario.effective_tags):
                sys.stdout.write("ACTIVE-TAG DISABLED: Scenario %s\n" % scenario.name)
                scenario.skip(active_tag_matcher.exclude_reason)
        """

    Scenario: Use tag schema dialect2 with one category
      Given a file named "features/e1.active_tags.feature" with:
        """
        Feature:

          @use.with_browser=chrome
          Scenario: Alice (Run only with Web-Browser Chrome)
            Given a step passes
            When another step passes

          @only.with_browser=safari
          Scenario: Bob (Run only with Web-Browser Safari)
            Given some step passes
        """
      When I run "behave -f plain -T features/e1.active_tags.feature"
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


    Scenario: Use tag schema dialect1 with several categories
      Given a file named "features/e2.active_tags.feature" with:
        """
        Feature:

          @active.with_webserver=apache
          Scenario: Alice (Run only with Apache Web-Server)
            Given a step passes
            When another step passes

          @active.with_browser=safari
          Scenario: Bob (Run only with Safari Web-Browser)
            Given another step passes
        """
      When I run "behave -f plain -D browser=firefox features/e2.active_tags.feature"
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

    Scenario Outline: Use active tags with positive and negative logic: <browser>
      Given a file named "features/e3.active_tags.feature" with:
        """
        Feature:

          @active.with_browser=chrome
          Scenario: Alice
            Given a step passes
            When another step passes

          @not_active.with_browser=opera
          Scenario: Bob
            Given another step passes

          @use.with_browser=safari
          Scenario: Charly
            Given some step passes
        """
      When I run "behave -f plain -D browser=<browser> features/e3.active_tags.feature"
      Then it should pass with:
        """
        ACTIVE-TAG DISABLED: Scenario <disabled scenario>
        """
      And the command output should not contain:
        """
        ACTIVE-TAG DISABLED: Scenario <enabled scenario>
        """
      And note that "<comment>"

      Examples:
        | browser | enabled scenario | disabled scenario | comment |
        | chrome  | Alice            | Charly            | Bob is also enabled |
        | firefox | Bob              | Alice             | Charly is also disabled |
        | safari  | Charly           | Alice             | Bob is also enabled |


    Scenario: Tag logic with one active tag
      Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
      Then the following active tag combinations are enabled:
        | tags                        | enabled? |
        | @active.with_foo=xxx        |  yes      |
        | @active.with_foo=other      |  no       |
        | @not_active.with_foo=xxx    |  no       |
        | @not_active.with_foo=other  |  yes      |
      And the following active tag combinations are enabled:
        | tags                        | enabled? |
        | @use.with_foo=xxx           |  yes      |
        | @use.with_foo=other         |  no       |
        | @only.with_foo=xxx          |  yes      |
        | @only.with_foo=other        |  no       |
        | @not.with_foo=xxx           |  no       |
        | @not.with_foo=other         |  yes      |


    Scenario: Tag logic with two active tags
      Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
        | bar      | zzz   |
      Then the following active tag combinations are enabled:
        | tags                                      | enabled? |
        | @use.with_foo=xxx   @use.with_bar=zzz     |  yes      |
        | @use.with_foo=xxx   @use.with_bar=other   |  no       |
        | @use.with_foo=other @use.with_bar=zzz     |  no       |
        | @use.with_foo=other @use.with_bar=other   |  no       |
        | @not.with_foo=xxx   @use.with_bar=zzz     |  no       |
        | @not.with_foo=xxx   @use.with_bar=other   |  no       |
        | @not.with_foo=other @use.with_bar=zzz     |  yes      |
        | @not.with_foo=other @use.with_bar=other   |  no       |
        | @use.with_foo=xxx   @not.with_bar=zzz     |  no       |
        | @use.with_foo=xxx   @not.with_bar=other   |  yes      |
        | @use.with_foo=other @not.with_bar=zzz     |  no       |
        | @use.with_foo=other @not.with_bar=other   |  no       |
        | @not.with_foo=xxx   @not.with_bar=zzz     |  no       |
        | @not.with_foo=xxx   @not.with_bar=other   |  no       |
        | @not.with_foo=other @not.with_bar=zzz     |  no       |
        | @not.with_foo=other @not.with_bar=other   |  yes      |


    Scenario: Tag logic with unknown categories (case: ignored)

      Unknown categories (where a value is missing) are ignored by default.
      Therefore, the active tag that uses an unknown category acts
      as if it is always enabled (even in the negated case).

      Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
      When unknown categories are ignored in active tags
      Then the following active tag combinations are enabled:
        | tags                   | enabled? |
        | @use.with_unknown=xxx  |  yes     |
        | @use.with_unknown=zzz  |  yes     |
        | @not.with_unknown=xxx  |  yes     |
        | @not.with_unknown=zzz  |  yes     |
      But note that "the active tag with the unknown category acts like a passive tag"


    Scenario: Tag logic with unknown categories (case: not ignored)

      If unknown categories are not ignored, then the active tag is disabled.

      Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
      When unknown categories are not ignored in active tags
      Then the following active tag combinations are enabled:
        | tags                   | enabled? |
        | @use.with_unknown=xxx  |  no      |
        | @use.with_unknown=zzz  |  no      |
        | @not.with_unknown=xxx  |  yes     |
        | @not.with_unknown=zzz  |  yes     |
      But note that "the active tag with the unknown category is disabled"
