@issue
@use.with_python.min_version=3.7
Feature: Issue #1180 -- Negative Time Problem with Summary Reporter

  . DESCRIPTION OF SYNDROME (OBSERVED BEHAVIOR):
  .   When I use "freezegun.freeze_time()" in one of my steps
  .   Then the summary report may show negative duration for the test-run duration.
  .
  . ANALYSIS OF THE PROBLEM (and solution):
  .   Freezegun must be configured to ignore one/some behave module(s).
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1180
  .   * https://github.com/spulec/freezegun


  Background: Setup
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
      """
      from __future__ import absolute_import
      import behave4cmd0.passing_steps
      """
    And a file named "features/steps/freeze_time_steps.py" with:
      """
      from __future__ import absolute_import
      import datetime
      import os
      from behave import given, when, then
      from freezegun import freeze_time
      import freezegun
      from assertpy import assert_that

      FREEZEGUN_IGNORE_BEHAVE = os.environ.get("FREEZEGUN_IGNORE_BEHAVE", "no") == "yes"
      if FREEZEGUN_IGNORE_BEHAVE:
          print("FREEZEGUN: Ignore behave modules ...")
          freezegun.configure(extend_ignore_list=["behave.model"])

      @given(u'current time is fixed at "{isotime:ti}"')
      @when(u'current time is fixed at "{isotime:ti}"')
      def step_current_time(ctx, isotime):
          time_patcher = freeze_time(isotime, real_asyncio=True)
          time_patcher.start()

          def restore_time():
              print("FREEZEGUN: Restore time")
              time_patcher.stop()
          ctx.add_cleanup(restore_time)

      @then(u'today is "{today:ti}"')
      def step_then_today_is(ctx, today):
          now = datetime.datetime.now()
          assert_that(today).is_equal_to(now)
      """
    And a file named "features/syndrome_1180.feature" with:
      """
      Feature: Check syndrome with freezegun

        Scenario: T1
          Given current time is fixed at "2001-09-11"
          Then today is "2001-09-11"

        Scenario: T2
          Given current time is fixed at "1980-01-01"
          Then today is "1980-01-01"
      """


  @syndrome
  @xfail.without.freezegun.ignore_behave_module
  Scenario: Use freezegun.freeze_time to check syndrome (proof-of-concept)
    Given I set the environment variable "FREEZEGUN_IGNORE_BEHAVE" to "no"
    When I run `behave -f plain features/syndrome_1180.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped
      """
    But the command output should match /Took -\d+min \d+\.\d+s/
    And note that "Test run duration is negative"

  @syndrome.fixed
  Scenario: Use freezegun.freeze_time to check syndrome (case: FIXED)
    Given I set the environment variable "FREEZEGUN_IGNORE_BEHAVE" to "yes"
    When I run `behave -f plain features/syndrome_1180.feature`
    Then it should pass with:
      """
      2 scenarios passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped
      """
    And the command output should match /Took \d+min \d+\.\d+s/
    But the command output should not match /Took -\d+min \d+\.\d+s/
    And note that "Test run duration is positive"

