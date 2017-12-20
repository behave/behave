@issue
@unicode
@not_reproducible
Feature: Issue #487 -- UnicodeEncodeError with ZBSP in multi-line text

    . NOTE: I use ZBSP (zero-width space) in multiline text
    . Traceback (most recent call last):
    .  File "/usr/bin/behave-2", line 9, in <module>
    .    load_entry_point('behave==1.2.5', 'console_scripts', 'behave')()
    .  File "/usr/lib/python2.7/site-packages/behave/__main__.py", line 111, in main
    .     print(u"ParseError: %s" % e)
    . UnicodeEncodeError: 'ascii' codec can't encode characters in position 92-103: ordinal not in range(128)
    .
    . ANALYSIS:
    .   ParseError indicates that the problem occured while parsing the
    .   feature file. Feature file encoding is assumed

    @not.with_ci=appveyor
    Scenario:
      Given a new working directory
      And a file named "features/steps/pass_steps.py" with:
        """
        from behave import step

        @step('{word:w} step passes')
        def step_passes(context, word):
            pass
        """
      And a file named "features/steps/steps.py" with:
        """
        # -*- coding: latin-1 -*-
        from __future__ import print_function
        from behave import step

        @step('I use {special_unicode_char:w} in text')
        def step_use_ZBSP_with_text(context, special_unicode_char):
            assert context.text
            print(u"TEXT: %s" % context.text)
        """
      And a file named "behave.ini" with:
          """
          [behave]
          show_timings = false
          """
      And a file named "features/syndrome.feature" with:
        """
        Feature:

          Scenario Outline: Use special unicode char (<comment>)
            Given I use ZBSP in text:
              '''
              HERE we use a ==><special_unicode_char><== SPECIAL UNICODE CHAR.
              '''

           Examples:
              | special_unicode_char | comment |
              | ⌘                    | MACOS command key symbol |
              | ©                    | copyright sign           |
              | €                    | Euro sign (currency)     |
              | xxx XXX              | special space            |
        """
      When I run "behave -f plain features/syndrome.feature"
      Then it should pass with:
        """
        4 scenarios passed, 0 failed, 0 skipped
        """
      And the command output should contain:
        '''
        Scenario Outline: Use special unicode char (MACOS command key symbol) -- @1.1
          Given I use ZBSP in text ... passed
            """
            HERE we use a ==>⌘<== SPECIAL UNICODE CHAR.
            """

        Scenario Outline: Use special unicode char (copyright sign) -- @1.2
          Given I use ZBSP in text ... passed
            """
            HERE we use a ==>©<== SPECIAL UNICODE CHAR.
            """

        Scenario Outline: Use special unicode char (Euro sign (currency)) -- @1.3
          Given I use ZBSP in text ... passed
            """
            HERE we use a ==>€<== SPECIAL UNICODE CHAR.
            """

        Scenario Outline: Use special unicode char (special space) -- @1.4
          Given I use ZBSP in text ... passed
            """
            HERE we use a ==>xxx XXX<== SPECIAL UNICODE CHAR.
            """
        '''
