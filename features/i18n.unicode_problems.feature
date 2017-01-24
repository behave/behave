Feature: Internationalization (i18n) and Problems with Unicode Strings

  . POTENTIAL PROBLEM AREAS:
  .   * Feature, scenario, step names with problematic chars
  .   * Tags with problematic chars
  .   * step raises exception with problematic text (output capture)
  .   * step generates output with problematic and some step fails (stdout capture)
  .   * filenames with problematic chars: feature files, steps files
  .
  . CHECKED FORMATTERS and REPORTERS:
  .   * plain
  .   * pretty
  .   * junit   (used via "behave.ini" defaults)


  @setup
  Scenario: Feature Setup
      Given a new working directory
      And a file named "behave.ini" with:
        """
        [behave]
        show_timings = false
        show_skipped = false
        show_source  = true
        junit = true
        """
      And a file named "features/steps/passing_steps.py" with:
        """
        # -*- coding: UTF-8 -*-
        from behave import step

        @step(u'{word:w} step passes')
        def step_passes(context, word):
            pass

        @step(u'{word:w} step passes with "{text}"')
        def step_passes_with_text(context, word, text):
            pass

        @step(u'{word:w} step fails')
        def step_fails(context, word):
            assert False, "XFAIL"

        @step(u'{word:w} step fails with "{text}"')
        def step_fails_with_text(context, word, text):
            assert False, u"XFAIL: "+ text
        """
      And a file named "features/steps/step_write_output.py" with:
        """
        # -*- coding: UTF-8 -*-
        from __future__ import print_function
        from behave import step
        import six

        @step(u'I write text "{text}" to stdout')
        def step_write_text(context, text):
            if six.PY2 and isinstance(text, six.text_type):
                text = text.encode("utf-8", "replace")
            print(text)

        @step(u'I write bytes "{data}" to stdout')
        def step_write_bytes(context, data):
            if isinstance(data, six.text_type):
                data = data.encode("unicode-escape", "replace")
            print(data)
        """


  Scenario Outline: Problematic scenario name: <scenario.name> (case: passed, <format>)
      Given a file named "features/scenario_name_problematic_and_pass.feature" with:
        """
        Feature:
          Scenario: <scenario.name>
            Given a step passes
        """
      When I run "behave -f <format> features/scenario_name_problematic_and_pass.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        """
        Scenario: <scenario.name>
        """

      Examples:
        | format | scenario.name |
        | plain  | Café                 |
        | pretty | Ärgernis ist überall |


  Scenario Outline: Problematic scenario name: <scenario.name> (case: failed, <format>)
      Given a file named "features/scenario_name_problematic_and_fail.feature" with:
        """
        Feature:
          Scenario: <scenario.name>
            Given a step fails
        """
      When I run "behave -f <format> features/scenario_name_problematic_and_fail.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
        Scenario: <scenario.name>
        """

      Examples:
        | format | scenario.name |
        | plain  | Café                 |
        | pretty | Ärgernis ist überall |


  Scenario Outline: Problematic step: <step.text> (case: passed, <format>)
      Given a file named "features/step_problematic_and_pass.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes with "<step.text>"
        """
      When I run "behave -f <format> features/step_problematic_and_pass.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        1 step passed, 0 failed, 0 skipped, 0 undefined
        """

      Examples:
        | format | step.text |
        | plain  | Café                 |
        | pretty | Ärgernis ist überall |


  Scenario Outline: Problematic step: <step.text> (case: fail, <format>)
      Given a file named "features/step_problematic_and_fail.feature" with:
        """
        Feature:
          Scenario:
            Given a step fails with "<step.text>"
        """
      When I run "behave -f <format> features/step_problematic_and_fail.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        0 steps passed, 1 failed, 0 skipped, 0 undefined
        """

      Examples:
        | format | step.text |
        | plain  | Café                 |
        | pretty | Ärgernis ist überall |


  @problematic.feature_filename
  @not.with_os=win32
  Scenario Outline: Problematic feature filename: <name> (case: pass, <format>)
      Given a file named "features/<name>_and_pass.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
        """
      When I run "behave -f <format> features/<name>_and_pass.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        """

      Examples:
        | format | name |
        | plain  | Café |
        | pretty | Ärgernis_ist_überall |


  @problematic.feature_filename
  @not.with_os=win32
  Scenario Outline: Problematic feature filename: <name> (case: fail, <format>)
      Given a file named "features/<name>_and_fail.feature" with:
        """
        Feature:
          Scenario:
            Given a step fails
        """
      When I run "behave -f <format> features/<name>_and_fail.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        """

      Examples:
        | format | name |
        | plain  | Café |
        | pretty | Ärgernis_ist_überall |


  @problematic.step_filename
  Scenario Outline: Problematic step filename: <name> (case: pass, <format>)

    TEST-CONSTRAINT: Only one step file is used (= 1 name only).
    Otherwise, duplicated steps occur (without cleanup in step directory).

      Given a file named "features/problematic_stepfile_and_pass.feature" with:
        """
        Feature:
          Scenario:
            Given I use a weird step and pass
        """
      And a file named "features/steps/step_pass_<name>.py" with:
        """
        from behave import step

        @step(u'I use a weird step and pass')
        def step_weird_pass(context):
            pass
        """
      When I run "behave -f <format> features/problematic_stepfile_and_pass.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        """
      But note that "you should normally use only ASCII/latin-1 python filenames"

      Examples:
        | format | name |
        | plain  | Ärgernis_ist_überall |
        | pretty | Ärgernis_ist_überall |


  @problematic.step_filename
  Scenario Outline: Problematic step filename: <name> (case: fail, <format>)

    TEST-CONSTRAINT: Only one step file is used (= 1 name only).
    Otherwise, duplicated steps occur (without cleanup in step directory).

      Given a file named "features/problematic_stepfile_and_fail.feature" with:
        """
        Feature:
          Scenario:
            Given I use a weird step and fail
        """
      And a file named "features/steps/step_fail_<name>.py" with:
        """
        from behave import step

        @step(u'I use a weird step and fail')
        def step_weird_fails(context):
            assert False, "XFAIL-WEIRD"
        """
      When I run "behave -f <format> features/problematic_stepfile_and_fail.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        """
      But note that "you should normally use only ASCII/latin-1 python filenames"

      Examples:
        | format | name |
        | plain  | Ärgernis_ist_überall |
        | pretty | Ärgernis_ist_überall |


  @problematic.output
  Scenario Outline: Problematic output: <text> (case: pass, <format>)
      Given a file named "features/problematic_output_and_pass.feature" with:
        """
        Feature:
          Scenario:
            Given I write text "<text>" to stdout
            Then I write bytes "<text>" to stdout
            And a step passes
        """
      When I run "behave -f <format> --no-capture features/problematic_output_and_pass.feature"
      Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        1 scenario passed, 0 failed, 0 skipped
        """

      Examples:
        | format | text |
        | plain  | Café |
        | pretty | Ärgernis ist überall |


  @problematic.output
  Scenario Outline: Problematic output: <text> (case: fail, <format>)
      Given a file named "features/problematic_output_and_fail.feature" with:
        """
        Feature:
          Scenario:
            Given I write text "<text>" to stdout
            Then I write bytes "<text>" to stdout
            And a step fails
        """
      When I run "behave -f <format> features/problematic_output_and_fail.feature"
      Then it should fail with:
        """
        0 features passed, 1 failed, 0 skipped
        0 scenarios passed, 1 failed, 0 skipped
        """
      And the command output should contain:
        """
        <text>
        """

      Examples:
        | format | text |
        | plain  | Café |
        | pretty | Ärgernis ist überall |


  @problematic.tags
  Scenario Outline: Problematic tag: <tag> (case: pass, <format>)
      Given a file named "features/problematic_tag_and_pass.feature" with:
        """
        Feature:
          @<tag>
          Scenario:
            Given a step passes
        """
      When I run "behave -f <format> features/problematic_tag_and_pass.feature"
      Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        """

      Examples:
        | format | tag |
        | plain  | tag.Café |
        | pretty | tag.Ärgernis_ist_überall |


  @problematic.tags
  Scenario Outline: Problematic tag: <tag> (case: fail, <format>)
      Given a file named "features/problematic_tag_and_fail.feature" with:
        """
        Feature:
          @<tag>
          Scenario:
            Given a step fails
        """
      When I run "behave -f <format> features/problematic_tag_and_fail.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        """

      Examples:
        | format | tag |
        | plain  | tag.Café |
        | pretty | tag.Ärgernis_ist_überall |


  @issue_0230
  Scenario Outline: Step assert fails with problematic chars (case: <format>)

    NOTE: Python2 fails silently without showing the failed step.
    HINT: Use unicode string when you use, special non-ASCII characters.
    HINT: Use encoding-hint in python file header.

      Given a file named "features/steps/problematic_steps.py" with:
        """
        # -*- coding: UTF-8 -*-
        from behave import step

        @step(u'{word:w} step fails with assert and non-ASCII text')
        def step_fails_with_assert_and_problematic_text(context, word):
            assert False, u"XFAIL:¾;"
        """
      And a file named "features/assert_with_ptext.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When a step fails with assert and non-ASCII text
        """
      When I run "behave -f <format> features/assert_with_ptext.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        Assertion Failed: XFAIL:¾;
        """

      Examples:
        | format |
        | plain  |
        | pretty |

  @issue_0226
  Scenario Outline: Step raises exception with problematic chars (case: <format>)

      In Python2: When an exception is raised with unicode argument,
      (and special non-ASCII chars) the conversion of the exception into
      a unicode string causes implicit conversion into a normal string
      by using the default encoding (normally: ASCII).
      Therefore, the implicit encoding into a normal string often fails.

      SEE ALSO: http://bugs.python.org/issue2517
      NOTE: Better if encoding hint is provided in python file header.

      Given a file named "features/steps/problematic_steps.py" with:
        """
        # -*- coding: UTF-8 -*-
        from behave import step

        @step(u'{word:w} step fails with exception and non-ASCII text')
        def step_fails_with_exception_and_problematic_text(context, word):
            # -- REQUIRE: UNICODE STRING, when special, non-ASCII chars are used.
            raise RuntimeError(u"FAIL:¾;")
        """
      And a file named "features/exception_with_ptext.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            When a step fails with exception and non-ASCII text
        """
      When I run "behave -f <format> features/exception_with_ptext.feature"
      Then it should fail with:
        """
        0 scenarios passed, 1 failed, 0 skipped
        1 step passed, 1 failed, 0 skipped, 0 undefined
        """
      And the command output should contain:
        """
        RuntimeError: FAIL:¾;
        """

      Examples:
        | format |
        | plain  |
        | pretty |
