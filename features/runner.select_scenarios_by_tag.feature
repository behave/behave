@sequential
Feature: Select scenarios by using tags

    As a tester
    I want to select a subset of all scenarios by using tags
    (for selecting/including them or excluding them)
    So that I run only a subset of scenarios.

    . RELATED:
    .   * runner.tag_logic.feature


    @setup
    Scenario: Feature Setup
      Given a new working directory
      And a file named "behave.ini" with:
          """
          [behave]
          default_format = plain
          show_skipped = false
          show_timings = false
          """
      And a file named "features/steps/steps.py" with:
          """
          from behave import step

          @step('{word:w} step passes')
          def step_passes(context, word):
              pass
          """
      And a file named "features/alice.feature" with:
          """
          Feature: Alice
            @foo
            Scenario: Alice in Wonderland
              Given a step passes

            @foo @bar
            Scenario: Alice in Florida
              When hotter step passes

            @bar
            Scenario: Alice in Antarctica
              Then colder step passes
          """
      And a file named "features/bob.feature" with:
          """
          Feature: Bob
            @bar
            Scenario: Bob in Berlin
              Given beautiful step passes

            @foo
            Scenario: Bob in Florida
              When freaky step passes

            Scenario: Alice and Bob
              Then another step passes
          """


    Scenario: Select scenarios with tag=@foo (inclusive)

      TAG-LOGIC: @foo

      When I run "behave -f plain --tags=foo --no-skipped --no-timings features/"
      Then it should pass with:
          """
          2 features passed, 0 failed, 0 skipped
          3 scenarios passed, 0 failed, 3 skipped
          3 steps passed, 0 failed, 3 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: Alice in Wonderland
              Given a step passes ... passed

            Scenario: Alice in Florida
              When hotter step passes ... passed

          Feature: Bob
            Scenario: Bob in Florida
              When freaky step passes ... passed
          """

    Scenario: Select scenarios without tag=@foo (exclusive)

      TAG-LOGIC: not @foo

      Use  '-' (minus-sign) or '~' (tilde) in front of the tag-name
      to negate the tag-selection (excluding tags mode).

      When I run "behave --tags=~@foo features/"
      Then it should pass with:
          """
          2 features passed, 0 failed, 0 skipped
          3 scenarios passed, 0 failed, 3 skipped
          3 steps passed, 0 failed, 3 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: Alice in Antarctica
              Then colder step passes ... passed

          Feature: Bob
            Scenario: Bob in Berlin
              Given beautiful step passes ... passed

            Scenario: Alice and Bob
              Then another step passes ... passed
          """

    Scenario: Select scenarios with @foo and @bar tags (both)

      TAG-LOGIC: @foo and @bar

      When I run "behave --tags=@foo --tags=@bar features/"
      Then it should pass with:
          """
          1 feature passed, 0 failed, 1 skipped
          1 scenario passed, 0 failed, 5 skipped
          1 step passed, 0 failed, 5 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: Alice in Florida
              When hotter step passes
          """
      And note that "only scenario 'Alice in Florida' has both tags"


    Scenario: Select scenarios without @foo tag and without @bar tag

      TAG-LOGIC: not @foo and not @bar

      When I run "behave --tags=-@foo --tags=-@bar features/"
      Then it should pass with:
          """
          1 feature passed, 0 failed, 1 skipped
          1 scenario passed, 0 failed, 5 skipped
          1 step passed, 0 failed, 5 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Bob
            Scenario: Alice and Bob
              Then another step passes
          """
      And note that "only scenario 'Alice and Bob' has neither tag"


    Scenario: Select scenarios with @foo tag, but exclude with @bar tag

      TAG-LOGIC: @foo and not @bar

      When I run "behave --tags=@foo --tags=-@bar features/"
      Then it should pass with:
          """
          2 features passed, 0 failed, 0 skipped
          2 scenarios passed, 0 failed, 4 skipped
          2 steps passed, 0 failed, 4 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: Alice in Wonderland
              Given a step passes ... passed

          Feature: Bob
            Scenario: Bob in Florida
              When freaky step passes ... passed
          """
      But note that "'Alice in Florida' is excluded because it has also @bar"


    Scenario: Select scenarios with @bar tag, but exclude with @foo tag

      TAG-LOGIC: not @foo and @bar

      When I run "behave --tags=-@foo --tags=@bar features/"
      Then it should pass with:
          """
          2 features passed, 0 failed, 0 skipped
          2 scenarios passed, 0 failed, 4 skipped
          2 steps passed, 0 failed, 4 skipped, 0 undefined
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: Alice in Antarctica
              Then colder step passes ... passed

          Feature: Bob
            Scenario: Bob in Berlin
              Given beautiful step passes ... passed
          """
      But note that "'Alice in Florida' is excluded because it has also @bar"


    Scenario: Select scenarios with tag=@foo in dry-run mode (inclusive)

      Ensure that tag-selection works also in dry-run mode.

      When I run "behave --tags=@foo --dry-run features/"
      Then it should pass with:
          """
          0 features passed, 0 failed, 0 skipped, 2 untested
          0 scenarios passed, 0 failed, 3 skipped, 3 untested
          0 steps passed, 0 failed, 3 skipped, 0 undefined, 3 untested
          """
      And the command output should contain:
          """
          Feature: Alice
            Scenario: Alice in Wonderland
              Given a step passes ... untested
            Scenario: Alice in Florida
              When hotter step passes ... untested

          Feature: Bob
            Scenario: Bob in Florida
              When freaky step passes ... untested
          """
