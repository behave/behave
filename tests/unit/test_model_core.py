# -*- coding: UTF-8 -*-
"""
(Additional) Unit tests for :mod:`behave.model_core` module.
"""

from __future__ import print_function
import six
from behave.model_core import Status, FileLocation
import pytest


# -- CONVENIENCE-ALIAS:
_text = six.text_type



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


class TestFileLocation(object):
    # pylint: disable=invalid-name
    ordered_locations1 = [
        FileLocation("features/alice.feature", 1),
        FileLocation("features/alice.feature", 5),
        FileLocation("features/alice.feature", 10),
        FileLocation("features/alice.feature", 11),
        FileLocation("features/alice.feature", 100),
    ]
    ordered_locations2 = [
        FileLocation("features/alice.feature", 1),
        FileLocation("features/alice.feature", 10),
        FileLocation("features/bob.feature", 5),
        FileLocation("features/charly.feature", None),
        FileLocation("features/charly.feature", 0),
        FileLocation("features/charly.feature", 100),
    ]
    same_locations = [
        (FileLocation("alice.feature"),
         FileLocation("alice.feature", None),
        ),
        (FileLocation("alice.feature", 10),
         FileLocation("alice.feature", 10),
        ),
        (FileLocation("features/bob.feature", 11),
         FileLocation("features/bob.feature", 11),
        ),
    ]

    def test_compare_equal(self):
        for value1, value2 in self.same_locations:
            assert value1 == value2

    def test_compare_equal_with_string(self):
        for location in self.ordered_locations2:
            assert location == location.filename
            assert location.filename == location

    def test_compare_not_equal(self):
        for value1, value2 in self.same_locations:
            assert not(value1 != value2)    # pylint: disable=unneeded-not, superfluous-parens

        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value1 != value2

    def test_compare_less_than(self):
        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value1 < value2, "FAILED: %s < %s" % (_text(value1), _text(value2))
                assert value1 != value2

    def test_compare_less_than_with_string(self):
        locations = self.ordered_locations2
        for value1, value2 in zip(locations, locations[1:]):
            if value1.filename == value2.filename:
                continue
            assert value1 < value2.filename, \
                   "FAILED: %s < %s" % (_text(value1), _text(value2.filename))
            assert value1.filename < value2, \
                   "FAILED: %s < %s" % (_text(value1.filename), _text(value2))

    def test_compare_greater_than(self):
        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value2 > value1, "FAILED: %s > %s" % (_text(value2), _text(value1))
                assert value2 != value1

    def test_compare_less_or_equal(self):
        for value1, value2 in self.same_locations:
            assert value1 <= value2, "FAILED: %s <= %s" % (_text(value1), _text(value2))
            assert value1 == value2

        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value1 <= value2, "FAILED: %s <= %s" % (_text(value1), _text(value2))
                assert value1 != value2

    def test_compare_greater_or_equal(self):
        for value1, value2 in self.same_locations:
            assert value2 >= value1, "FAILED: %s >= %s" % (_text(value2), _text(value1))
            assert value2 == value1

        for locations in [self.ordered_locations1, self.ordered_locations2]:
            for value1, value2 in zip(locations, locations[1:]):
                assert value2 >= value1, "FAILED: %s >= %s" % (_text(value2), _text(value1))
                assert value2 != value1

    def test_filename_should_be_same_as_self(self):
        for location in self.ordered_locations2:
            assert location == location.filename
            assert location.filename == location

    def test_string_conversion(self):
        for location in self.ordered_locations2:
            expected = u"%s:%s" % (location.filename, location.line)
            if location.line is None:
                expected = location.filename
            assert six.text_type(location) == expected

    def test_repr_conversion(self):
        for location in self.ordered_locations2:
            expected = u'<FileLocation: filename="%s", line=%s>' % \
                       (location.filename, location.line)
            actual = repr(location)
            assert actual == expected, "FAILED: %s == %s" % (actual, expected)
