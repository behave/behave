Feature: Perform Context.cleanups at the end of a test-run, feature or scenario (scope guards)

  As a test writer
  I want to perform cleanups (tear-downs) of functionality at the end of a test-run, feature or scenario
  So that I can easily implement the "scope guard" design pattern (Python: contextmanager)

  . SPECIFICATION:
  .   * Context.add_cleanup(func) is provided to register cleanup functions
  .   * Cleanup functions are registered in the current layer of the context object stack.
  .   * Cleanup functions are executed before the current layer of the context object is removed/popped.
  .   * Cleanup functions are executed in reverse order of registration
  .     (LIFO: first registered cleanup function will be executed last, etc.)
  .   * Cleanup functions are executed in best-effort mode: If one fails, the others are still executed
  .   * Behaviour when the execution of cleanup function fails should be adjustable
  .
  .   | Scope/Layer | Cleanup Registration Point  | Cleanup Execution Point |
  .   | test-run    | In before_all() hook        | After after_all() hook is executed.      |
  .   | feature     | In before_feature() hook    | After after_feature() hook is executed.  |
  .   | feature     | In before_tag() in Feature  | After after_feature() hook is executed.  |
  .   | scenario    | In before_scenario() hook   | After after_scenario() hook is executed. |
  .   | scenario    | In before_tag() in Scenario | After after_scenario() hook is executed. |
  .   | scenario    | In step implementation      | After after_scenario() hook is executed. |
  .   | scenario    | In step hooks               | After after_scenario() hook is executed. |


  @setup
  Scenario: Test Setup
    Given a new working directory
    And a file named "features/environment.py" with:
      """
      from __future__ import print_function

      # -- CLEANUP FUNCTIONS:
      class CleanupFuntion(object):
          def __init__(self, name=None):
              self.name = name or ""

          def __call__(self):
              print("CALLED: CleanupFunction:%s" % self.name)

      def cleanup_after_testrun():
          print("CALLED: cleanup_after_testrun")

      def cleanup_foo():
          print("CALLED: cleanup_foo")

      def cleanup_bar():
          print("CALLED: cleanup_bar")

      # -- HOOKS:
      def before_all(context):
          print("CALLED-HOOK: before_all")
          userdata = context.config.userdata
          use_cleanup = userdata.getbool("use_cleanup_after_testrun")
          if use_cleanup:
              print("REGISTER-CLEANUP: cleanup_after_testrun")
              context.add_cleanup(cleanup_after_testrun)

      def before_feature(context, feature):
          print("CALLED-HOOK: before_feature:%s" % feature.name)
          userdata = context.config.userdata
          use_cleanup = userdata.getbool("use_cleanup_after_feature")
          if use_cleanup and "cleanup.after_feature" in feature.tags:
              print("REGISTER-CLEANUP: cleanup_foo")
              context.add_cleanup(cleanup_foo)

      def after_feature(context, feature):
          print("CALLED-HOOK: after_feature: %s" % feature.name)

      def after_all(context):
          print("CALLED-HOOK: after_all")
      """
    And a file named "features/steps/use_steps.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/alice.feature" with:
      """
      Feature: Alice
        Scenario: A1
          Given a step passes

        Scenario: A2
          When another step passes
      """
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      stdout_capture = true
      """

  @cleanup.after_testrun
  Scenario: Cleanup registered in before_all hook
    When I run "behave -D use_cleanup_after_testrun -f plain features/alice.feature"
    Then it should pass with:
      """
      CALLED-HOOK: before_all
      REGISTER-CLEANUP: cleanup_after_testrun
      CALLED-HOOK: before_feature:Alice
      Feature: Alice
      """
    And the command output should contain:
      """
      Scenario: A2
        When another step passes ... passed

      CALLED-HOOK: after_feature: Alice
      CALLED-HOOK: after_all
      CALLED: cleanup_after_testrun
      """

  @cleanup.after_feature
  Scenario: Cleanup registered in before_feature hook
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function

      # -- CLEANUP FUNCTIONS:
      def cleanup_foo():
          print("CALLED: cleanup_foo")

      # -- HOOKS:
      def before_feature(context, feature):
          print("CALLED-HOOK: before_feature:%s" % feature.name)
          if "cleanup.after_feature" in feature.tags:
              print("REGISTER-CLEANUP: cleanup_foo")
              context.add_cleanup(cleanup_foo)

      def after_feature(context, feature):
          print("CALLED-HOOK: after_feature:%s" % feature.name)

      def after_all(context):
          print("CALLED-HOOK: after_all")
      """
    And a file named "features/bob.feature" with:
      """
      @cleanup.after_feature
      Feature: Bob
        Scenario: B1
          Given a step passes
      """
    When I run "behave -f plain features/bob.feature"
    Then it should pass with:
      """
      CALLED-HOOK: before_feature:Bob
      REGISTER-CLEANUP: cleanup_foo
      Feature: Bob
      """
    And the command output should contain:
      """
      Scenario: B1
        Given a step passes ... passed

      CALLED-HOOK: after_feature:Bob
      CALLED: cleanup_foo
      CALLED-HOOK: after_all
      """


  @cleanup.after_scenario
  Scenario: Cleanup registered in before_scenario hook
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function

      # -- CLEANUP FUNCTIONS:
      def cleanup_foo():
          print("CALLED: cleanup_foo")

      # -- HOOKS:
      def before_scenario(context, scenario):
          print("CALLED-HOOK: before_scenario:%s" % scenario.name)
          if "cleanup_foo" in scenario.tags:
              print("REGISTER-CLEANUP: cleanup_foo")
              context.add_cleanup(cleanup_foo)

      def after_scenario(context, scenario):
          print("CALLED-HOOK: after_scenario:%s" % scenario.name)
      """
    And a file named "features/charly.feature" with:
      """
      Feature: Charly
        @cleanup_foo
        Scenario: C1
          Given a step passes

        Scenario: C2
          When a step passes
      """
    When I run "behave -f plain features/charly.feature"
    Then it should pass with:
      """
      CALLED-HOOK: before_scenario:C1
      REGISTER-CLEANUP: cleanup_foo
      Scenario: C1
      """
    And the command output should contain:
      """
      Scenario: C1
        Given a step passes ... passed

      CALLED-HOOK: after_scenario:C1
      CALLED: cleanup_foo
      CALLED-HOOK: before_scenario:C2
      """

  @cleanup.after_scenario
  Scenario: Cleanups are executed in reverse registration order

    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function

      # -- CLEANUP FUNCTIONS:
      def cleanup_foo():
          print("CALLED: cleanup_foo")

      def cleanup_bar():
          print("CALLED: cleanup_bar")

      # -- HOOKS:
      def before_scenario(context, scenario):
          print("CALLED-HOOK: before_scenario:%s" % scenario.name)
          if "cleanup_foo" in scenario.tags:
              print("REGISTER-CLEANUP: cleanup_foo")
              context.add_cleanup(cleanup_foo)
          if "cleanup_bar" in scenario.tags:
              print("REGISTER-CLEANUP: cleanup_bar")
              context.add_cleanup(cleanup_bar)

      def after_scenario(context, scenario):
          print("CALLED-HOOK: after_scenario:%s" % scenario.name)
      """
    And a file named "features/dodo.feature" with:
      """
      Feature: Dodo
        @cleanup_foo
        @cleanup_bar
        Scenario: D1
          Given a step passes

        Scenario: D2
          When a step passes
      """
    When I run "behave -f plain features/dodo.feature"
    Then it should pass with:
      """
      CALLED-HOOK: before_scenario:D1
      REGISTER-CLEANUP: cleanup_foo
      REGISTER-CLEANUP: cleanup_bar
      Scenario: D1
      """
    And the command output should contain:
      """
      Scenario: D1
        Given a step passes ... passed

      CALLED-HOOK: after_scenario:D1
      CALLED: cleanup_bar
      CALLED: cleanup_foo
      CALLED-HOOK: before_scenario:D2
      """
    And the command output should contain 1 times:
      """
      CALLED: cleanup_bar
      CALLED: cleanup_foo
      """

  @cleanup.after_scenario
  Scenario: Cleanup registered in step implementation
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function

      # -- HOOKS:
      def before_scenario(context, scenario):
          print("CALLED-HOOK: before_scenario:%s" % scenario.name)

      def after_scenario(context, scenario):
          print("CALLED-HOOK: after_scenario:%s" % scenario.name)
      """
    And a file named "features/steps/cleanup_steps.py" with:
      """
      from behave import given

      # -- CLEANUP FUNCTIONS:
      def cleanup_foo():
          print("CALLED: cleanup_foo")

      # -- STEPS:
      @given(u'I register a cleanup "{cleanup_name}"')
      def step_register_cleanup(context, cleanup_name):
          if cleanup_name == "cleanup_foo":
              context.add_cleanup(cleanup_foo)
          else:
              raise KeyError("Unknown_cleanup:%s" % cleanup_name)
      """
    And a file named "features/emily.feature" with:
      """
      Feature: Emily
        Scenario: E1
          Given I register a cleanup "cleanup_foo"

        Scenario: E2
          When a step passes
      """
    When I run "behave -f plain features/emily.feature"
    Then it should pass with:
      """
      Scenario: E1
          Given I register a cleanup "cleanup_foo" ... passed

      CALLED-HOOK: after_scenario:E1
      CALLED: cleanup_foo
      CALLED-HOOK: before_scenario:E2
      """
    And the command output should contain 1 times:
      """
      CALLED: cleanup_foo
      """

  @cleanup.after_scenario
  Scenario: Registered cleanup function args are passed to cleanup
    Given a file named "features/environment.py" with:
      """
      from __future__ import print_function

      # -- CLEANUP FUNCTIONS:
      def cleanup_foo(text):
          print('CALLED: cleanup_foo("%s")' % text)

      # -- HOOKS:
      def before_scenario(context, scenario):
          print("CALLED-HOOK: before_scenario:%s" % scenario.name)
          if "cleanup_foo" in scenario.tags:
              print('REGISTER-CLEANUP: cleanup_foo("Alice")')
              context.add_cleanup(cleanup_foo, "Alice")
              print('REGISTER-CLEANUP: cleanup_foo("Bob")')
              context.add_cleanup(cleanup_foo, "Bob")

      def after_scenario(context, scenario):
          print("CALLED-HOOK: after_scenario:%s" % scenario.name)
      """
    And a file named "features/frank.feature" with:
      """
      Feature: Frank
        @cleanup_foo
        Scenario: F1
          Given a step passes

        Scenario: F2
          When a step passes
      """
    When I run "behave -f plain features/frank.feature"
    Then it should pass with:
      """
      CALLED-HOOK: before_scenario:F1
      REGISTER-CLEANUP: cleanup_foo("Alice")
      REGISTER-CLEANUP: cleanup_foo("Bob")
      Scenario: F1
      """
    And the command output should contain:
      """
      Scenario: F1
        Given a step passes ... passed

      CALLED-HOOK: after_scenario:F1
      CALLED: cleanup_foo("Bob")
      CALLED: cleanup_foo("Alice")
      CALLED-HOOK: before_scenario:F2
      """
