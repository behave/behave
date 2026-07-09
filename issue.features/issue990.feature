@issue
Feature: Issue #990 -- os.path.relpath may fail on Windows with cross-drive paths

  . DESCRIPTION:
  .   On Windows, os.path.relpath() raises ValueError when the filename
  .   and the base directory are on different drives (e.g. C: and D:).
  .   Most call sites in behave already handle this via make_relpath_if_possible,
  .   but the sphinx_steps formatter had an unprotected os.path.relpath() call.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/990

  Scenario: sphinx_steps formatter handles cross-drive paths on Windows
    Given a new working directory
    And a file named "features/steps/use_steplib_behave4cmd.py" with:
      """
      import behave4cmd0.passing_steps
      """
    And a file named "features/issue990.feature" with:
      """
      Feature: Issue 990
        Scenario: S1
          Given a step passes
      """
    When I run "behave --format=sphinx.steps features/issue990.feature"
    Then it should pass with:
      """
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped
      """
