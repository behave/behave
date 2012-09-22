@issue
Feature: Issue #72: Using 'GHERKIN_COLORS' fails with Exception

    > Trying: GHERKIN_COLORS=executing=white behave
    > It fails:
    >
    >    Traceback (most recent call last):
    >      ...
    >      File "/.../behave/formatter/ansi_escapes.py", line 38, in <module>
    >        escapes[alias] = ''.join([colors[c] for c in aliases[alias].split(',')])
    >    TypeError: list indices must be integers, not str
    >
    > The reason is that the global variable colors is defined twice in this module.
    > The second variable overrides/modifies the first (without intention).


  Scenario: Using GHERKIN_COLORS in new working dir
    Given a new working directory
     And I set the environment variable "GHERKIN_COLORS" to "executing=white"
    When I run "behave"
    Then it should fail with:
      """
      No steps directory in "{__WORKDIR__}/features"
      """
     But the command output should not contain:
      """
      Traceback (most recent call last):
      """
     And the command output should not contain:
      """
      TypeError: list indices must be integers, not str
      """
