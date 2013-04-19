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
    formattes = ['pretty', 'progress']

class TestPlainAndScenarioProgress(MultipleFormattersTest):
    formattes = ['plain', 'progress']

class TestJSONAndScenarioProgress(MultipleFormattersTest):
    formattes = ['json', 'progress']

class TestPrettyAndStepProgress(MultipleFormattersTest):
    formattes = ['pretty', 'progress2']

class TestPlainAndStepProgress(MultipleFormattersTest):
    formattes = ['plain', 'progress2']

class TestJSONAndStepProgress(MultipleFormattersTest):
    formattes = ['json', 'progress2']

class TestScenarioProgressAndStepProgress(MultipleFormattersTest):
    formattes = ['progress', 'progress2']
