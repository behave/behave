# Analysis: cleanup_error on Context Bug

## Summary

This document analyzes the bug in `behave/runner.py` line 336 where `Context._pop()` uses `self.config` instead of `self._config` when capture_hooks is enabled.

## The Bug

**Location**: `behave/runner.py`, line 336

**Current (buggy) code:**
```python
if self.config.should_capture_hooks():
```

**Should be:**
```python
if self._config.should_capture_hooks():
```

## Why This is a Bug

The `Context` class has two ways to access the configuration:
1. **`self._config`**: Direct attribute access to the private `_config` attribute set in `__init__`
2. **`self.config`**: Stack lookup that searches through context stack frames via `__getattr__`

The bug occurs because:
- `self.config` relies on the `config` entry being present in the context stack
- In edge cases or if the stack is manipulated, `config` may not be accessible via stack lookup
- This causes an `AttributeError: 'Context' object has no attribute 'config'`
- Meanwhile, `self._config` would work correctly as a direct attribute

## When the Bug Manifests

The bug triggers when:
1. `capture_hooks` is enabled in the configuration
2. `Context._pop()` is called
3. The `config` entry is not accessible in the context stack (edge case)

## Test Coverage Analysis

### Why Existing Tests Don't Catch This Bug

The existing tests in `tests/unit/test_context_cleanups.py`:
- Create contexts with default configuration (capture_hooks disabled by default)
- Use `make_context()` helper which doesn't enable capture_hooks
- Never manipulate the context stack to remove the `config` entry

### New Test Added

Added `TestContextCleanupWithCapture` class with two tests:

1. **`test_context_pop_with_capture_hooks_enabled`**: Reproduces the bug by:
   - Enabling `capture_hooks` configuration
   - Removing `config` from the root stack frame
   - Calling `context._pop()` which triggers the bug

2. **`test_context_pop_with_capture_hooks_and_normal_config_access`**: Sanity check that:
   - Verifies capture_hooks works in normal circumstances
   - Ensures the normal code path is not broken

## Analysis of Similar Issues

Analyzed all `self.config` references in the Context class (lines 61-647):

| Line | Code | Status |
|------|------|--------|
| 158 | `self._config = runner.config` | ✅ Correct (initialization) |
| 162 | `"config": self._config,` | ✅ Correct (storing in root stack) |
| 336 | `if self.config.should_capture_hooks():` | ❌ **BUG** (should use `self._config`) |
| 340 | `with capture_output_to_sink(self._config,` | ✅ Correct (uses direct access) |
| 393 | `elif self._config.verbose:` | ✅ Correct (uses direct access) |

**Conclusion**: Only one occurrence of the bug in the Context class at line 336.

## Recommendations

1. **Fix the bug**: Change line 336 from `self.config` to `self._config`
2. **Keep the test**: Integrate `test_context_pop_with_capture_hooks_enabled` to prevent regression
3. **Code review pattern**: In Context class methods, prefer `self._config` over `self.config` for:
   - Better performance (avoids stack traversal)
   - More reliable access (not dependent on stack state)
   - Consistency with the rest of the code

## References

- PR #1297: Attempts to fix this bug
- Test file: `tests/unit/test_context_cleanups.py`
- Affected module: `behave/runner.py`
