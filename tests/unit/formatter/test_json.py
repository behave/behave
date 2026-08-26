"""
Unit tests for :mod:`behave.formatter.json` module.

Focus: :meth:`JSONFormatter.make_captured_output()` -- the captured
stdout/stderr/log JSON fields (see issue #1323).
"""

from behave.capture import Captured, NO_CAPTURED_DATA
from behave.formatter.json import JSONFormatter


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestMakeCapturedOutput:
    """Unit tests for the (isolated) captured-output field builder."""

    def test_without_output__returns_empty(self):
        captured = Captured()
        assert JSONFormatter.make_captured_output(captured) == {}

    def test_with_no_captured_data__returns_empty(self):
        assert JSONFormatter.make_captured_output(NO_CAPTURED_DATA) == {}

    def test_with_none__returns_empty(self):
        assert JSONFormatter.make_captured_output(None) == {}

    def test_with_log_only(self):
        captured = Captured(log="LOG_ERROR:foo: Hello")
        captured_fields = JSONFormatter.make_captured_output(captured)
        assert captured_fields == {"captured_log": "LOG_ERROR:foo: Hello"}

    def test_with_all_streams(self):
        captured = Captured(stdout="OUT", stderr="ERR", log="LOG")
        captured_fields = JSONFormatter.make_captured_output(captured)
        assert captured_fields == {
            "captured_stdout": "OUT",
            "captured_stderr": "ERR",
            "captured_log": "LOG",
        }

    def test_multiline_text_is_split_into_lines(self):
        captured = Captured(log="line1\nline2")
        captured_fields = JSONFormatter.make_captured_output(captured)
        assert captured_fields == {"captured_log": ["line1", "line2"]}

    def test_exclude_text__omits_duplicated_stderr(self):
        # -- DUPLICATION: A failed step stores its error_message in captured stderr.
        error_message = "ASSERT FAILED: EXPECT something"
        captured = Captured(stderr=error_message, log="LOG", failed=True)
        captured_fields = JSONFormatter.make_captured_output(
            captured, exclude_text=error_message)
        assert "captured_stderr" not in captured_fields
        assert captured_fields == {"captured_log": "LOG"}

    def test_exclude_text__keeps_distinct_stderr(self):
        captured = Captured(stderr="real stderr output")
        captured_fields = JSONFormatter.make_captured_output(
            captured, exclude_text="a different error message")
        assert captured_fields == {"captured_stderr": "real stderr output"}
