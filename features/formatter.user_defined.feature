Feature: Use a user-defined Formatter

  As a behave user
  I want to be able to provide own, user-defined formatters
  So that I am able to add a new, user-defined formatters
  when I need other output formats (or override existing ones).

  . SPECIFICATION:
  .   * A user-defined formatter must inherit from the "Formatter" class.
  .   * A user-defined formatter can be specified on command-line
  .     by using a scoped class name as value for the '--format' option.
  .   * A user-defined formatter can be registered by name
  .     by using the "behave.formatters" section in the behave config file.
  .
  . SCOPED CLASS NAME (for formatter.class):
  .   * my.module_name:ClassName   (preferred:   single colon separator)
  .   * my.module_name::ClassName  (alternative: double colon separator)


  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/passing_steps.py" with:
      """
      from behave import step

      @step('{word:w} step passes')
      def step_passes(context, word):
          pass

      @step('{word:w} step fails')
      def step_fails(context, word):
          assert False, "XFAIL-STEP"
      """
    And a file named "features/passing.feature" with:
      """
      Feature:
        Scenario: Alice
          Given a step passes
          When another step passes

        Scenario: Bob
          Then some step passes
      """
    And an empty file named "behave_ext/__init__.py"
    And a file named "behave_ext/formatter_one.py" with:
      """
      from behave.formatter.base import Formatter

      class NotAFormatter(object): pass
      class SuperFormatter(Formatter):
          name = "super"
          description = "Super-duper formatter."
      """
    And a file named "behave_ext/formatter_foo.py" with:
      """
      from behave.formatter.base import Formatter

      class FooFormatter(Formatter):
          name = "foo"
          description = "User-specific FOO formatter."

      class FooFormatter2(Formatter):
          description = "User-specific FOO2 formatter."
      """
    And a file named "behave_ext/formatter_bar.py" with:
      """
      from behave.formatter.base import Formatter

      class BarFormatter(Formatter):
          description = "User-specific BAR formatter."
      """

  @use_formatter.class
  Scenario: Use a known, valid user-defined formatter with scoped class name
    When I run "behave -f behave_ext.formatter_one:SuperFormatter features/passing.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """

  @use_formatter.class
  Scenario: Use a known, valid user-defined formatter (with double colon)

    ALTERNATIVE: Can currently use a double colon as separator, too.

    When I run "behave -f behave_ext.formatter_one::SuperFormatter features/passing.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """


  @use_formatter.class
  Scenario Outline: Use built-in formatter "<formatter.name>" like a user-defined formatter
    When I run "behave -f <formatter.class> features/passing.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """

    Examples:
      | formatter.name | formatter.class |
      | plain          | behave.formatter.plain:PlainFormatter |
      | pretty         | behave.formatter.pretty:PrettyFormatter |


  @problematic
  @use_formatter.class
  Scenario Outline: Use a problematic user-defined formatter (<case>)
    When I run "behave -f <formatter.class> features/passing.feature"
    Then it should fail with:
      """
      error: format=<formatter.class> is unknown
      """

    Examples:
      | formatter.class                         | case            |
      | my.unknown_module:SomeFormatter         | Unknown module  |
      | behave_ext.formatter_one:UnknownClass   | Unknown class   |
      | behave_ext.formatter_one:NotAFormatter  | Invalid Formatter class |


  @formatter.registered_by_name
  Scenario Outline: Register user-defined formatter by name: <formatter.name>
    Given a file named "behave.ini" with:
      """
      [behave.formatters]
      foo  = behave_ext.formatter_foo:FooFormatter
      foo2 = behave_ext.formatter_foo:FooFormatter2
      bar  = behave_ext.formatter_bar:BarFormatter
      """
    And note that "the schema: 'formatter.name = formatter.class' is used"
    When I run "behave -f <formatter.name> features/passing.feature"
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      """
    But the command output should not contain:
      """
      error: format=<formatter.name> is unknown
      """

    Examples:
      | formatter.name | Comment |
      | foo            | First user-defined, registered formatter. |
      | bar            | Last  user-defined, registered formatter. |


  @formatter.registered_by_name
  Scenario: Help-Format shows description of registered-by-name formatters
    Given a file named "behave.ini" with:
      """
      [behave.formatters]
      foo = behave_ext.formatter_foo:FooFormatter
      bar = behave_ext.formatter_bar:BarFormatter
      """
    When I run "behave -f help"
    Then it should pass with:
      """
      Available formatters:
      """
    And the command output should contain:
      """
      bar            User-specific BAR formatter.
      """
    And the command output should contain:
      """
      foo            User-specific FOO formatter.
      """


  @problematic
  @formatter.registered_by_name
  Scenario Outline: Use problematic, registered-by-name formatter: <case>
    Given a file named "behave.ini" with:
      """
      [behave.formatters]
      <formatter.name> = <formatter.class>
      """
    When I run "behave -f <formatter.name> features/passing.feature"
    Then it should fail with:
      """
      error: format=<formatter.name> is unknown
      """

    Examples:
      | formatter.name | formatter.class                        | case            |
      | unknown1       | my.unknown_module:SomeFormatter        | Unknown module  |
      | unknown2       | behave_ext.formatter_one:UnknownClass  | Unknown class   |
      | invalid1       | behave_ext.formatter_one:NotAFormatter | Invalid Formatter class |

