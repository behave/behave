# -*- coding: utf-8 -*-
"""
Test progress formatters:
  * behave.formatter.progress.ScenarioProgressFormatter
  * behave.formatter.progress.StepProgressFormatter
"""

from __future__ import absolute_import
from .test_formatter import FormatterTests as FormatterTest
from .test_formatter import MultipleFormattersTests as MultipleFormattersTest

class TestScenarioProgressFormatter(FormatterTest):
    formatter_name = "progress"


class TestStepProgressFormatter(FormatterTest):
    formatter_name = "progress2"


class TestPrettyAndScenarioProgress(MultipleFormattersTest):
    formatters = ['pretty', 'progress']

class TestPlainAndScenarioProgress(MultipleFormattersTest):
    formatters = ['plain', 'progress']

class TestJSONAndScenarioProgress(MultipleFormattersTest):
    formatters = ['json', 'progress']

class TestPrettyAndStepProgress(MultipleFormattersTest):
    formatters = ['pretty', 'progress2']

class TestPlainAndStepProgress(MultipleFormattersTest):
    formatters = ['plain', 'progress2']

class TestJSONAndStepProgress(MultipleFormattersTest):
    formatters = ['json', 'progress2']

class TestScenarioProgressAndStepProgress(MultipleFormattersTest):
    formatters = ['progress', 'progress2']
