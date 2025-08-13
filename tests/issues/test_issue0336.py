"""
Test issue #336: Unicode problem w/ exception traceback on Windows (python2.7)
Default encoding (unicode-escape) of text() causes problems w/
exception tracebacks.

STATUS: BASICS SOLVED (default encoding changed)

ALTERNATIVE SOLUTIONS:
* Use traceback2: Returns unicode-string when calling traceback.
* Use text(traceback.format_exc(), sys.getfilesystemencoding(), "replace")
  where the text-conversion of a traceback is used.
  MAYBE traceback_to_text(traceback.format_exc())
"""

from behave.textutil import text
import pytest


class TestIssue(object):
    # -- USE SAVED TRACEBACK: No need to require Windows platform.
    traceback_bytes = br"""\
Traceback (most recent call last):
  File "C:\Users\alice\xxx\behave\model.py", line 1456, in run
    match.run(runner.context)
  File "C:\Users\alice\xxx\behave\model.py", line 1903, in run
    self.func(context, args, *kwargs)
  File "features\steps\my_steps.py", line 210, in step_impl
    directories, task_names, reg_keys)
AssertionError
"""

    traceback_file_line_texts = [
        # -- NOTE: Cannot use: ur'C:\Users ..." => \U is a unicode escape char.
         'File "C:\\Users\\alice\\xxx\\behave\\model.py", line 1456, in run',
         'File "C:\\Users\\alice\\xxx\\behave\\model.py", line 1903, in run',
         'File "features\\steps\\my_steps.py", line 210, in step_impl',
    ]

    def test_issue__with_default_encoding(self):
        """Test ensures that problem is fixed with default encoding"""
        text2 = text(self.traceback_bytes)
        assert isinstance(self.traceback_bytes, bytes)
        assert isinstance(text2, str)
        for file_line_text in self.traceback_file_line_texts:
            assert file_line_text in text2

    @pytest.mark.filterwarnings("ignore:invalid escape sequence")
    @pytest.mark.filterwarnings("ignore:.* is an invalid escape sequence.*:DeprecationWarning")
    def test__problem_exists_with_problematic_encoding(self):
        """Test ensures that problem exists with encoding=unicode-escape"""
        # -- NOTE: Explicit use of problematic encoding
        problematic_encoding = "unicode-escape"
        text2 = text(self.traceback_bytes, problematic_encoding)
        print("TEXT: "+ text2)
        assert isinstance(self.traceback_bytes, bytes)
        assert isinstance(text2, str)

        # -- VERIFY BAD-OUTCOME: With problematic encoding
        file_line_text = self.traceback_file_line_texts[0]
        assert file_line_text not in text2
