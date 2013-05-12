@slow
Feature: Validate JSON Formatter Output

  To ensure that the JSON formatter generates valid JSON output
  As a tester
  I want that the JSON output is validated against its JSON schema.


  Scenario: Validate JSON output from features/ test run
    Given I use the current directory as working directory
    When I run "behave -f json -o testrun1.json features/"
    And  I run "bin/jsonschema_validate.py testrun1.json"
    Then it should pass with:
        """
        validate: testrun1.json ... OK
        """

  Scenario: Validate JSON output from issue.features/ test run
    Given I use the current directory as working directory
    When I run "behave -f json -o testrun2.json issue.features/"
    And  I run "bin/jsonschema_validate.py testrun2.json"
    Then it should pass with:
        """
        validate: testrun2.json ... OK
        """

  Scenario: Validate JSON output from tools/test-features/ test run
    Given I use the current directory as working directory
    When I run "behave -f json -o testrun3.json tools/test-features/"
    And  I run "bin/jsonschema_validate.py testrun3.json"
    Then it should pass with:
        """
        validate: testrun3.json ... OK
        """