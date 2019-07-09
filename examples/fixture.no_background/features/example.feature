Feature: Disable the Background Inheritance Mechanism in some Scenarios

  . BEWARE:
  .   This is only an example how this can be done (PROOF-OF-CONCEPT).
  .   This is not an example that you should do this !!!

    Background:
      Given a background step passes

    Scenario: Alice
      When a step passes
      And note that "BACKGROUND STEPS are executed here"

    @fixture.behave.no_background
    Scenario: Bob
      Given I need another scenario setup
      When another step passes
      And note that "NO-BACKGROUND STEPS are executed here"
