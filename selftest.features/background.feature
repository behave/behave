# -- BASED-ON: cucumber/features/background.feature
Feature: Background

  In order to provide a context to my scenarios within a feature
  As a feature editor
  I want to write a background section in my features.

  Background:
    Given a new working directory
    And   a file named "features/passing_background.feature" with:
        """
        Feature: Passing background sample

            Background:
                Given "10" cukes

            Scenario: passing background
                Then I should have "10" cukes

            Scenario: another passing background
                Then I should have "10" cukes
        """
    And a file named "features/scenario_outline_passing_background.feature" with:
      """
      Feature: Passing background with scenario outlines sample

        Background:
          Given "10" cukes

        Scenario Outline: passing background
          Then I should have "<count>" cukes
          Examples:
            |count|
            | 10  |

        Scenario Outline: another passing background
          Then I should have "<count>" cukes
          Examples:
            |count|
            | 10  |
      """
    And a file named "features/background_tagged_before_on_outline.feature" with:
      """
      @background_tagged_before_on_outline
      Feature: Background tagged Before on Outline

        Background:
          Given passing without a table

        Scenario Outline: passing background
          Then I should have "<count>" cukes

          Examples:
            | count |
            | 888   |
      """
    And a file named "features/multiline_args_background.feature" with:
      '''
      Feature: Passing background with multiline args

        Background:
          Given table
            |a|b|
            |c|d|
          And multiline string
            """
            I'm a cucumber and I'm okay.
            I sleep all night and I test all day
            """

        Scenario: passing background
          Then the table should be
            |a|b|
            |c|d|
          Then the multiline string should be
            """
            I'm a cucumber and I'm okay.
            I sleep all night and I test all day
            """

        Scenario: another passing background
          Then the table should be
            |a|b|
            |c|d|
          Then the multiline string should be
            """
            I'm a cucumber and I'm okay.
            I sleep all night and I test all day
            """
      '''
    And a file named "features/steps/steps.py" with:
        """#!python
        from behave import given, when, then, matchers
        from hamcrest import assert_that, equal_to

        # -- REGISTER USER-TYPE PARSER/CONVERTER:
        matchers.register_type(int=int)

        def flunker():
            raise Exception("FAIL")

        @given(u'"{amount:int}" cukes')
        def step(context, amount):
            if not hasattr(context, "cukes"):
                context.cukes = 0
            if context.cukes:
                raise Exception("We already have {0} cukes!".format(
                                context.cukes))
            context.cukes = amount

        #@given(u'"{amount:int}" global cukes')
        #def step(context, amount):
        #    context.scenario_runs = 0   # XXX
        #    if context.scenario_runs >= 1:
        #        flunker()
        #    context.cukes = amount
        #    context.scenario_runs += 1

        @given(u'passing without a table')
        def step(context):
            pass

        @given(u'failing without a table')
        def step(context):
            flunker()

        @then(u'I should have "{amount:int}" cukes')
        def step(context, amount):
            if not hasattr(context, "cukes"):
                context.cukes = 0
            assert_that(context.cukes, equal_to(amount))

        @then(u'I should have "{amount:int}" global cukes')
        def step(context, amount):
            assert_that(context.global_cukes, equal_to(amount))

        """

  @pass
  Scenario: run a feature with a background that passes
    When I run "behave -c -q features/passing_background.feature"
    Then it should pass with:
    """
    Feature: Passing background sample

      Background:

      Scenario: passing background
        Given "10" cukes
        Then I should have "10" cukes

      Scenario: another passing background
        Given "10" cukes
        Then I should have "10" cukes

    1 feature passed, 0 failed, 0 skipped
    2 scenarios passed, 0 failed, 0 skipped
    4 steps passed, 0 failed, 0 skipped, 0 undefined
    """

  Scenario: run a feature with scenario outlines that has a background that passes
    When I run "behave -c -q features/scenario_outline_passing_background.feature"
    Then it should pass with:
        """
        Feature: Passing background with scenario outlines sample
          Background:
          Scenario Outline: passing background
            Given "10" cukes
            Then I should have "10" cukes
          Scenario Outline: another passing background
            Given "10" cukes
            Then I should have "10" cukes
        1 feature passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        4 steps passed, 0 failed, 0 skipped, 0 undefined
        """

#  @xfail
#  Scenario: run a feature with scenario outlines that has a background that passes
#    When I run "behave -c -q features/background_tagged_before_on_outline.feature"
#    Then it should pass with:
#        """
#        @background_tagged_before_on_outline
#        Feature: Background tagged Before on Outline
#
#          Background:
#          Scenario Outline: passing background
#            Given passing without a table
#            Then I should have "888" cukes
#
#        1 feature passed, 0 failed, 0 skipped
#        1 scenarios passed, 0 failed, 0 skipped
#        2 steps passed, 0 failed, 0 skipped, 0 undefined
#        """
