# -*- coding: UTF-8 -*-
"""
(Additional) Unit tests for :mod:`behave.model_core` module.
"""

from __future__ import print_function
from behave.model_core import Status
import pytest


# -----------------------------------------------------------------------------
# TESTS:
# -----------------------------------------------------------------------------
class TestStatus(object):
    """Test Status enum class.
    In addition, checks if it is partly backward compatibility to
    string-based status.

    EXAMPLE::

        status = Status.passed
        assert status == "passed"
        assert status != "failed"
        assert status == Status.from_name("passed")
    """

    @pytest.mark.parametrize("enum_value", list(Status.__members__.values()))
    def test_equals__with_string_value(self, enum_value):
        """Ensure that Status enum value can be compared with a string-status"""
        assert enum_value == enum_value.name

    @pytest.mark.parametrize("enum_value", list(Status.__members__.values()))
    def test_equals__with_unknown_name(self, enum_value):
        assert enum_value != "__UNKNOWN__"
        assert not (enum_value == "__UNKNOWN__")

    @pytest.mark.parametrize("enum_value, similar_name", [
        (Status.passed, "Passed"),
        (Status.failed, "FAILED"),
        (Status.passed, "passed1"),
        (Status.failed, "failed2"),
    ])
    def test_equals__with_similar_name(self, enum_value, similar_name):
        assert enum_value != similar_name

    @pytest.mark.parametrize("enum_value", list(Status.__members__.values()))
    def test_from_name__with_known_names(self, enum_value):
        assert enum_value == Status.from_name(enum_value.name)


    @pytest.mark.parametrize("unknown_name", [
        "Passed", "Failed", "passed2", "failed1"
    ])
    def test_from_name__with_unknown_name_raises_lookuperror(self, unknown_name):
        with pytest.raises(LookupError):
            Status.from_name(unknown_name)
