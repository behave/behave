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
  .     SIMPLIFIED ALGORITHM: For active-tag expression
  .
  .       enabled := enabled(active-tag1) and enabled(active-tag2) and ...
  .
  .           where all active-tags have a different category.
  .
  .     REAL ALGORITHM:
  .       If multiple active-tags for the same catgory exist,
  .       then these active-tags need to be merged together into a tag_group.
  .
  .     enabled           := enabled(tag_group1) and enabled(tag_group2) and ...
  .     tag_group.enabled := enabled(tag1) or enabled(tag2) or ...
  .
  .           where all the active-tags within a tag-group have the same category.
  .
  . ACTIVE TAG SCHEMA (dialect1):
  .     @use.with_{category}={value}
  .     @not.with_{category}={value}
  .
  .     DEPRECATED: @only.with_{category}={value}
  .
  . ACTIVE TAG SCHEMA (dialect2):
  .     @active.with_{category}={value}
  .     @not_active.with_{category}={value}
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

        # -- BEHAVE-HOOKS:
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

    Scenario: Use active-tag with Scenario and one category (tag schema dialect2)
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
      When I run "behave -f plain features/e1.active_tags.feature"
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


  Scenario: Tag logic with two active tags of same category
      Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
      Then the following active tag combinations are enabled:
        | tags                                      | enabled? | Comment |
        | @use.with_foo=xxx   @use.with_foo=other   |  yes     | Enabled: tag1 |
        | @use.with_foo=xxx   @not.with_foo=other   |  yes     | Enabled: tag1, tag2|
        | @use.with_foo=other @not.with_foo=xxx     |  no      | Disabled: none |
        | @not.with_foo=other @not.with_foo=xxx     |  no      | Disabled: tag1 |
        | @use.with_foo=xxx   @not.with_foo=xxx     |  no      | Disabled: tag1 (BAD-SPEC, CONFLICTS) |


  Scenario: Tag logic with three active tags of same category
      Given I setup the current values for active tags with:
        | category | value |
        | foo      | xxx   |
      Then the following active tag combinations are enabled:
        | tags                                                        | enabled? | Comment |
        | @use.with_foo=xxx  @use.with_foo=other @use.with_foo=other2|  yes     | Enabled: tag1  |
        | @use.with_foo=xxx  @use.with_foo=other @not.with_foo=other2|  yes     | Enabled: tag1  |
        | @use.with_foo=xxx  @not.with_foo=other @use.with_foo=other2|  yes     | Enabled: tag1  |
        | @use.with_foo=xxx  @not.with_foo=other @not.with_foo=other2|  yes     | Enabled: tag1  |
        | @not.with_foo=xxx  @use.with_foo=other @use.with_foo=other2|  no      | Disabled: tag1 |
        | @not.with_foo=xxx  @use.with_foo=other @not.with_foo=other2|  no      | Disabled: tag1 |
        | @not.with_foo=xxx  @not.with_foo=other @use.with_foo=other2|  no      | Disabled: tag1 |
        | @not.with_foo=xxx  @not.with_foo=other @not.with_foo=other2|  no      | Disabled: tag1 |


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


    Scenario: ScenarioOutline with enabled active-tag is executed
      Given a file named "features/outline1.active_tags.feature" with:
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
      When I run "behave -D browser=chrome features/outline1.active_tags.feature"
      Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        @use.with_browser=chrome
        Scenario Outline: Alice -- Anna, German -- @1.1   # features/outline1.active_tags.feature:10
          Given a step passes                             # features/steps/pass_steps.py:3
          But note that "Anna can speak German"           # ../behave4cmd0/note_steps.py:15

        @use.with_browser=chrome
        Scenario Outline: Alice -- Arabella, English -- @1.2   # features/outline1.active_tags.feature:11
          Given a step passes                                  # features/steps/pass_steps.py:3
          But note that "Arabella can speak English"           # ../behave4cmd0/note_steps.py:15
        """
      And the command output should not contain "ACTIVE-TAG DISABLED: Scenario Alice"
      But note that "we check now that tags for example rows are generated correctly"
      And the command output should not contain "@use.with_browserchrome"
      But the command output should contain "@use.with_browser=chrome"


    Scenario: ScenarioOutline with disabled active-tag is skipped
      Given a file named "features/outline2.active_tags.feature" with:
        """
        Feature:

          @use.with_browser=chrome
          Scenario Outline: Bob -- <name>, <language>
            Given some step passes
            But note that "<name> can speak <language>"

            Examples:
              | name     | language |
              | Bernhard | French   |
        """
      When I run "behave -D browser=other features/outline2.active_tags.feature"
      Then it should pass with:
        """
        0 scenarios passed, 0 failed, 1 skipped
        0 steps passed, 0 failed, 2 skipped, 0 undefined
        """
      And the command output should contain:
        """
        ACTIVE-TAG DISABLED: Scenario Bob -- Bernhard, French -- @1.1
        """

    Scenario: ScenarioOutline with generated active-tag
      Given a file named "features/outline3.active_tags.feature" with:
        """
        Feature:

          @use.with_browser=<browser>
          Scenario Outline: Charly -- <name>, <language>, <browser>
            Given a step passes
            But note that "<name> can speak <language>"

            Examples:
              | name     | language | browser | Comment |
              | Anna     | German   | firefox | Should be skipped  when browser=chrome |
              | Arabella | English  | chrome  | Should be executed when browser=chrome |
        """
      When I run "behave -D browser=chrome features/outline3.active_tags.feature"
      Then it should pass with:
        """
        1 scenario passed, 0 failed, 1 skipped
        2 steps passed, 0 failed, 2 skipped, 0 undefined
        """
      And the command output should contain:
        """
        ACTIVE-TAG DISABLED: Scenario Charly -- Anna, German, firefox -- @1.1
        """
      And the command output should not contain:
        """
        ACTIVE-TAG DISABLED: Scenario Charly -- Arabella, English, chrome -- @1.2
        """
      And the command output should contain:
        """
        ACTIVE-TAG DISABLED: Scenario Charly -- Anna, German, firefox -- @1.1

        @use.with_browser=chrome
        Scenario Outline: Charly -- Arabella, English, chrome -- @1.2   # features/outline3.active_tags.feature:11
          Given a step passes                                           # features/steps/pass_steps.py:3
          But note that "Arabella can speak English"                    # ../behave4cmd0/note_steps.py:15
        """
