# -*- coding: utf-8 -*-
"""
Knowledge base of all built-in formatters.
"""

from __future__ import  absolute_import
from behave.formatter import _registry


# -----------------------------------------------------------------------------
# DATA:
# -----------------------------------------------------------------------------
# SCHEMA: formatter.name, formatter.class(_name)
_BUILTIN_FORMATS = [
    # pylint: disable=bad-whitespace
    ("plain",   "behave.formatter.plain:PlainFormatter"),
    ("pretty",  "behave.formatter.pretty:PrettyFormatter"),
    ("json",    "behave.formatter.json:JSONFormatter"),
    ("json.pretty", "behave.formatter.json:PrettyJSONFormatter"),
    ("null",      "behave.formatter.null:NullFormatter"),
    ("progress",  "behave.formatter.progress:ScenarioProgressFormatter"),
    ("progress2", "behave.formatter.progress:StepProgressFormatter"),
    ("progress3", "behave.formatter.progress:ScenarioStepProgressFormatter"),
    ("rerun",     "behave.formatter.rerun:RerunFormatter"),
    ("tags",          "behave.formatter.tags:TagsFormatter"),
    ("tags.location", "behave.formatter.tags:TagsLocationFormatter"),
    ("steps",         "behave.formatter.steps:StepsFormatter"),
    ("steps.doc",     "behave.formatter.steps:StepsDocFormatter"),
    ("steps.bad", "behave.formatter.bad_steps:BadStepsFormatter"),
    ("steps.catalog", "behave.formatter.steps:StepsCatalogFormatter"),
    ("steps.code",    "behave.formatter.steps_code:StepWithCodeFormatter"),
    ("steps.missing", "behave.contrib.formatter_missing_steps:MissingStepsFormatter"),
    ("steps.usage",   "behave.formatter.steps:StepsUsageFormatter"),
    ("sphinx.steps",  "behave.formatter.sphinx_steps:SphinxStepsFormatter"),
    ("captured", "behave.formatter.captured:CapturedFormatter"),
]


# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_formatters():
    """Register all built-in formatters (lazy-loaded)."""
    _registry.register_formats(_BUILTIN_FORMATS)
