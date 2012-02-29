Feature: support scenario outlines

  Scenario Outline: run scenarios with one example table
    Given Some text <prefix>
     When we add some text <suffix>
     Then we should get the <combination>

     Examples: some simple examples
      | prefix  | suffix  | combination  |
      | go      | ogle    | google       |
      | onomat  | opoeia  | onomatopoeia | 
      | comb    | ination | combination  |

  Scenario Outline: run scenarios with examples
    Given Some text <prefix>
     When we add some text <suffix>
     Then we should get the <combination>

     Examples: some simple examples
      | prefix  | suffix  | combination  |
      | go      | ogle    | google       |
      | onomat  | opoeia  | onomatopoeia | 
      | comb    | ination | combination  |

     Examples: some other examples
      | prefix  | suffix | combination |
      | 1       | 2      | 12          |
      | one     | two    | onetwo      |

  @xfail
  Scenario Outline: scenarios that reference invalid subs
    Given Some text <prefix>
     When we add try to use a <broken> reference
     Then it won't work

     Examples: some simple examples
      | prefix  |
      | go      |

