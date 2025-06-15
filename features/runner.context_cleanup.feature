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


  Background:
    Given a new working directory
    And a file named "behave.ini" with:
      """
      [behave]
      show_timings = false
      capture = true
      """
    And a file named "features/steps/use_steps.py" with:
      """
      import behave4cmd0.passing_steps
      """

  Rule: Good cases
    Background: Rule Setup
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import capture_output, any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        class SomeError(RuntimeError): pass

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
        @capture_output(show_on_success=True)
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
      And a file named "features/alice.feature" with:
        """
        Feature: Alice
          Scenario: A1
            Given a step passes

          Scenario: A2
            When another step passes
        """

    @cleanup.after_testrun
    Scenario: Cleanup registered in before_all hook
      When I run "behave -D use_cleanup_after_testrun -f plain features/alice.feature"
      Then it should pass with:
        """
        CALLED-HOOK: before_all
        REGISTER-CLEANUP: cleanup_after_testrun
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_after_testrun
        """
      But note that "the complete details are shown below"
      And the command output should contain:
        """
        ----
        CAPTURED STDOUT:
        CALLED-HOOK: before_all
        REGISTER-CLEANUP: cleanup_after_testrun
        ----
        Feature: Alice
        ----
        CAPTURED STDOUT: before_feature
        CALLED-HOOK: before_feature:Alice
        ----

          Scenario: A1
            Given a step passes ... passed

          Scenario: A2
            When another step passes ... passed
        ----
        CAPTURED STDOUT: after_feature
        CALLED-HOOK: after_feature: Alice
        ----

        ----
        CAPTURED STDOUT: after_all
        CALLED-HOOK: after_all
        ----
        CALLED: cleanup_after_testrun
        """


    @cleanup.after_feature
    Scenario: Cleanup registered in before_feature hook
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

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
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_foo
        """
      But note that "the complete details are shown below"
      And the command output should contain:
        """
        Feature: Bob
        ----
        CAPTURED STDOUT: before_feature
          CALLED-HOOK: before_feature:Bob
          REGISTER-CLEANUP: cleanup_foo
        ----
          Scenario: B1
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: after_feature
        CALLED-HOOK: after_feature:Bob
        ----
        ----
        CAPTURED STDOUT: feature.cleanup
        CALLED: cleanup_foo
        ----
        """

    @cleanup.after_scenario
    Scenario: Cleanup registered in before_scenario hook
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        # -- CLEANUP FUNCTIONS:
        def cleanup_foo():
            print("CALLED: cleanup_foo")

        # -- HOOKS:
        def before_scenario(context, scenario):
            print("CALLED-HOOK: before_scenario:%s" % scenario.name)
            if "cleanup_foo" in scenario.tags:
                print("REGISTER-CLEANUP: cleanup_foo")
                context.add_cleanup(cleanup_foo)
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
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_foo
        """
      But note that "the complete details are shown below"
      And the command output should contain:
        """
          Scenario: C1
        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:C1
        REGISTER-CLEANUP: cleanup_foo
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: cleanup_foo
        ----
        """


    @cleanup.after_scenario
    Scenario: Cleanups are executed in reverse registration order
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

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
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_bar
        CALLED: cleanup_foo
        """
      But note that "the cleanup-functions are called in reversed order"
      And note that "the complete details are shown below"
      And the command output should contain:
        """
          Scenario: D1
        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:D1
        REGISTER-CLEANUP: cleanup_foo
        REGISTER-CLEANUP: cleanup_bar
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: cleanup_bar
        CALLED: cleanup_foo
        ----
        """

    @cleanup.after_scenario
    Scenario: Cleanup registered in step implementation
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

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

        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:E1
        ----
              Given I register a cleanup "cleanup_foo" ... passed
        ----
        CAPTURED STDOUT: after_scenario
        CALLED-HOOK: after_scenario:E1
        ----
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: cleanup_foo
        ----
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_foo
        """

    @cleanup.after_scenario
    Scenario: Registered cleanup function args are passed to cleanup
      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

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
          Scenario: F1
        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:F1
        REGISTER-CLEANUP: cleanup_foo("Alice")
        REGISTER-CLEANUP: cleanup_foo("Bob")
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: after_scenario
        CALLED-HOOK: after_scenario:F1
        ----
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: cleanup_foo("Bob")
        CALLED: cleanup_foo("Alice")
        ----
        """
      But note that "cleanup args are used by registered cleanup-functions"


  Rule: Bad Cases

    @error.in.cleanup_function
    @cleanup.after_scenario
    Scenario: Cleanup function raises Error
      INTENTION: All registered cleanups must be called.

      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        any_hook.show_capture_on_success = True
        any_hook.show_cleanup_on_success = True

        class SomeError(RuntimeError): pass

        # -- CLEANUP FUNCTIONS:
        def cleanup_foo():
            print("CALLED: cleanup_foo")

        def bad_cleanup_bar():
            print("CALLED: bad_cleanup_bar -- PART_1")
            raise SomeError("CLEANUP-OOPS")
            print("CALLED: bad_cleanup_bar -- PART_2 -- NOT_REACHED")

        # -- HOOKS:
        def before_scenario(context, scenario):
            print("CALLED-HOOK: before_scenario:%s" % scenario.name)
            if "cleanup_foo" in scenario.tags:
                print("REGISTER-CLEANUP: cleanup_foo")
                context.add_cleanup(cleanup_foo)
            if "cleanup_bar" in scenario.tags:
                print("REGISTER-CLEANUP: bad_cleanup_bar")
                context.add_cleanup(bad_cleanup_bar)
        """
      And a file named "features/bad_cleanup.feature" with:
        """
        Feature: Bad Cleanup
          @cleanup_foo
          @cleanup_bar
          Scenario: E1
            Given a step passes

          Scenario: E2
            When a step passes
        """
      When I run "behave -f plain features/bad_cleanup.feature"
      Then it should fail with:
        """
        Errored scenarios:
          features/bad_cleanup.feature:4  E1

        0 features passed, 0 failed, 1 error, 0 skipped
        1 scenario passed, 0 failed, 1 cleanup_error, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: E1
        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:E1
        REGISTER-CLEANUP: cleanup_foo
        REGISTER-CLEANUP: bad_cleanup_bar
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: bad_cleanup_bar -- PART_1
        CLEANUP-ERROR in bad_cleanup_bar: SomeError: CLEANUP-OOPS
        """
      And the command output should contain:
        """
          File "features/environment.py", line 15, in bad_cleanup_bar
            raise SomeError("CLEANUP-OOPS")
        """
      And the command output should contain:
        """
        SomeError: CLEANUP-OOPS
        CALLED: cleanup_foo
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_foo
        """
      And the command output should not contain:
        """
        CALLED: bad_cleanup_bar -- PART_2 -- NOT_REACHED
        """
      But note that "all cleanup functions are called when bad_cleanup raises an error"


    @error.in.before_scenario
    @cleanup.after_scenario
    Scenario: Hook before_scenario raises Error
      INTENTION: Registered cleanups are performed.

      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        class SomeError(RuntimeError): pass

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

            # -- PROBLEM-POINT:
            if "problem_point" in scenario.tags:
                raise SomeError("OOPS")

        def after_scenario(context, scenario):
            print("CALLED-HOOK: after_scenario:%s" % scenario.name)

        # -- ENABLE CAPTURED-OUTPUT:
        any_hook.show_cleanup_on_success = True
        after_scenario.show_capture_on_success = True
        """
      And a file named "features/bad_antony.feature" with:
        """
        Feature: Bad Antony
          @cleanup_foo
          @cleanup_bar
          @problem_point
          Scenario: E1
            Given a step passes

          Scenario: E2
            When a step passes
        """
      When I run "behave -f plain features/bad_antony.feature"
      Then it should fail with:
        """
        0 features passed, 0 failed, 1 error, 0 skipped
        1 scenario passed, 0 failed, 1 hook_error, 0 skipped
        1 step passed, 0 failed, 0 skipped, 1 untested
        """
      And the command output should contain:
        """
          Scenario: E1
        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:E1
        REGISTER-CLEANUP: cleanup_foo
        REGISTER-CLEANUP: cleanup_bar
        HOOK-ERROR in before_scenario: SomeError: OOPS
        ----
        ----
        CAPTURED STDOUT: after_scenario
        CALLED-HOOK: after_scenario:E1
        ----
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: cleanup_bar
        CALLED: cleanup_foo
        ----
        """
      And the command output should contain 1 times:
        """
        CALLED: cleanup_bar
        CALLED: cleanup_foo
        """
      But note that "cleanup functions are called even if an HOOK-ERROR occurs"

    @error.in.after_scenario
    @cleanup.after_scenario
    Scenario: Hook after_scenario raises Error
      INTENTION: Registered cleanups are performed.

      Given a file named "features/environment.py" with:
        """
        from __future__ import absolute_import, print_function
        from behave.capture import any_hook

        class SomeError(RuntimeError): pass

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

            # -- PROBLEM-POINT:
            if "problem_point" in scenario.tags:
                raise SomeError("OOPS")

        # -- ENABLE CAPTURED-OUTPUT: On captured output parts.
        any_hook.show_cleanup_on_success = True
        before_scenario.show_capture_on_success = True
        after_scenario.show_capture_on_success = True
        """
      And a file named "features/bad_bob.feature" with:
        """
        Feature: Bad Bob
          @cleanup_foo
          @cleanup_bar
          @problem_point
          Scenario: E1
            Given a step passes

          Scenario: E2
            When a step passes
        """
      When I run "behave -f plain --capture features/bad_bob.feature"
      Then it should fail with:
        """
        Errored scenarios:
          features/bad_bob.feature:5  E1

        0 features passed, 0 failed, 1 error, 0 skipped
        1 scenario passed, 0 failed, 1 hook_error, 0 skipped
        2 steps passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
          Scenario: E1
        ----
        CAPTURED STDOUT: before_scenario
        CALLED-HOOK: before_scenario:E1
        REGISTER-CLEANUP: cleanup_foo
        REGISTER-CLEANUP: cleanup_bar
        ----
            Given a step passes ... passed
        ----
        CAPTURED STDOUT: after_scenario
        CALLED-HOOK: after_scenario:E1
        HOOK-ERROR in after_scenario: SomeError: OOPS
        ----
        ----
        CAPTURED STDOUT: scenario.cleanup
        CALLED: cleanup_bar
        CALLED: cleanup_foo
        ----
        """
      And the command output should contain:
        """
        Scenario: E2
          ----
          CAPTURED STDOUT: before_scenario
          CALLED-HOOK: before_scenario:E2
          ----
              When a step passes ... passed
          ----
          CAPTURED STDOUT: after_scenario
          CALLED-HOOK: after_scenario:E2
          ----
        """
      But note that "cleanup functions are called even if an HOOK-ERROR occurs"

