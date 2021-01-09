@use.with_python_has_async_function=true
@use.with_python_has_asyncio.coroutine_decorator=true
Feature:
  Scenario:
    Given I dispatch an async-call with param "Alice"
    And   I dispatch an async-call with param "Bob"
    Then the collected result of the async-calls is "ALICE, BOB"
