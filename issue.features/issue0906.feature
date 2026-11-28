@issue
@formatter.json
Feature: Issue #906 -- context.attach() in after_scenario hook fails with JSON formatter

  . DESCRIPTION:
  .   Calling "context.attach()" in the "after_scenario" hook, for example to
  .   attach a screenshot of a failed scenario, fails with the JSON formatter:
  .
  .   * After the last step ran: "IndexError: list index out of range",
  .     so the scenario becomes a HOOK-ERROR and the attachment is lost.
  .   * After an earlier step failed: The attachment ends up at the next step,
  .     which was skipped.
  .
  . REASON:
  .   JSONFormatter.result() moves to the next step after each step result.
  .   An attachment made outside of a step pointed one step too far.
  .
  . FIX:
  .   An attachment that is made outside of a step belongs to the last step
  .   that ran.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/906

  Background:
    Given a new working directory
    And a file named "features/steps/use_behave4cmd_steps.py" with:
        """
        import behave4cmd0.passing_steps
        import behave4cmd0.failing_steps
        """
    And a file named "features/environment.py" with:
        """
        def after_scenario(context, scenario):
            context.attach("text/plain", b"after_scenario")
        """
    And a file named "features/example.feature" with:
        """
        Feature:
          Scenario: All steps pass
            Given a step passes
            Then another step passes

          Scenario: Last step fails
            Given a step passes
            Then a step fails

          Scenario: First step fails
            Given a step fails
            Then another step passes
        """

  Scenario: Attachment in after_scenario hook belongs to the last step that ran
    When I run "behave -f json.pretty features/example.feature"
    Then it should fail with:
        """
        1 scenario passed, 2 failed, 0 skipped
        3 steps passed, 2 failed, 1 skipped
        """
    And the command output should not contain "HOOK-ERROR"
    And the command output should not contain "IndexError"
    And the command output should contain:
        """
        "embeddings": [
          {
            "data": "YWZ0ZXJfc2NlbmFyaW8=",
            "mime_type": "text/plain"
          }
        ],
        "keyword": "Then",
        "location": "features/example.feature:4",
        """
    And the command output should contain:
        """
        "embeddings": [
          {
            "data": "YWZ0ZXJfc2NlbmFyaW8=",
            "mime_type": "text/plain"
          }
        ],
        "keyword": "Then",
        "location": "features/example.feature:8",
        """
    And the command output should contain:
        """
        "embeddings": [
          {
            "data": "YWZ0ZXJfc2NlbmFyaW8=",
            "mime_type": "text/plain"
          }
        ],
        "keyword": "Given",
        "location": "features/example.feature:11",
        """
    But the command output should contain "YWZ0ZXJfc2NlbmFyaW8=" 3 times
