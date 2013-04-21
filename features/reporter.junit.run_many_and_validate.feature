@slow
@requires_tool.paver
@requires_tool.xmllint
Feature: Run many feature files with JUnitReporter and validate Output

    I want that the JUnitReporter covers many cases
    And its generated xUnit XML files should be valid
    And conform to its DTD/XML schema.

  @wip
  @xfail
  Scenario: Run Reporter with many passing features
    Given I use the current directory as working directory
    And  I remove the directory "reports"
    When I run "behave --junit issue.features/"
    Then it should pass
    When I run "paver junit_validate reports"
    Then it should pass

  Scenario: Run Reporter with failing scenario
    Given I use the current directory as working directory
    And  I remove the directory "reports"
    When I run "behave -f progress --junit --tags=@xfail tools/test-features/step-data.feature"
    Then it should fail with:
      """
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 6 skipped
      1 step passed, 1 failed, 12 skipped, 0 undefined
      """
    When I run "paver junit_validate reports"
    Then it should pass

  @wip
  @xfail
  Scenario: Run Reporter with many passing and some failing features
    Given I use the current directory as working directory
    And  I remove the directory "reports"
    When I run "behave --junit -f progress tools/test-features/"
    Then it should fail with:
      """
      XXX french.feature
      """
    When I run "paver junit_validate reports/"
    Then it should pass
