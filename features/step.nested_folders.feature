Feature: Identically named folders and modules in nested directories are all discovered

Scenario: Steps are found even in identically-named folders, with differing or identical module names
    When a step is implemented in the root folder
    And a step is implemented in a sub folder
    And a step is implemented in a sub-sub folder
    And a step is implemented in another sub folder
    And a step is implemented in another sub-sub folder with an identical name
    And a step module with an identical name exists in the root folder
    And a step module with an identical name exists in a sub folder
    And a step module with an identical name exists in a sub-sub folder
    And a step is implemented in a sub-sub-sub folder with no module in the intermediate level
    And a step module with an identical name exists in the sub-folder two levels deeper
    Then the implementation from all nested step modules has been executed
