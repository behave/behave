@issue
Feature: Issue #300 -- UnicodeDecodeError when read steps.py

  . My system is running on Chinese GBK character set.
  . But you know we make our files as utf-8 format generally, and so do I.
  . I set my step file api1_steps.py as utf-8, and entered some Chinese characters in.
  . I run "behave", but I got UnicodeDecodeError, just like this:
  .
  .   File "D:\workspace\env_110\lib\site-packages\behave\runner.py", line 304, in exec_file
  .     code = compile(f.read(), filename2, 'exec')
  .   UnicodeDecodeError: 'gbk' codec can't decode byte 0xad in position 510: illegal multibyte sequence

  | OPEN ISSUES:
  |   * Acceptable/supported Python source file encodings
  |   * config: Add encoding option for feature files, step files or both.

    Scenario: Cause BAD-ASCII Syndrome in steps file
        Given a new working directory
        And a file named "features/steps/bad_ascii_steps.py" with:
            """
            '''
            BAD ASCII CASES (requires UTF-8/latin1 support):
             * Café
             * Ärgernis ist überall
            '''
            # COMMENT: Ärgernis ist überall
            """
        And a file named "features/steps/steps.py" with:
            """
            from __future__ import unicode_literals
            from behave import step

            @step('{word:w} step passes')
            def step_passes(context, word):
                pass
            """
        And a file named "features/e1.feature" with:
            """
            Feature:
              Scenario: Alice
                Given a step passes
                Then another step passes
            """
        When I run "behave -f plain features/e1.feature"
        Then it should pass with:
            """
            1 scenario passed, 0 failed, 0 skipped
            2 steps passed, 0 failed, 0 skipped, 0 undefined
            """
