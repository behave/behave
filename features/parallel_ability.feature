Feature: Parallel options

    Scenario: Test parallel correctness 
        Given a new working directory
        And a file named "features/parallel_running_scenarios.feature" with:
          """
            Feature: parallelizable
                Background: I like to say bgstep
                    Given I decide to say bgstep1
                    Then I say bgstep2
                Scenario: I like to say
                    Given I decide to say 1
                    Then I say again 1
                Scenario: I like to yell
                    Given I decide to yell 2
                    Then I yell again 2
                Scenario Outline: Devide by VALUE outline
                    Given I decide to yell <value>
                    Then I will devide by <value>
                    Then I say again <value>

                    Examples: VTABLE
                    |value|
                    |3|
                    |2|
                    |1|
                    |0|
                    |-1|
          """
        And a file named "features/serialtag_override.feature" with:
          """
          @serial
          Feature: serialtag
              Scenario: I like to say
                  Given I decide to say 1
                  Then I say again 1
              Scenario: I like to yell
                  Given I decide to yell 2
                  Then I yell again 2
              Scenario Outline: I like to whisper outline
                  Given I decide to whisper <value>
                  Then I whisper again, but this time <value2>

                  Examples: VTABLE
                  |value|value2|
                  |1|7|
                  |2|3|
                  |3|1|
                  |4|9|
                  |5|8|
                  |6|4|
                  |7|5|
                  |8|4|
                  |9|5|

          """
        And a file named "features/steps/parallel_test_steps.py" with:
          """
          from behave import given,then
          import time,sys

          @given('I decide to say {msg}')
          def saystuff(context,msg):
              print "And I say,",msg

          @then('I say again {msg}')
          def sayagain(context,msg):
              print "Again I say",msg

          @then('I say {msg}')
          def say(context,msg):
              print "I say",msg

          @given('I decide to yell {msg}')
          def yell(context,msg):
              print "And I yell",msg

          @then('I yell again {msg}')
          def yellagain(context,msg):
              print "Again I yell",msg

          @given('I decide to whisper {msg}')
          def whisperstuff(context,msg):
              print "And I whisper",msg

          @then('I whisper again, but this time {msg}')
          def whisperagain(context,msg):
              print "Again I whisper,",msg

          @then('I will devide by {num}')
          def devide_by_num(context,num):
              print "About to devide by",num
              sys.stderr.write("I_wrote_this_to_stderr_"+str(num))
              print 1/int(num)

          @then('I sing to the stars {msg}')
          def starsong(context,msg):
              print "starsong: "+msg
          """

        When I run "behave --processes 8 --parallel-element scenario features/parallel_running_scenarios.feature"
        Then it should fail
        And the command output should contain:
          """
          7 scenario(s) and 0 feature(s) queued for consideration by 8 workers
          """
        And the command output should contain:
          """
          0 features passed, 1 features failed, 0 features skipped
          6 scenarios passed, 1 scenarios failed, 0 scenarios skipped
          31 steps passed, 1 steps failed, 1 steps skipped, 0 steps undefined
          """

    Scenario: Test parallel correctness with serial tag              
        When I run "behave --processes 8 --parallel-element scenario features/serialtag_override.feature"
        Then it should pass
        And the command output should contain:
          """
          0 scenario(s) and 1 feature(s) queued for consideration by 8 workers
          """
        And the command output should contain:
          """
          1 features passed, 0 features failed, 0 features skipped
          11 scenarios passed, 0 scenarios failed, 0 scenarios skipped
          22 steps passed, 0 steps failed, 0 steps skipped, 0 steps undefined
          """

    Scenario: Test parallel correctness with serial & parallel features              
        When I run "behave --processes 8 --parallel-element scenario"
        Then it should fail 
        And the command output should contain:
          """
          7 scenario(s) and 1 feature(s) queued for consideration by 8 workers
          """
        And the command output should contain:
          """
          1 features passed, 1 features failed, 0 features skipped
          17 scenarios passed, 1 scenarios failed, 0 scenarios skipped
          53 steps passed, 1 steps failed, 1 steps skipped, 0 steps undefined
          """

    Scenario: Test parallel correctness split at features              
        When I run "behave --processes 8 --parallel-element feature"
        Then it should fail 
        And the command output should contain:
          """
          0 scenario(s) and 2 feature(s) queued for consideration by 8 workers
          """
        And the command output should contain:
          """
          1 features passed, 1 features failed, 0 features skipped
          17 scenarios passed, 1 scenarios failed, 0 scenarios skipped
          53 steps passed, 1 steps failed, 1 steps skipped, 0 steps undefined
          """

