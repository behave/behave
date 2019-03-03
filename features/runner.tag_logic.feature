Feature: Runner Tag logic

  As a tester
  I want to select scenarios using logical AND/OR of tags
  In order to conveniently run subsets of these scenarios

  . SPECIFICATION: Tag logic
  .   See "tag_expression.feature" description.
  .
  . RELATED:
  .  * tag_expression.feature

  Scenario: Select scenarios with 1 tag (@foo)
    Given a behave model with:
        | statement  | name | tags              | Comment |
        | Scenario   | S0   |                   | Untagged    |
        | Scenario   | S1   | @foo              | With 1 tag  |
        | Scenario   | S2   | @other            |             |
        | Scenario   | S3   | @foo @other       | With 2 tags |
    And note that "are all combinations of 0..2 tags"
    When I run the behave model with "tags"
    Then the following scenarios are selected with cmdline:
        | cmdline           | selected?      | Logic comment |
        |                   | S0, S1, S2, S3 | ALL, no selector |
        | --tags=@foo       | S1, S3         | @foo          |
        | --tags='not @foo' | S0, S2         | not @foo      |


  Scenario: Use other tag expression variants
    Given a behave model with:
        | statement  | name | tags              | Comment |
        | Scenario   | S0   |                   | Untagged    |
        | Scenario   | S1   | @foo              | With 1 tag  |
        | Scenario   | S2   | @other            |             |
        | Scenario   | S3   | @foo @other       | With 2 tags |
    Then the following scenarios are selected with cmdline:
        | cmdline           | selected?      | Logic comment |
        | --tags=foo        | S1, S3         | @foo,     without optional @  |
        | --tags='not foo'  | S0, S2         | not @foo, without optional @  |
        | --tags='not @foo' | S0, S2         | not @foo |
    And note that "these tag expression variants can also be used"


  Scenario: Select scenarios with 2 tags (@foo, @bar)
    Given a behave model with:
        | statement  | name | tags              | Comment |
        | Scenario   | S0   |                   | Untagged    |
        | Scenario   | S1   | @foo              | With a tag  |
        | Scenario   | S2   | @bar              |             |
        | Scenario   | S3   | @other            |             |
        | Scenario   | S4   | @foo @bar         | With 2 tags |
        | Scenario   | S5   | @foo @other       |             |
        | Scenario   | S6   | @bar @other       |             |
        | Scenario   | S7   | @foo @bar @other  | With 3 tags |
    And note that "are all combinations of 0..3 tags"
    When I run the behave model with "tags"
    Then the following scenarios are selected with cmdline:
        | cmdline                             | selected?                      | Logic comment |
        |                                     | S0, S1, S2, S3, S4, S5, S6, S7 | ALL, no selector      |
        | --tags="@foo or @bar"               | S1, S2, S4, S5, S6, S7         | @foo or @bar          |
        | --tags="@foo or not @bar"           | S0, S1, S3, S4, S5, S7         | @foo or not @bar      |
        | --tags="not @foo or not @bar"       | S0, S1, S2, S3, S5, S6         | not @foo or not @bar  |
        | --tags="@foo and @bar"              | S4, S7                         | @foo and @bar         |
        | --tags="@foo and not @bar"          | S1, S5                         | @foo and not @bar     |
        | --tags="not @foo and not @bar"      | S0, S3                         | not @foo and not @bar |
    But note that "the following tag-expressions check backward-compatible logic"
    And the following scenarios are selected with cmdline:
        | cmdline                             | selected?                      | Logic comment |
        | --tags=@foo  --tags=@bar            | S4, S7                         | @foo and @bar         |
        | --tags=@foo  --tags="not @bar"      | S1, S5                         | @foo and not @bar     |
        | --tags="not @foo" --tags="not @bar" | S0, S3                         | not @foo and not @bar |

