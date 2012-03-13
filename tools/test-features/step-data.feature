Feature: steps may have associated data

  Scenario: step with text
    Given some body of text
        """
           Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
        enim ad minim veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat.
        """
     Then the text is as expected

  Scenario: step with a table
    Given some initial data
        | name      | department  |
        | Barry     | Beer Cans   |
        | Pudey     | Silly Walks |
        | Two-Lumps | Silly Walks | 
     Then we will have the expected data

  @xfail
  Scenario: step with text that fails
    Given some body of text
        """
           Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
        enim ad minim VENIAM, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat.
        """
     Then the text is as expected

  Scenario Outline: step with text and subtitution
    Given some body of text
        """
           Lorem <ipsum> dolor sit amet, consectetur adipisicing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
        enim ad minim veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat.
        """
     Then the text is substituted as expected

    Examples:
        | ipsum |
        | spam  |
        | ham   |


  Scenario Outline: step with a table and substution
    Given some initial data
        | name      | department  |
        | Barry     | <spam> Cans |
        | Pudey     | Silly Walks |
        | Two-Lumps | Silly Walks | 
     Then we will have the substituted data

    Examples:
        | spam |
        | spam |
        | ham  |

