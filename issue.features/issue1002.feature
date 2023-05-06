@issue
Feature: Issue #1002 -- ScenarioOutline with Empty Placeholder Values in Examples Table

  SEE: https://github.com/behave/behave/issues/1002
  SEE: https://github.com/behave/behave/issues/1045 (duplicated)

  . COMMENTS:
  .  * Named placeholders in the "parse" module do not match EMPTY-STRING (anymore)
  .
  . SOLUTIONS:
  .  * Use "Cardinality field parser (cfparse) with optional word, like: "{param:Word?}"
  .  * Use a second step alias that matches empty string, like:
  .
  .      @step(u'I meet with "{name}"')
  .      @step(u'I meet with ""')
  .      def step_meet_person_with_name(ctx, name=""):
  .          if not name:
  .              name = "NOBODY"
  .
  .  * Use explicit type converters instead of MATCH-ANYTHING (non-empty), like:
  .
  .     @parse.with_pattern(r".*")
  .     def parse_any_text(text):
  .         return text
  .
  .     @parse.with_pattern(r'[^"]*')
  .     def parse_unquoted_or_empty_text(text):
  .         return text
  .
  .     register_type(AnyText=parse_any_text)
  .     register_type(Unquoted=parse_unquoted_or_empty_text)
  .
  .     # -- VARIANT 1:
  .     @step('Passing parameter "{param:AnyText}"')
  .     def step_use_parameter_v1(context, param):
  .         print(param)
  .
  .     # -- VARIANT 2 (ALTERNATIVE: either/or):
  .     @step('Passing parameter "{param:Unquoted}"')
  .     def step_use_parameter_v2(context, param):
  .         print(param)

  Background: Test Setup
    Given a new working directory
    And a file named "features/example_1002.feature" with:
      """
      Feature:
        Scenario Outline: Meet with <name>
          When I meet with "<name>"

        Examples:
          | name   | case |
          | Alice  | Non-empty value |
          |        | Empty string (SYNDROME) |
      """

  Scenario: SOLUTION 1: Use another step binding for empty-string
    Given a file named "features/steps/steps.py" with:
      """
      # -- FILE: features/steps/steps.py
      from behave import step

      @step(u'I meet with "{name}"')
      @step(u'I meet with ""')  # -- SPECIAL CASE: Match EMPTY-STRING
      def step_meet_with_person(ctx, name=""):
          ctx.other_person = name
      """
    When I run "behave -f plain features/example_1002.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "NotImplementedError"


  Scenario: SOLUTION 2: Use a placeholder type -- AnyText
    Given a file named "features/steps/steps.py" with:
      """
      # -- FILE: features/steps/steps.py
      from behave import step, register_type
      import parse

      @parse.with_pattern(r".*")
      def parse_any_text(text):
            # -- SUPPORTS: AnyText including EMPTY string.
            return text

      register_type(AnyText=parse_any_text)

      @step(u'I meet with "{name:AnyText}"')
      def step_meet_with_person(ctx, name):
          ctx.other_person = name
      """
    When I run "behave -f plain features/example_1002.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "NotImplementedError"


  Scenario: SOLUTION 3: Use a placeholder type -- Unquoted_or_Empty
    Given a file named "features/steps/steps.py" with:
      """
      # -- FILE: features/steps/steps.py
      from behave import step, register_type
      import parse

      @parse.with_pattern(r'[^"]*')
      def parse_unquoted_or_empty_text(text):
          return text

      register_type(Unquoted_or_Empty=parse_unquoted_or_empty_text)

      @step(u'I meet with "{name:Unquoted_or_Empty}"')
      def step_meet_with_person(ctx, name):
          # -- SUPPORTS: Unquoted text including EMPTY string
          ctx.other_person = name
      """
    When I run "behave -f plain features/example_1002.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "NotImplementedError"


  Scenario: SOLUTION 4: Use a placeholder type -- OptionalUnquoted
    Given a file named "features/steps/steps.py" with:
      """
      # -- FILE: features/steps/steps.py
      # USE: cfparse with cardinality-field support for: Optional
      from behave import step, register_type, use_step_matcher
      import parse

      @parse.with_pattern(r'[^"]+')
      def parse_unquoted(text):
          # -- SUPPORTS: Non-empty unquoted-text
          return text

      register_type(Unquoted=parse_unquoted)
      use_step_matcher("cfparse") # -- SUPPORT FOR: OptionalUnquoted

      @step(u'I meet with "{name:Unquoted?}"')
      def step_meet_with_person(ctx, name):
          ctx.other_person = name
      """
    When I run "behave -f plain features/example_1002.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "NotImplementedError"


  Scenario: SOLUTION 5: Use a placeholder type -- OptionalWord
    Given a file named "features/steps/steps.py" with:
      """
      # -- FILE: features/steps/steps.py
      # USE: cfparse (with cardinality-field support for: Optional)
      from behave import step, register_type, use_step_matcher
      import parse

      @parse.with_pattern(r'[A-Za-z0-9_\-\.]+')
      def parse_word(text):
          # -- SUPPORTS: Word but not an EMPTY string
          return text

      register_type(Word=parse_word)
      use_step_matcher("cfparse")   # -- NEEDED FOR: Optional

      @step(u'I meet with "{name:Word?}"')
      def step_meet_with_person(ctx, name):
          ctx.other_person = name
      """
    When I run "behave -f plain features/example_1002.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped
      """
    And the command output should not contain "NotImplementedError"
