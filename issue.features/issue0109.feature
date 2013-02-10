@issue
Feature: Issue #109: Insists that implemented tests are not implemented

    | STATUS: Resolved, not a behave problem.
    |
    | Following feature file marks implemented step "when I submit the following data"
    | as not implemented.


  Scenario:
    Given a new working directory
    And   a file named "features/syndrome109.feature" with:
        """
        @wip
        Feature: Manage accounts from the admin interface

            Scenario: Login successfully via login form
                Given I navigate to "/admin/"
                when I submit the following data
                    | name          | value         |
                    | username      | admin@foo.bar |
                    | password      | pass          |
                then I see the word "Welcome"

            Scenario: Create user via admin user creation form
                Given I navigate to "/admin/users/user/add/"
                when I submit the following data
                    | name           | value                           |
                    | email          | spaaaaaaaaaaaaaaaaaaam@ham.eggs |
                    | password1      | pass                            |
                    | password2      | pass                            |
                then I see the word "successfully"
        """
    And   a file named "features/steps/steps.py" with:
        """
        from behave import given, when, then

        @given(u'I navigate to "{url}"')
        def step_navigate_to_url(context, url):
            pass

        @when(u'I submit the following data')
        def step_submit_data(context):
            pass

        @then(u'I see the word "{word}"')
        def step_see_word(context, word):
            pass
        """
    When I run "behave -w features/syndrome109.feature"
    Then it should pass with:
        """
        1 feature passed, 0 failed, 0 skipped
        2 scenarios passed, 0 failed, 0 skipped
        6 steps passed, 0 failed, 0 skipped, 0 undefined
        """
    And the command output should not contain:
        """
        You can implement step definitions for undefined steps with these snippets:
        """
