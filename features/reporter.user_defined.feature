Feature: Use a user-defined Reporter

  As a behave user
  I want to be able to provide own, user-defined reporters
  So that I am able to add a new, user-defined reporters
  when I need other output formats (or override existing ones).

  . SPECIFICATION
  .   * A user-defined reporter must inherit from the "Reporter" class.
  .   * A user-defined reporter can be specified on command-line
  .     by using a scoped class name as value for the '--report' option.
  .
  . SCOPED CLASS NAME (for reporter.class):
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
      And a file named "behave_ext/reporters.py" with:
      """
      from behave.reporter.base import Reporter

      class NotAReporter(object): pass
      class OversimplifiedReporter(Reporter):
          def __init__(self, config):
              self.status = 'passed'

          def feature(self, feature):
              print('feature:', feature.status)
              if feature.status == 'failed':
                  self.status = 'failed'

          def end(self):
              print('all tests:', self.status)
      """

  Scenario: Use a known, valid user-defined reporter with scoped class name
    When I run "behave -r behave_ext.reporters:OversimplifiedReporter features/passing.feature"
    Then it should pass with:
      """
      feature: passed
      all tests: passed
      """

  Scenario: Use a known, valid user-defined reporter with scoped class name

    ALTERNATIVE: Can currently use a double colon as separator, too.

    When I run "behave -r behave_ext.reporters::OversimplifiedReporter features/passing.feature"
    Then it should pass with:
      """
      feature: passed
      all tests: passed
      """

  @problematic
  Scenario Outline: Use a problematic user-defined reporter (<case>)
    When I run "behave -r <reporter.class> features/passing.feature"
    Then it should fail with:
      """
      Exception: reporter=<reporter.class> is unknown
      """

    Examples:
    | reporter.class                    | case                   |
    | my.unknown_module:SomeReporter    | Unknown module         |
    | behave_ext.reporters:UnknownClass | Unknown class          |
    | behave_ext.reporters:NotAReporter | Invalid Reporter class |
