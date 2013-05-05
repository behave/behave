# -*- coding: utf-8 -*-
"""
Test formatters:
  * behave.formatter.tag_count.TagCountFormatter
  * behave.formatter.tag_count.TagLocationFormatter
"""

from __future__ import absolute_import
from .test_formatter import FormatterTests as FormatterTest
from .test_formatter import MultipleFormattersTests as MultipleFormattersTest

# -----------------------------------------------------------------------------
# FORMATTER TESTS: With TagCountFormatter
# -----------------------------------------------------------------------------
class TestTagCountFormatter(FormatterTest):
    formatter_name = "tag_count"

# -----------------------------------------------------------------------------
# FORMATTER TESTS: With TagLocationFormatter
# -----------------------------------------------------------------------------
class TestTagLocationFormatter(FormatterTest):
    formatter_name = "tag_location"


# -----------------------------------------------------------------------------
# MULTI-FORMATTER TESTS: With TagCountFormatter
# -----------------------------------------------------------------------------
class TestPrettyAndTagCount(MultipleFormattersTest):
    formatters = ["pretty", "tag_count"]

class TestPlainAndTagCount(MultipleFormattersTest):
    formatters = ["plain", "tag_count"]

class TestJSONAndTagCount(MultipleFormattersTest):
    formatters = ["json", "tag_count"]

class TestRerunAndTagCount(MultipleFormattersTest):
    formatters = ["rerun", "tag_count"]


# -----------------------------------------------------------------------------
# MULTI-FORMATTER TESTS: With TagLocationFormatter
# -----------------------------------------------------------------------------
class TestPrettyAndTagLocation(MultipleFormattersTest):
    formatters = ["pretty", "tag_location"]

class TestPlainAndTagLocation(MultipleFormattersTest):
    formatters = ["plain", "tag_location"]

class TestJSONAndTagLocation(MultipleFormattersTest):
    formatters = ["json", "tag_location"]

class TestRerunAndTagLocation(MultipleFormattersTest):
    formatters = ["rerun", "tag_location"]

class TestTagCountAndTagLocation(MultipleFormattersTest):
    formatters = ["tag_count", "tag_location"]
