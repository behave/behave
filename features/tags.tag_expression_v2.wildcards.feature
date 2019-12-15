Feature: Tag Expression v2 Extension: Wildcards for tag matching

  As a tester
  I want to use a wildcard pattern to select tags following a naming scheme
  So that it is simpler to select a subset of scenarios and features.

  . SPECIFICATION: Wildcards in tag-expressions v2
  .   * Use file-name matching wildcards (fnmatch): *, ?
  .   * a tag expression is a boolean expression
  .   * a tag expression supports the operators: and, or, not
  .   * a tag expression supports '(' and ')' for grouping expressions
  .
  . EXAMPLES:
  .   | Tag expression          | Comment |
  .   | @foo.*                  | Matches any tags that start with "@foo." |
  .   | not @foo.*              | Excludes any element that have tags that start with "@foo." |


  Scenario: Select tags that match the "@foo.*" pattern
    Given the tag expression "@foo.*"
    Then the tag expression selects elements with tags:
        | tags          | selected? |
        |               |   no      |
        | @foo          |   no      |
        | @foo.one      |   yes     |
        | @foo.two      |   yes     |
        | @other        |   no      |
        | @foo.3 @other |   yes     |

  Scenario: Select tags that do not match the "@foo.*" pattern
    Given the tag expression "not @foo.*"
    Then the tag expression selects elements with tags:
        | tags          | selected? |
        |               |   yes     |
        | @foo          |   yes     |
        | @foo.one      |   no      |
        | @foo.two      |   no      |
        | @other        |   yes     |
        | @foo.3 @other |   no      |
