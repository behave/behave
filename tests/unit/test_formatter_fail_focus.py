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


class TestFailFocusFormatterUndefinedScenario(unittest.TestCase):
    """An undefined scenario should produce no output."""

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


if __name__ == "__main__":
    unittest.main()
