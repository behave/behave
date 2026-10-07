"""
Tests for :mod:`behave.model_type` module.
"""

import os
import platform
from unittest.mock import patch

import pytest

from behave.model_type import make_relpath_if_possible

todo = pytest.mark.todo()


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
@todo
class TestStatus:
    pass

@todo
class TestScenarioStatus:
    pass

@todo
class TestOuterStatus:
    pass

@todo
class TestFileLocation:
    pass


class TestMakeRelpathIfPossible:
    def test_returns_relative_path_when_same_drive(self):
        base = os.path.abspath(os.path.join(os.sep, "home", "user"))
        filename = os.path.join(base, "features", "test.feature")
        result = make_relpath_if_possible(filename, base)
        assert result == os.path.join("features", "test.feature")

    def test_returns_absolute_path_when_cross_drive_on_windows(self):
        if platform.system() != "Windows":
            pytest.skip("Cross-drive paths only exist on Windows")
        base = "C:\\home\\user"
        filename = "D:\\other\\steps\\test.py"
        result = make_relpath_if_possible(filename, base)
        assert result == filename

    def test_returns_absolute_path_when_os_relpath_raises_valueerror(self):
        base = "/home/user"
        filename = "/other/steps/test.py"
        with patch("os.path.relpath", side_effect=ValueError("cross-drive")):
            result = make_relpath_if_possible(filename, base)
        assert result == filename
