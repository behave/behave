Feature: parse stuff out of steps

  Scenario: basic parsing
     Given a string with an argument
      Then we get "with" parsed

  Scenario: custom type parsing
     Given a string with a custom type
      Then we get "WITH" parsed

