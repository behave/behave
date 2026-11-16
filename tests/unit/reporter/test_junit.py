"""Tests for JUnitReporter."""

import pytest
import re

from unittest.mock import patch, mock_open

from behave.reporter.junit import JUnitReporter
from behave.model import Scenario, Status, Step


def test_feature_closes_report_file(mock_config, feature):
    """Verify the report file handle is deterministically closed."""
    reporter = JUnitReporter(mock_config)
    m = mock_open()

    with patch("builtins.open", m):
        reporter.feature(feature)

    handle = m()
    handle.__exit__.assert_called()


def test_feature_writes_report_file(mock_config, feature, tmp_path):
    """Verify the report file is actually written."""
    reporter = JUnitReporter(mock_config)

    reporter.feature(feature)

    report_files = list(tmp_path.glob("TESTS-*.xml"))
    assert len(report_files) == 1
    content = report_files[0].read_bytes()
    assert b"Test Feature" in content


def test_feature_creates_missing_report_directory(mock_config, feature, tmp_path):
    """Verify that multiple directory levels are created at once."""
    report_dir = tmp_path / "reports" / "junit"
    mock_config.junit_directory = str(report_dir)
    reporter = JUnitReporter(mock_config)

    reporter.feature(feature)

    assert len(list(report_dir.glob("TESTS-*.xml"))) == 1


def test_feature_tolerates_concurrently_created_report_directory(
        mock_config, feature, tmp_path):
    """Verify that a report directory, that another process creates between
    an existence check and its creation, does not cause an error.

    Several behave processes may use the same JUnit report directory.
    """
    reporter = JUnitReporter(mock_config)

    # -- SIMULATE RACE: Directory does not exist when checked, but exists
    # when it should be created (here: tmp_path exists already).
    with patch("os.path.exists", return_value=False):
        reporter.feature(feature)

    assert len(list(tmp_path.glob("TESTS-*.xml"))) == 1


_re_illegal_characters = re.compile(r"[\x00-\x08\x0B-\x1F\x7F-\x84\x86-\x9F]")


def test_feature_report_file_replaces_illegal_characters(mock_config, feature, tmp_path):
    """Verify the feature report file does not contain illegal characters."""
    scenario = Scenario("Test.feature", 2600, "Scenario", "Test scenario")
    scenario.set_status(Status.failed)
    scenario.error_message = "Error with some \x07s and whistles, like: \x0B\x0C\x7F\x80"
    feature.add_scenario(scenario)

    reporter = JUnitReporter(mock_config)

    reporter.feature(feature)

    report_files = list(tmp_path.glob("TESTS-*.xml"))
    assert len(report_files) == 1
    content = report_files[0].read_bytes()
    assert b"Test Feature" in content
    assert not _re_illegal_characters.search(content.decode("utf-8"))


@pytest.mark.parametrize(
    "step_text, error_text",
    [
        ("there is a regular step", "Regular error"),
        ("we add some \x07s and whistles, like: \x0B\x0C\x7F\x80", "This is a regular error text"),
        ("there is a regular step", "Error with some \x07s and whistles, like: \x0B\x0C\x7F\x80"),
    ]
)
def test_feature_testcase_report_file_replaces_illegal_characters(
        step_text, error_text, mock_config, feature, tmp_path):
    """Verify the step report file does not contain illegal characters."""
    step = Step("Test.feature", 2601, "Given", "Given", step_text)
    step.set_status(Status.failed)
    step.exception = AssertionError(error_text)
    scenario = Scenario("Test.feature", 2600, "Scenario", "Test scenario", steps = [step])
    scenario.set_status(Status.failed)
    feature.add_scenario(scenario)

    reporter = JUnitReporter(mock_config)

    reporter.feature(feature)

    report_files = list(tmp_path.glob("TESTS-*.xml"))
    assert len(report_files) == 1
    content = report_files[0].read_bytes()
    assert b"Test Feature" in content
    assert not _re_illegal_characters.search(content.decode("utf-8"))
