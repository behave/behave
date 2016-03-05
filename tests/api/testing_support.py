# -*- coding: UTF-8 -*-
"""
Test support functionality for other tests.
"""

# -- IMPORTS:
from __future__ import absolute_import
from behave.step_registry import StepRegistry
from behave.matchers import ParseMatcher, CFParseMatcher, RegexMatcher
import time


# -----------------------------------------------------------------------------
# TEST SUPPORT:
# -----------------------------------------------------------------------------
class StopWatch(object):
    def __init__(self):
        self.start_time = None
        self.duration = None

    def start(self):
        self.start_time = self.now()
        self.duration = None

    def stop(self):
        self.duration = self.now() - self.start_time

    @staticmethod
    def now():
        return time.time()

    @property
    def elapsed(self):
        assert self.start_time is not None
        return self.now() - self.start_time

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

# -- NEEDED-UNTIL: stepimport functionality is completly provided.
class MatcherFactory(object):
    matcher_mapping = {
        "parse": ParseMatcher,
        "cfparse": CFParseMatcher,
        "re": RegexMatcher,
    }
    default_matcher = ParseMatcher

    def __init__(self, matcher_mapping=None, default_matcher=None):
        self.matcher_mapping = matcher_mapping or self.matcher_mapping
        self.default_matcher = default_matcher or self.default_matcher
        self.current_matcher = self.default_matcher
        self.type_registry = {}
        # self.type_registry = ParseMatcher.custom_types.copy()

    def register_type(self, **kwargs):
        self.type_registry.update(**kwargs)

    def use_step_matcher(self, name):
        self.current_matcher = self.matcher_mapping[name]

    def use_default_step_matcher(self, name=None):
        if name:
            self.default_matcher = self.matcher_mapping[name]
        self.current_matcher = self.default_matcher

    def make_matcher(self, func, step_text, step_type=None):
        return self.current_matcher(func, step_text, step_type=step_type,
                                    custom_types=self.type_registry)

    def step_matcher(self, name):
        """
        DEPRECATED, use :method:`~MatcherFactory.use_step_matcher()` instead.
        """
        # -- BACKWARD-COMPATIBLE NAME: Mark as deprecated.
        import warnings
        warnings.warn("Use 'use_step_matcher()' instead",
                      PendingDeprecationWarning, stacklevel=2)
        self.use_step_matcher(name)


class SimpleStepContainer(object):
    def __init__(self, step_registry=None):
        if step_registry is None:
            step_registry = StepRegistry()
        matcher_factory = MatcherFactory()

        self.step_registry = step_registry
        self.step_registry.matcher_factory = matcher_factory
        self.matcher_factory = matcher_factory
