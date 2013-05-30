# -*- coding: utf-8 -*-
"""
Test formatters:
  * behave.formatter.tags.TagsCountFormatter
  * behave.formatter.tags.TagsLocationFormatter
"""

from __future__ import absolute_import
from .test_formatter import FormatterTests as FormatterTest
from .test_formatter import MultipleFormattersTests as MultipleFormattersTest

# -----------------------------------------------------------------------------
# FORMATTER TESTS: With TagCountFormatter
# -----------------------------------------------------------------------------
class TestTagsCountFormatter(FormatterTest):
    formatter_name = "tags"

# -----------------------------------------------------------------------------
# FORMATTER TESTS: With TagLocationFormatter
# -----------------------------------------------------------------------------
class TestTagsLocationFormatter(FormatterTest):
    formatter_name = "tags.location"


# -----------------------------------------------------------------------------
# MULTI-FORMATTER TESTS: With TagCountFormatter
# -----------------------------------------------------------------------------
class TestPrettyAndTagsCount(MultipleFormattersTest):
    formatters = ["pretty", "tags"]

class TestPlainAndTagsCount(MultipleFormattersTest):
    formatters = ["plain", "tags"]

class TestJSONAndTagsCount(MultipleFormattersTest):
    formatters = ["json", "tags"]

class TestRerunAndTagsCount(MultipleFormattersTest):
    formatters = ["rerun", "tags"]


# -----------------------------------------------------------------------------
# MULTI-FORMATTER TESTS: With TagLocationFormatter
# -----------------------------------------------------------------------------
class TestPrettyAndTagsLocation(MultipleFormattersTest):
    formatters = ["pretty", "tags.location"]

class TestPlainAndTagsLocation(MultipleFormattersTest):
    formatters = ["plain", "tags.location"]

class TestJSONAndTagsLocation(MultipleFormattersTest):
    formatters = ["json", "tags.location"]

class TestRerunAndTagsLocation(MultipleFormattersTest):
    formatters = ["rerun", "tags.location"]

class TestTagsCountAndTagsLocation(MultipleFormattersTest):
    formatters = ["tags", "tags.location"]
