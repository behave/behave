@issue
Feature: Issue #361 -- UTF-8 File with BOM

  . Using step files with "Byte-Order Mark" (BOM) prefix
  . causes weird problems.
  .
  . FIXES ALSO: #300
  . AFFECTED FILES:
  .   * features/environment.py
  .   * features/steps/*.py

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And a file named "features/steps/reuse_steps.py" with:
        """
        from behave4cmd0 import passing_steps
        """
    And a file named "features/passing.feature" with:
        """
        Feature:
          Scenario:
            Given a step passes
            Then a special step
        """

  @encoding.<encoding>
  @use.with_pypy=<with_pypy>
  Scenario Outline: Use step file with <case>
    Given a file named "features/steps/my_steps.py" and encoding="<encoding>" with:
        """
        # -*- coding: <encoding> -*-
        '''
        <text>.
        '''
        from behave import step

        @step(u'a special step')
        def step_impl(context):
            pass
        """
    When I run "behave -f plain features/passing.feature"
    Then it should pass with:
        """
        1 scenario passed, 0 failed, 0 skipped
        2 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should contain:
        """
        Feature:
          Scenario:
            Given a step passes ... passed
            Then a special step ... passed
        """
    And the command output should not contain:
        """
        SyntaxError: invalid character in identifier
        """

    Examples:
      | encoding   | text                 | with_pypy | case                    | Comment |
      | UTF-8-sig  | Ärgernis ist überall | false     | UTF-8 encoding and BOM  | Pypy 4.x has SyntaxError with BOM |
      | latin1     | Café                 | true      | Latin1 encoding         |                  |
      | iso-8859-1 | Ärgernis ist überall | true      | iso-8859-1 encoding     | Alias for latin1 |
      | cp1252     | Ärgernis ist überall | true      | cp1252 encoding         | Windows: Western Europe |
      | cp1251     | Привет! (=hello)     | true      | cp1251 encoding (Russia)| Windows: Russia  |
      | cp866      | Привет! (=hello)     | true      | cp688 encoding (Russia) | IBM866:  Russia  |
      | euc_jp     | こんにちは (=hello)   | true      | euc_jp encoding (Japan) | Japanese         |
      | gbk        | 您好 (=hello)        | true      | gbk encoding (China)    | Unified Chinese  |
      | gb2312     | 您好 (=hello)        | true      | gb2312 encoding (China) | Simplified Chinese |
