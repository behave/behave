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
