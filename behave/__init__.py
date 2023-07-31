# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
"""
behave is behaviour-driven development, Python style

Behavior-driven development (or BDD) is an agile software development
technique that encourages collaboration between developers, QA and
non-technical or business participants in a software project.

*behave* uses tests written in a natural language style, backed up by Python
code.

To get started, we recommend the `tutorial`_ and then the `test language`_ and
`api`_ references.

.. _`tutorial`: tutorial.html
.. _`test language`: gherkin.html
.. _`api`: api.html
"""

from __future__ import absolute_import
# pylint: disable=no-name-in-module
from behave.step_registry import given, when, then, step, Given, When, Then, Step
# pylint: enable=no-name-in-module
from behave.api.step_matchers import (
    register_type,
    use_default_step_matcher, use_step_matcher,
    step_matcher
)
from behave.fixture import fixture, use_fixture
from behave.version import VERSION as __version__  # noqa: F401

# pylint: disable=undefined-all-variable
__all__ = [
    "given", "when", "then", "step",
    "Given", "When", "Then", "Step",
    "use_default_step_matcher", "use_step_matcher", "register_type",
    "fixture", "use_fixture",
    # -- DEPRECATING:
    "step_matcher"
]
