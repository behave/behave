"""Unit tests for the FailFocusFormatter."""

import io
import unittest
from unittest.mock import Mock

from behave.formatter.base import StreamOpener
from behave.model_type import Status


def make_feature(name="Test Feature", filename="features/test.feature"):
    feature = Mock()
    feature.name = name
    feature.filename = filename
    feature.keyword = "Feature"
    return feature


def make_scenario(name="Test Scenario", filename="features/test.feature", line=10):
    scenario = Mock()
    scenario.name = name
    scenario.keyword = "Scenario"
    scenario.location = Mock()
    scenario.location.filename = filename
    scenario.location.line = line
    return scenario


def make_step(keyword="Given", name="a step", status=Status.passed, error_message=None):
    step = Mock()
    step.keyword = keyword
    step.name = name
    step.status = status
    step.error_message = error_message
    return step


def make_formatter(stream):
    from behave.formatter.fail_focus import FailFocusFormatter
    config = Mock()
    stream_opener = StreamOpener(stream=stream)
    return FailFocusFormatter(stream_opener, config)


class TestFailFocusFormatterPassedScenario(unittest.TestCase):
    """A passed scenario should produce no output."""

    def test_passed_scenario_produces_no_output(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature()
        scenario = make_scenario()
        step1 = make_step("Given", "a passing step", Status.passed)

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.eof()
        formatter.close()

        self.assertEqual(stream.getvalue(), "")


class TestFailFocusFormatterFailedScenario(unittest.TestCase):
    """A failed scenario should produce output with feature, scenario, steps, and error."""

    def test_failed_scenario_produces_output(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature("Login", "features/login.feature")
        scenario = make_scenario("Bad password", "features/login.feature", 5)
        step1 = make_step("Given", "a user exists", Status.passed)
        step2 = make_step("When", "they enter wrong password", Status.failed,
                          "AssertionError: expected 200 got 401")

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.step(step2)
        formatter.result(step2)
        formatter.eof()
        formatter.close()

        output = stream.getvalue()
        self.assertIn("Feature: Login -- features/login.feature", output)
        self.assertIn("Scenario: Bad password  -- features/login.feature:5", output)
        self.assertIn("Given a user exists ... passed", output)
        self.assertIn("When they enter wrong password ... failed", output)
        self.assertIn("AssertionError: expected 200 got 401", output)

    def test_failed_scenario_exact_output_format(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature("Login", "features/login.feature")
        scenario = make_scenario("Bad password", "features/login.feature", 5)
        step1 = make_step("Given", "a user exists", Status.passed)
        step2 = make_step("When", "they enter wrong password", Status.failed,
                          "AssertionError: expected 200 got 401")

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.step(step2)
        formatter.result(step2)
        formatter.eof()
        formatter.close()

        expected = (
            "Feature: Login -- features/login.feature\n"
            "\n"
            "  Scenario: Bad password  -- features/login.feature:5\n"
            "    Given a user exists ... passed\n"
            "    When they enter wrong password ... failed\n"
            "AssertionError: expected 200 got 401\n"
        )
        self.assertEqual(stream.getvalue(), expected)


class TestFailFocusFormatterErrorScenario(unittest.TestCase):
    """A scenario with a Status.error step should produce output."""

    def test_error_scenario_produces_output(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature("Login", "features/login.feature")
        scenario = make_scenario("Crash on login", "features/login.feature", 20)
        step1 = make_step("Given", "a user exists", Status.passed)
        step2 = make_step("When", "the server crashes", Status.error,
                          "RuntimeError: unexpected failure")

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.step(step2)
        formatter.result(step2)
        formatter.eof()
        formatter.close()

        output = stream.getvalue()
        self.assertIn("Feature: Login -- features/login.feature", output)
        self.assertIn("Scenario: Crash on login", output)
        self.assertIn("When the server crashes ... error", output)
        self.assertIn("RuntimeError: unexpected failure", output)

    def test_hook_error_scenario_produces_output(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature("Login", "features/login.feature")
        scenario = make_scenario("Hook failure", "features/login.feature", 30)
        step1 = make_step("Given", "a step", Status.hook_error,
                          "HookError: before_scenario failed")

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.eof()
        formatter.close()

        output = stream.getvalue()
        self.assertIn("Scenario: Hook failure", output)
        self.assertIn("HookError: before_scenario failed", output)


class TestFailFocusFormatterFeatureDeduplication(unittest.TestCase):
    """Feature header should only be printed once per feature."""

    def test_feature_header_printed_once_for_multiple_failures(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature("Login", "features/login.feature")
        scenario1 = make_scenario("Fail 1", "features/login.feature", 5)
        scenario2 = make_scenario("Fail 2", "features/login.feature", 15)
        step1 = make_step("Given", "a failing step", Status.failed, "Error 1")
        step2 = make_step("Given", "another failing step", Status.failed, "Error 2")

        formatter.feature(feature)

        formatter.scenario(scenario1)
        formatter.step(step1)
        formatter.result(step1)

        formatter.scenario(scenario2)
        formatter.step(step2)
        formatter.result(step2)

        formatter.eof()
        formatter.close()

        output = stream.getvalue()
        # Feature header should appear exactly once
        self.assertEqual(output.count("Feature: Login -- features/login.feature"), 1)
        # Both scenarios should appear
        self.assertIn("Scenario: Fail 1", output)
        self.assertIn("Scenario: Fail 2", output)


class TestFailFocusFormatterUndefinedScenario(unittest.TestCase):
    """An undefined scenario should produce no output (suppressed by --fail-focus)."""

    def test_undefined_scenario_produces_no_output(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature()
        scenario = make_scenario()
        step1 = make_step("Given", "an undefined step", Status.undefined)

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.eof()
        formatter.close()

        self.assertEqual(stream.getvalue(), "")


class TestFailFocusFormatterSkippedScenario(unittest.TestCase):
    """A skipped scenario should produce no output."""

    def test_skipped_scenario_produces_no_output(self):
        stream = io.StringIO()
        formatter = make_formatter(stream)

        feature = make_feature()
        scenario = make_scenario()
        step1 = make_step("Given", "a skipped step", Status.skipped)

        formatter.feature(feature)
        formatter.scenario(scenario)
        formatter.step(step1)
        formatter.result(step1)
        formatter.eof()
        formatter.close()

        self.assertEqual(stream.getvalue(), "")


class TestFailFocusFormatterRegistration(unittest.TestCase):
    """The fail_focus formatter should be registered in the builtins."""

    def test_fail_focus_formatter_is_registered(self):
        from behave.formatter._registry import is_formatter_valid
        from behave.formatter._builtins import setup_formatters
        setup_formatters()
        self.assertTrue(is_formatter_valid("fail_focus"))


class TestFailFocusConfiguration(unittest.TestCase):
    def test_fail_focus_sets_stop_and_no_snippets_and_no_summary(self):
        from behave.configuration import Configuration
        config = Configuration(command_args=["--fail-focus", "features/"],
                               load_config=False)
        self.assertTrue(config.stop)
        self.assertFalse(config.show_snippets)
        self.assertFalse(config.summary)

    def test_fail_focus_sets_formatter_to_fail_focus(self):
        from behave.configuration import Configuration
        config = Configuration(command_args=["--fail-focus", "features/"],
                               load_config=False)
        self.assertIn("fail_focus", config.format)


if __name__ == "__main__":
    unittest.main()
