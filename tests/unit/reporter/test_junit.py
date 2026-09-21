"""Tests for JUnitReporter."""

from unittest.mock import patch, mock_open

from behave.reporter.junit import JUnitReporter


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
