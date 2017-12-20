@issue
Feature: Issue #197: Hooks processing should be more exception safe

  TESTS PROVIDED IN: features/runner.hook_errors.feature

  @reuse.colocated_test
  Scenario: Hook processing in case of errors
    Given I use the current directory as working directory
    When I run "behave -f plain features/runner.hook_errors.feature"
    Then it should pass

