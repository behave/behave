Feature: Tag Expression v2 (cucumber-tag-expressions)

  As a tester
  I want to select a subset of all features/scenarios by using tags
  And I want to include and/or exclude some tags
  So that I can focus on the "important" scenarios (and features).

  . SPECIFICATION: cucumber-tag-expressions
  .   * cucumber-tag-expressions and very readable and similar to python boolean expressions.
  .   * a tag expression is a boolean expression
  .   * a tag expression supports the operators: and, or, not
  .   * a tag expression supports '(' and ')' for grouping expressions
  .
  . EXAMPLES:
  .   | Tag expression          | Comment |
  .   | @foo                    | Select elements with @foo tag      |
  .   |  foo                    | Same, '@' is optional.             |
  .   | not @foo                | Use "not" for negated logic.       |
  .   | @foo or @bar            | Use "or"  for either @foo or @bar. |
  .   | @foo and @bar           | Use "and" to require bot tags.     |
  .   | @foo or  not @bar       |                                    |
  .   | @foo and not @bar       |                                    |
  .   | (@foo or @bar) and @baz |                                    |


  Scenario: Select @foo
    Given the tag expression "@foo"
    Then the tag expression selects elements with tags:
        | tags         | selected? |
        |              |   no      |
        | @foo         |   yes     |
        | @other       |   no      |
        | @foo @other  |   yes     |


  Scenario: Tag expression with 0..1 tags
    Given the model elements with name and tags:
        | name | tags         | Comment |
        | S0   |              | Untagged    |
        | S1   | @foo         | With 1 tag  |
        | S2   | @other       |             |
        | S3   | @foo @other  | With 2 tags |
    And note that "are all combinations of 0..2 tags"
    Then the tag expression selects model elements with:
        | tag expression | selected?      | Case comment |
        |                | S0, S1, S2, S3 | Select all (empty tag expression) |
        |  @foo          | S1, S3         | Select @foo                       |
        |  not @foo      | S0, S2         | not @foo, selects untagged elements |
    But note that "tag expression variants are also supported"
    And the tag expression selects model elements with:
        | tag expression | selected?      | Case comment |
        |  foo           | S1, S3         |     @foo: '@' is optional     |
        | not foo        | S0, S2         | not @foo: '@' is optional     |
        | not @foo       | S0, S2         | not @foo: '~@' is supported   |


  Scenario: Tag expression with two tags (@foo, @bar)
    Given the model elements with name and tags:
        | name | tags             | Comment |
        | S0   |                  | Untagged    |
        | S1   | @foo             | With 1 tag  |
        | S2   | @bar             |             |
        | S3   | @other           |             |
        | S4   | @foo @bar        | With 2 tags |
        | S5   | @foo @other      |             |
        | S6   | @bar @other      |             |
        | S7   | @foo @bar @other | With 3 tags |
    And note that "are all combinations of 0..3 tags"
    Then the tag expression selects model elements with:
        | tag expression         | selected?                      | Case |
        |                        | S0, S1, S2, S3, S4, S5, S6, S7 | Select all            |
        |  @foo or @bar          | S1, S2, S4, S5, S6, S7         | @foo or @bar          |
        |  @foo or not @bar      | S0, S1, S3, S4, S5, S7         | @foo or not @bar      |
        |  not @foo or not @bar  | S0, S1, S2, S3, S5, S6         | not @foo or @not @bar |
        |  @foo  and @bar        | S4, S7                         | @foo and @bar         |
        |  @foo and     not @bar | S1, S5                         | @foo and not @bar     |
        |  not @foo and not @bar | S0, S3                         | not @foo and not @bar |


  Scenario: Tag expression with three tags (@foo, @bar, @zap)
    Given the model elements with name and tags:
        | name | tags                   | Comment |
        | S0   |                        | Untagged    |
        | S1   | @foo                   | With 1 tag  |
        | S2   | @bar                   |             |
        | S3   | @zap                   |             |
        | S4   | @other                 |             |
        | S5   | @foo @bar              | With 2 tags |
        | S6   | @foo @zap              |             |
        | S7   | @foo @other            |             |
        | S8   | @bar @zap              |             |
        | S9   | @bar @other            |             |
        | S10  | @zap @other            |             |
        | S11  | @foo @bar @zap         | With 3 tags |
        | S12  | @foo @bar @other       |             |
        | S13  | @foo @zap @other       |             |
        | S14  | @bar @zap @other       |             |
        | S15  | @foo @bar @zap @other  | With 4 tags |
    And note that "are all combinations of 0..4 tags"
    Then the tag expression selects model elements with:
        | tag expression                | selected?                   | Case |
        |  (@foo or @bar) and @zap      | S6, S8, S11, S13, S14, S15  | (@foo or @bar) and @zap |
        |  (@foo or @bar) and not @zap  | S1, S2, S5, S7, S9, S12     | (@foo or @bar) and not @zap |
        |  (@foo or not @bar) and @zap | S3, S6, S10, S11, S13, S15  | (@foo or not @bar) and @zap |
