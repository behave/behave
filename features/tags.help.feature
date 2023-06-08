Feature: behave --tags-help option

  As a user
  I want to understand how to specify tag-expressions on command-line
  So that I can select some features, rules or scenarios, etc.

  . IN ADDITION:
  .  The --tags-help option helps to diagnose tag-expression v2 problems.

  Background:
    Given a new working directory

  Rule: Use --tags-help option to see tag-expression syntax and examples
    Scenario: Shows tag-expression description
      When I run "behave --tags-help"
      Then it should pass with:
        """
        TAG-EXPRESSIONS selects Features/Rules/Scenarios by using their tags.
        A TAG-EXPRESSION is a boolean expression that references some tags.

        EXAMPLES:

            --tags=@smoke
            --tags="not @xfail"
            --tags="@smoke or @wip"
            --tags="@smoke and @wip"
            --tags="(@slow and not @fixme) or @smoke"
            --tags="not (@fixme or @xfail)"

        NOTES:
        * The tag-prefix "@" is optional.
        * An empty tag-expression is "true" (select-anything).
        """

  Rule: Use --tags-help option to inspect current tag-expression
    Scenario: Shows current tag-expression without any tags
      When I run "behave --tags-help"
      Then it should pass with:
        """
        CURRENT TAG_EXPRESSION: true
        """
      And note that "an EMPTY tag-expression is always TRUE"

    Scenario: Shows current tag-expression with tags
      When I run "behave --tags-help --tags='@one and @two'"
      Then it should pass with:
        """
        CURRENT TAG_EXPRESSION: (one and two)
        """

    Scenario Outline: Shows more details of current tag-expression in verbose mode
      When I run "behave --tags-help --tags='<tags>' --verbose"
      Then it should pass with:
        """
        CURRENT TAG_EXPRESSION: <tag_expression>
          means: <tag_expression.logic>
        """
      But note that "the low-level tag-expression details are shown in verbose mode"

      Examples:
        | tags                    | tag_expression           | tag_expression.logic                           |
        | @one or @two and @three | (one or (two and three)) | Or(Tag('one'), And(Tag('two'), Tag('three')))  |
        | @one and @two or @three | ((one and two) or three) | Or(And(Tag('one'), Tag('two')), Tag('three'))  |

  Rule: Use --tags-help option with BAD TAG-EXPRESSION
    Scenario: Shows Tag-Expression Error for BAD TAG-EXPRESSION
      When I run "behave --tags-help --tags='not @one @two'"
      Then it should fail with:
        """
        TagExpressionError: Syntax error. Expected operator after one
        Expression: ( not one two )
        ______________________^ (HERE)
        """
      And note that "the error description indicates where the problem is"
      And note that "the correct tag-expression may be: not @one and @two"
      But the command output should not contain "Traceback"

