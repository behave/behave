# Design: `--fail-focus` Parameter

## Overview

Add a `--fail-focus` CLI parameter to behave that focuses output on the first failing scenario only, suppressing passed scenarios, undefined step snippets, and other noise.

## Behavior

When `behave --fail-focus` is invoked:

1. **Auto-enable `--stop`** — stop execution on first failure
2. **Auto-enable `--no-snippets`** — suppress undefined step snippet suggestions
3. **Use `fail_focus` formatter** — replaces the default formatter to control output

## Formatter Output Rules

- **Passed scenarios**: completely silent
- **Undefined/skipped scenarios**: completely silent
- **Feature header**: deferred output — only printed when a scenario under that feature fails. Includes feature name + file path.
- **Failed scenario**: outputs:
  - Feature name and file path
  - Scenario name and line number
  - All steps with pass/fail status markers
  - Failed step's error message and traceback

## Output Example

```
Feature: User login -- features/login.feature

  Scenario: Login with wrong password  -- features/login.feature:15
    Given a registered user "alice"  ... passed
    When she logs in with password "wrong"  ... passed
    Then she should see an error message  ... failed
      Assertion Failed: Expected error message not found
      Traceback (most recent call last):
        File "features/steps/login_steps.py", line 42, in step_impl
          assert context.error_message is not None
      AssertionError
```

## Files to Modify

| File | Change |
|------|--------|
| `behave/formatter/fail_focus.py` | **New** — FailFocusFormatter class |
| `behave/formatter/_registry.py` | Register `fail_focus` formatter |
| `behave/configuration.py` | Add `--fail-focus` argument definition |
| `behave/runner.py` | Handle `--fail-focus` logic (set stop, no-snippets, override formatter) |

## FailFocusFormatter Design

- Extends `Formatter` base class from `behave/formatter/base.py`
- Tracks current feature (deferred output)
- On `scenario()`: stores current scenario
- On `result()`: tracks step results for current scenario
- On scenario end: if scenario failed, flush feature header (if not yet printed) + scenario + steps with error details
- On scenario end: if scenario passed/undefined/skipped, discard buffered output

## Compatibility

- Works with `--tags`, `--include`, `--exclude` and other filtering parameters
- If `--format` is also specified, `--fail-focus` formatter takes precedence (with a warning)
- Does not affect JUnit XML or other file-based reporters
