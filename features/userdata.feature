Feature: User-specific Configuration Data (userdata)

  As a test writer
  I want to provide my own configuration data
  So that the test suite and/or the environment can be adapted to its needs.

  . MECHANISM:
  .   * Use -D name=value (--define) option to specify user data on command-line.
  .   * Specify user data in section "behave.userdata" of "behave.ini"
  .   * Load/setup user data in before_all() hook (advanced cases)
  .
  . USING USER DATA:
  .   * context.config.userdata (as dict)
  .
  . SUPPORTED DATA TYPES (from "behave.ini" and command-line):
  .   * string
  .   * bool-like (= "true", if definition has no value)

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
    And a file named "features/steps/userdata_steps.py" with:
        """
        from behave import step
        from hamcrest import assert_that, equal_to

        @step('the following user-data is provided')
        def step_userdata_is_provided_with_table(context):
            assert context.table, "REQUIRE: table"
            context.table.require_columns(["name", "value"])
            userdata = context.config.userdata
            for row in context.table.rows:
                name = row["name"]
                expected_value = row["value"]
                if name in userdata:
                    actual_value = userdata[name]
                    assert_that(str(actual_value), equal_to(expected_value))
                else:
                    assert False, "MISSING: userdata %s" % name

        @step('I modify the user-data with')
        def step_modify_userdata_with_table(context):
            assert context.table, "REQUIRE: table"
            context.table.require_columns(["name", "value"])
            userdata = context.config.userdata
            for row in context.table.rows:
                name = row["name"]
                value = row["value"]
                userdata[name] = value
        """

  @userdata.define
  Scenario: Use define command-line option
    Given a file named "features/userdata_ex1.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value |
              | person1 | Alice |
              | person2 | Bob   |
        """
    And an empty file named "behave.ini"
    When I run "behave -D person1=Alice --define person2=Bob features/userdata_ex1.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.define
  Scenario: Duplicated define with other value overrides first value
    Given a file named "features/userdata_ex2.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value |
              | person1 | Bob   |
        """
    And an empty file named "behave.ini"
    When I run "behave -D person1=Alice -D person1=Bob features/userdata_ex2.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.define
  Scenario: Use boolean flag as command-line definition

    Ensure that command-line define without value part is a boolean flag.

    Given a file named "features/userdata_ex3.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value |
              | DEBUG   | true  |
        """
    And an empty file named "behave.ini"
    When I run "behave -D DEBUG features/userdata_ex3.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.config
  Scenario: Use user-data from behave configuration file
    Given a file named "behave.ini" with:
        """
        [behave.userdata]
        person1 = Alice
        person2 = Bob
        """
    When I run "behave features/userdata_ex1.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.config
  Scenario: Override user-data from behave configuration file on command-line
    Given a file named "features/userdata_config2.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value   |
              | person1 | Charly  |
              | person2 | Bob     |
        """
    And a file named "behave.ini" with:
        """
        [behave.userdata]
        person1 = Alice
        person2 = Bob
        """
    When I run "behave -D person1=Charly features/userdata_config2.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.config
  Scenario: Extend user-data from behave configuration file on command-line
    Given a file named "features/userdata_config3.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value   |
              | person1 | Alice   |
              | person2 | Bob     |
              | person3 | Charly  |
        """
    And a file named "behave.ini" with:
        """
        [behave.userdata]
        person1 = Alice
        person2 = Bob
        """
    When I run "behave -D person3=Charly features/userdata_config3.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.load
  Scenario: Load user-data configuration in before_all hook (JSON)
    Given an empty file named "behave.ini"
    And a file named "features/environment.py" with:
        """
        import json
        import os.path

        def before_all(context):
            userdata = context.config.userdata
            configfile = userdata.get("configfile", "userconfig.json")
            if os.path.exists(configfile):
                config = json.load(open(configfile))
                userdata.update(config)
        """
    And a file named "userconfig.json" with:
        """
        {
            "person1": "Anna",
            "person2": "Beatrix"
        }
        """
    And a file named "features/userdata_load1.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value   |
              | person1 | Anna    |
              | person2 | Beatrix |
        """
    When I run "behave features/userdata_load1.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @userdata.load
  Scenario: Load user-data configuration in before_all hook (INI)
    Given a file named "behave.ini" with:
        """
        [behave.userdata]
        configfile     = userconfig.ini
        config_section = behave.userdata.more
        """
    And a file named "userconfig.ini" with:
        """
        [behave.userdata.more]
        person1 = Anna2
        person2 = Beatrix2
        """
    And a file named "features/environment.py" with:
        """
        try:
            import configparser
        except:
            import ConfigParser as configparser   # -- PY2

        def before_all(context):
            userdata = context.config.userdata
            configfile = userdata.get("configfile", "userconfig.ini")
            section = userdata.get("config_section", "behave.userdata")
            parser = configparser.SafeConfigParser()
            parser.read(configfile)
            if parser.has_section(section):
                userdata.update(parser.items(section))
        """
    And a file named "features/userdata_load2.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value   |
              | person1 | Anna2    |
              | person2 | Beatrix2 |
        """
    When I run "behave features/userdata_load2.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

  @bad_practice
  @userdata.modify
  Scenario: Modified user-data is used by the remaining features/scenarios

    Given a file named "features/userdata_modify1.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name    | value   |
              | person1 | Alice   |
              | person2 | Bob     |
            When I modify the user-data with:
              | name    | value   |
              | person1 | MODIFIED_VALUE |
            Then the following user-data is provided:
              | name    | value   |
              | person1 | MODIFIED_VALUE |
              | person2 | Bob     |

          Scenario: Next scenario has modified user-data, too
            Given the following user-data is provided:
              | name    | value   |
              | person1 | MODIFIED_VALUE |
              | person2 | Bob     |
        """
    And a file named "behave.ini" with:
        """
        [behave.userdata]
        person1 = Alice
        person2 = Bob
        """
    When I run "behave features/userdata_modify1.feature"
    Then it should pass with:
        """
        2 scenarios passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    But note that "modifying userdata is BAD-PRACTICE, except in before_all() hook"

  @userdata.case_sensitive
  Scenario: Loaded user-data from configuration should have case-sensitive keys

    Given a file named "features/userdata_case_sensitive.feature" with:
        """
        Feature:
          Scenario:
            Given the following user-data is provided:
              | name            | value |
              | CamelCaseKey    | 1     |
              | CAPS_SNAKE_KEY  | 2     |
              | lower_snake_key | 3     |
        """
    And a file named "behave.ini" with:
        """
        [behave.userdata]
        CamelCaseKey = 1
        CAPS_SNAKE_KEY = 2
        lower_snake_key = 3
        """
    When I run "behave features/userdata_case_sensitive.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """
