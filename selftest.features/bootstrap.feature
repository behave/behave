# -- BASED-ON: cucumber/features/bootstrap.feature
# DEVIATES-FROM: cucumber => behave complains about steps dir, not features dir.
Feature: Bootstrapping a new project

  In order to have the best chances of getting up and running with behave
  As a new behave user
  I want behave to give helpful error messages in basic situations

  Scenario: Running behave against a non-existing feature file

    Given a new working directory
    When I run "behave"
    Then it should fail with:
      """
      No steps directory in "{__WORKDIR__}/features"
      """

  Scenario: Running behave with steps directory but without feature files

    Given a new working directory
    And   a file named "features/steps/steps.py" with:
        """#!python
        from behave import given, when, then

        @given(u'passing')
        def step(context):
            pass
        """
    When I run "behave"
    Then it should fail with:
      """
      No feature files in "{__WORKDIR__}/features"
      """

  Scenario: Running behave with feature files but without steps directory

    Given a new working directory
    And   a file named "features/simplistic.feature" with:
        """
        Feature: Simplistic
        """
    When I run "behave"
    Then it should fail with:
      """
      No steps directory in "{__WORKDIR__}/features"
      """

  Scenario: Running behave with feature files but without steps

    Given a new working directory
    And   a file named "features/simplistic2.feature" with:
        """
        Feature: Simplistic2
          Scenario: One
            Given I have an unknown step
        """
    And   a file named "features/steps/no_steps.py" with:
        """#!python
        from behave import given, when, then
        """
    When I run "behave -c -f plain"
    Then it should fail with:
      """
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      0 steps passed, 0 failed, 0 skipped, 1 undefined
      """
    And the command output should contain:
      """
      Feature: Simplistic2
         Scenario: One
             Given I have an unknown step ... undefined
      """
