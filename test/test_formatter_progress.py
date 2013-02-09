# -*- coding: utf-8 -*-
"""
Test progress formatters:
  * behave.formatter.progress.ScenarioProgressFormatter
  * behave.formatter.progress.StepProgressFormatter
"""

from __future__ import absolute_import
from .test_formatter import FormatterTests as FormatterTest

class TestScenarioProgressFormatter(FormatterTest):
    formatter_name = "progress"


class TestStepProgressFormatter(FormatterTest):
    formatter_name = "progress2"


