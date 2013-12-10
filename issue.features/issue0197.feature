@issue
Feature: Issue #197: Hooks processing should be more exception safe

  Background:
    Given a new working directory
    And a file named "features/steps/steps.py" with:
      """
      from behave import given, when, then

      @given(u'passing')
      def step(context):
          pass
      """
    And   a file named "features/passing.feature" with:
        """
        @tag
        Feature:
          Scenario:
            Given passing
        """

    Scenario: Exception in before_all
      Given a file named "features/environment.py" with:
          """
          def before_all(context):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Exception in before_all hook: FAIL

          ABORTED: By user.
          0 features passed, 0 failed, 0 skipped, 1 untested
          0 scenarios passed, 0 failed, 0 skipped, 1 untested
          0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
          """

    Scenario: Exception in before_feature
      Given a file named "features/environment.py" with:
          """
          def before_feature(context, feature):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Exception in before_feature hook: FAIL
          
            Scenario: 
              Given passing ... failed
          
          
          Failing scenarios:
            features/passing.feature:3  
          
          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in before_tag
      Given a file named "features/environment.py" with:
          """
          def before_tag(context, tag):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature -t tag"
      Then it should pass with
          """
          Feature: 
          Exception in before_tag hook: FAIL
          
            Scenario: 
              Given passing ... passed
          
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in before_scenario
      Given a file named "features/environment.py" with:
          """
          def before_scenario(context, scenario):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Feature: 
          
            Scenario: 
          Exception in before_scenario hook: FAIL
              Given passing ... failed
          
          
          Failing scenarios:
            features/passing.feature:3  
          
          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in before_step
      Given a file named "features/environment.py" with:
          """
          def before_step(context, step):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Feature: 
          
            Scenario: 
          Exception in before_step hook: FAIL
              Given passing ... failed
          
          
          Failing scenarios:
            features/passing.feature:3  
          
          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in after_step
      Given a file named "features/environment.py" with:
          """
          def after_step(context, step):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Feature: 
          
            Scenario: 
          Exception in after_step hook: FAIL
              Given passing ... failed
          
          
          Failing scenarios:
            features/passing.feature:3  
          
          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in after_scenario
      Given a file named "features/environment.py" with:
          """
          def after_scenario(context, scenario):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Feature: 
          
            Scenario: 
              Given passing ... passed
          Exception in after_scenario hook: FAIL
          
          
          Failing scenarios:
            features/passing.feature:3  
          
          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in after_tag
      Given a file named "features/environment.py" with:
          """
          def after_tag(context, tag):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature -t tag"
      Then it should pass with
          """
          Feature: 
          
            Scenario: 
              Given passing ... passed
          Exception in after_tag hook: FAIL
          
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in after_feature
      Given a file named "features/environment.py" with:
          """
          def after_feature(context, feature):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Feature: 
          
            Scenario: 
              Given passing ... passed
          Exception in after_feature hook: FAIL
          
          
          Failing scenarios:
            features/passing.feature:3  
          
          0 features passed, 1 failed, 0 skipped
          0 scenarios passed, 1 failed, 0 skipped
          0 steps passed, 1 failed, 0 skipped, 0 undefined
          """

    Scenario: Exception in after_all
      Given a file named "features/environment.py" with:
          """
          def after_all(context):
              raise RuntimeError("FAIL")
          """
      When I run "behave -f plain features/passing.feature"
      Then it should fail with
          """
          Feature: 
          
            Scenario: 
              Given passing ... passed
          
          Exception in after_all hook: FAIL
          1 feature passed, 0 failed, 0 skipped
          1 scenario passed, 0 failed, 0 skipped
          1 step passed, 0 failed, 0 skipped, 0 undefined
          """
