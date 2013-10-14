@issue
Feature: Issue #75: behave @features_from_text_file does not work

   | Feature of Cucumber. Reading the source code, I see it partly implemented.
   |
   |   $ behave @list_of_features.txt
   |   https://github.com/jeamland/behave/blob/master/behave/runner.py#L416:L430
   |
   | However it fails because:
   |  * it does not remove the @ from the path
   |  * it does not search the steps/ directory in the parents of the feature files themselves


  @reuse.colocated_test
  Scenario: Use feature listfile
    Given I use the current directory as working directory
    When I run "behave -f plain features/runner.feature_listfile.feature"
    Then it should pass
