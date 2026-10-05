# `--fail-focus` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `--fail-focus` CLI parameter that stops on first failure and only outputs the failing scenario with its Feature header, steps, and traceback — suppressing passed/undefined/skipped scenarios.

**Architecture:** New `FailFocusFormatter` registered as `fail_focus` in the formatter registry. The `--fail-focus` flag in `Configuration` triggers `setup_fail_focus_mode()` which sets `stop=True`, `show_snippets=False`, and overrides the default formatter to `fail_focus`. The formatter buffers feature/scenario/step data and only flushes output when a scenario fails.

**Tech Stack:** Python, behave formatter API (`behave.formatter.base.Formatter`)

---

### Task 1: Create FailFocusFormatter

**Files:**
- Create: `behave/formatter/fail_focus.py`
- Test: `tests/unit/test_formatter_fail_focus.py`

- [ ] **Step 1: Write the failing test for FailFocusFormatter — passed scenario is silent**

```python
# tests/unit/test_formatter_fail_focus.py
import io
import unittest
from unittest.mock import Mock
from behave.formatter.base import StreamOpener
from behave.model import Feature, Scenario, Step
from behave.model_type import Status


def make_config(**kwargs):
    config = Mock()
    config.show_timings = kwargs.get("show_timings", False)
    config.show_multiline = kwargs.get("show_multiline", True)
    config.show_source = kwargs.get("show_source", False)
    config.color = "off"
    return config


def make_stream_opener():
    stream = io.StringIO()
    return StreamOpener(stream=stream), stream


class TestFailFocusFormatter(unittest.TestCase):
    def _make_formatter(self, **config_kwargs):
        from behave.formatter.fail_focus import FailFocusFormatter
        stream_opener, stream = make_stream_opener()
        config = make_config(**config_kwargs)
        formatter = FailFocusFormatter(stream_opener, config)
        return formatter, stream

    def _make_feature(self, name="Test Feature", filename="features/test.feature"):
        feature = Mock()
        feature.keyword = "Feature"
        feature.name = name
        feature.filename = filename
        feature.tags = []
        feature.location = Mock()
        feature.location.filename = filename
        feature.location.line = 1
        return feature

    def _make_scenario(self, name="Test Scenario", filename="features/test.feature", line=5):
        scenario = Mock()
        scenario.keyword = "Scenario"
        scenario.name = name
        scenario.filename = filename
        scenario.tags = []
        scenario.location = Mock()
        scenario.location.filename = filename
        scenario.location.line = line
        return scenario

    def _make_step(self, keyword="Given", name="a step", status=Status.passed,
                   error_message=None, duration=0):
        step = Mock()
        step.keyword = keyword
        step.name = name
        step.status = status
        step.error_message = error_message
        step.duration = duration
        step.text = None
        step.table = None
        return step

    def test_passed_scenario_produces_no_output(self):
        formatter, stream = self._make_formatter()
        feature = self._make_feature()
        scenario = self._make_scenario()
        step = self._make_step(status=Status.passed)

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step)
        formatter.result(step)
        formatter.eof()
        formatter.close()

        self.assertEqual(stream.getvalue(), "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'behave.formatter.fail_focus'`

- [ ] **Step 3: Write FailFocusFormatter — minimal implementation for passed scenario silence**

```python
# behave/formatter/fail_focus.py
"""
Formatter that only outputs the first failing scenario.
Used with --fail-focus mode.
"""

from behave.formatter.base import Formatter
from behave.model_type import Status


class FailFocusFormatter(Formatter):
    name = "fail_focus"
    description = "Only shows the first failing scenario with error details."

    def __init__(self, stream_opener, config):
        super(FailFocusFormatter, self).__init__(stream_opener, config)
        self.current_feature = None
        self.current_scenario = None
        self.current_steps = []
        self.feature_printed = False
        self.stream = self.open()

    def feature(self, feature):
        self.current_feature = feature
        self.feature_printed = False

    def scenario(self, scenario):
        self.current_scenario = scenario
        self.current_steps = []

    def step(self, step):
        self.current_steps.append(step)

    def result(self, step):
        # Update stored step with result
        for i, s in enumerate(self.current_steps):
            if s is step:
                self.current_steps[i] = step
                break

        if step.status in (Status.failed, Status.error):
            self._print_failure()

    def _print_failure(self):
        if not self.feature_printed and self.current_feature:
            self.stream.write("Feature: %s -- %s\n" % (
                self.current_feature.name,
                self.current_feature.filename
            ))
            self.feature_printed = True

        if self.current_scenario:
            self.stream.write("\n  Scenario: %s  -- %s:%s\n" % (
                self.current_scenario.name,
                self.current_scenario.location.filename,
                self.current_scenario.location.line
            ))

        for s in self.current_steps:
            status_text = s.status.name
            self.stream.write("    %s %s ... %s\n" % (
                s.keyword, s.name, status_text
            ))
            if s.error_message:
                self.stream.write("%s\n" % s.error_message)

        self.stream.flush()

    def eof(self):
        pass

    def close(self):
        self.close_stream()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py::TestFailFocusFormatter::test_passed_scenario_produces_no_output -v`
Expected: PASS

- [ ] **Step 5: Write test for failed scenario output**

Add to `tests/unit/test_formatter_fail_focus.py`:

```python
    def test_failed_scenario_outputs_feature_and_scenario_with_error(self):
        formatter, stream = self._make_formatter()
        feature = self._make_feature(name="User login", filename="features/login.feature")
        scenario = self._make_scenario(name="Login with wrong password",
                                       filename="features/login.feature", line=15)
        step1 = self._make_step(keyword="Given", name='a registered user "alice"',
                                status=Status.passed)
        step2 = self._make_step(keyword="Then", name="she should see an error",
                                status=Status.failed,
                                error_message="Assertion Failed: Expected error message")

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.step(step2)
        formatter.result(step1)
        formatter.result(step2)
        formatter.eof()
        formatter.close()

        output = stream.getvalue()
        self.assertIn("Feature: User login -- features/login.feature", output)
        self.assertIn("Scenario: Login with wrong password", output)
        self.assertIn("features/login.feature:15", output)
        self.assertIn("Given a registered user", output)
        self.assertIn("... passed", output)
        self.assertIn("... failed", output)
        self.assertIn("Assertion Failed", output)

    def test_undefined_scenario_produces_no_output(self):
        formatter, stream = self._make_formatter()
        feature = self._make_feature()
        scenario = self._make_scenario()
        step = self._make_step(status=Status.undefined)

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step)
        formatter.result(step)
        formatter.eof()
        formatter.close()

        self.assertEqual(stream.getvalue(), "")

    def test_skipped_scenario_produces_no_output(self):
        formatter, stream = self._make_formatter()
        feature = self._make_feature()
        scenario = self._make_scenario()
        step = self._make_step(status=Status.skipped)

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step)
        formatter.result(step)
        formatter.eof()
        formatter.close()

        self.assertEqual(stream.getvalue(), "")
```

- [ ] **Step 6: Run all tests to verify they pass**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py -v`
Expected: All 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add behave/formatter/fail_focus.py tests/unit/test_formatter_fail_focus.py
git commit -m "feat: add FailFocusFormatter for --fail-focus mode"
```

---

### Task 2: Register fail_focus formatter

**Files:**
- Modify: `behave/formatter/_builtins.py:12-34`

- [ ] **Step 1: Write a test that the formatter is registered**

Add to `tests/unit/test_formatter_fail_focus.py`:

```python
class TestFailFocusFormatterRegistration(unittest.TestCase):
    def test_fail_focus_formatter_is_registered(self):
        from behave.formatter._registry import is_formatter_valid
        from behave.formatter._builtins import setup_formatters
        setup_formatters()
        self.assertTrue(is_formatter_valid("fail_focus"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py::TestFailFocusFormatterRegistration -v`
Expected: FAIL — `fail_focus` not found in registry

- [ ] **Step 3: Add fail_focus to _builtins.py**

In `behave/formatter/_builtins.py`, add to `_BUILTIN_FORMATS` list (after the `"captured"` entry):

```python
    ("fail_focus", "behave.formatter.fail_focus:FailFocusFormatter"),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py::TestFailFocusFormatterRegistration -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add behave/formatter/_builtins.py tests/unit/test_formatter_fail_focus.py
git commit -m "feat: register fail_focus formatter in builtins"
```

---

### Task 3: Add --fail-focus CLI parameter and setup_fail_focus_mode

**Files:**
- Modify: `behave/configuration.py:407-431` (OPTIONS list, add after `--wip`)
- Modify: `behave/configuration.py:826-827` (add setup call after wip setup)
- Modify: `behave/configuration.py:874` (init method, add `fail_focus = None`)
- Modify: `behave/configuration.py:950-969` (add `setup_fail_focus_mode` method after `setup_wip_mode`)

- [ ] **Step 1: Write a test for Configuration with --fail-focus**

Add to `tests/unit/test_formatter_fail_focus.py`:

```python
class TestFailFocusConfiguration(unittest.TestCase):
    def test_fail_focus_sets_stop_and_no_snippets(self):
        from behave.configuration import Configuration
        config = Configuration(command_args=["--fail-focus", "features/"],
                               load_config=False)
        self.assertTrue(config.stop)
        self.assertFalse(config.show_snippets)

    def test_fail_focus_sets_formatter_to_fail_focus(self):
        from behave.configuration import Configuration
        config = Configuration(command_args=["--fail-focus", "features/"],
                               load_config=False)
        self.assertIn("fail_focus", config.format)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py::TestFailFocusConfiguration -v`
Expected: FAIL — `--fail-focus` not recognized

- [ ] **Step 3: Add --fail-focus option to OPTIONS list**

In `behave/configuration.py`, add after the `--wip` option block (after line 411):

```python
    (("--fail-focus",),
     dict(action="store_true",
          help="""Focus on the first failure only. Additionally: use the
                  "fail_focus" formatter, stop at the first failure,
                  and do not show snippets for undefined steps.""")),
```

- [ ] **Step 4: Add fail_focus to init() method**

In `behave/configuration.py`, in the `init()` method, add after `self.wip = None` (line 874):

```python
        self.fail_focus = None
```

- [ ] **Step 5: Add setup_fail_focus_mode() method**

In `behave/configuration.py`, add after `setup_wip_mode()` method (after line 969):

```python
    def setup_fail_focus_mode(self):
        # Focus on first failure only.
        # Additionally:
        #  * use the "fail_focus" formatter (per default)
        #  * stop at the first failure
        #  * do not show snippets for undefined steps
        self.default_format = "fail_focus"
        self.stop = True
        self.show_snippets = False
```

- [ ] **Step 6: Call setup_fail_focus_mode() in __init__**

In `behave/configuration.py`, add after `if self.wip: self.setup_wip_mode()` (after line 827):

```python
        if self.fail_focus:
            self.setup_fail_focus_mode()
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py::TestFailFocusConfiguration -v`
Expected: PASS

- [ ] **Step 8: Run all fail_focus tests**

Run: `python -m pytest tests/unit/test_formatter_fail_focus.py -v`
Expected: All tests PASS

- [ ] **Step 9: Commit**

```bash
git add behave/configuration.py tests/unit/test_formatter_fail_focus.py
git commit -m "feat: add --fail-focus CLI parameter"
```

---

### Task 4: Integration verification

**Files:**
- No new files

- [ ] **Step 1: Run the full behave test suite to check for regressions**

Run: `python -m pytest tests/unit/ -v`
Expected: All existing tests PASS

- [ ] **Step 2: Verify --fail-focus appears in help**

Run: `python -m behave --help | grep -A3 fail-focus`
Expected: Shows the `--fail-focus` option with its help text

- [ ] **Step 3: Test manually with a real feature file (if available)**

Run: `python -m behave --fail-focus` (in a directory with feature files)
Expected: Only the first failure is shown with Feature header, scenario, steps, and error

- [ ] **Step 4: Commit any fixes if needed**

```bash
git add -u
git commit -m "fix: address integration issues for --fail-focus"
```
