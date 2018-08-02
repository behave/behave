# -*- coding: UTF-8 -*-
"""
Provides a step registry and step decorators.
The step registry allows to match steps (model elements) with
step implementations (step definitions). This is necessary to execute steps.
"""

from __future__ import absolute_import
import functools
from behave.matchers import Match, get_matcher
from behave.textutil import text as _text

# limit import * to just the decorators
# pylint: disable=undefined-all-variable
# names = "given when then step"
# names = names + " " + names.title()
# __all__ = names.split()
__all__ = [
    "given", "when", "then", "step",    # PREFERRED.
    "Given", "When", "Then", "Step"     # Also possible.
]


class AmbiguousStep(ValueError):
    pass


class StepRegistry(object):
    def __init__(self):
        self.steps = {
            "given": [],
            "when": [],
            "then": [],
            "step": [],
        }

    @staticmethod
    def same_step_definition(step, other_pattern, other_location):
        return (step.pattern == other_pattern and
                step.location == other_location and
                other_location.filename != "<string>")

    def add_step_definition(self, keyword, step_text, func):
        step_location = Match.make_location(func)
        step_type = keyword.lower()
        step_text = _text(step_text)
        step_definitions = self.steps[step_type]
        for existing in step_definitions:
            if self.same_step_definition(existing, step_text, step_location):
                # -- EXACT-STEP: Same step function is already registered.
                # This may occur when a step module imports another one.
                return
            elif existing.match(step_text):     # -- SIMPLISTIC
                message = u"%s has already been defined in\n  existing step %s"
                new_step = u"@%s('%s')" % (step_type, step_text)
                existing.step_type = step_type
                existing_step = existing.describe()
                existing_step += u" at %s" % existing.location
                raise AmbiguousStep(message % (new_step, existing_step))
        step_definitions.append(get_matcher(func, step_text))

    def find_step_definition(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps["step"]
        if step.step_type != "step" and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for step_definition in candidates:
            if step_definition.match(step.name):
                return step_definition
        return None

    def find_match(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps["step"]
        if step.step_type != "step" and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for step_definition in candidates:
            result = step_definition.match(step.name)
            if result:
                return result

        return None

    def make_decorator(self, step_type):
        def decorator(step_text):
            def wrapper(func):
                self.add_step_definition(step_type, step_text, func)
                return func
            return wrapper
        return decorator


registry = StepRegistry()

# -- Create the decorators
# pylint: disable=redefined-outer-name
def setup_step_decorators(run_context=None, registry=registry):
    if run_context is None:
        run_context = globals()
    for step_type in ("given", "when", "then", "step"):
        step_decorator = registry.make_decorator(step_type)
        run_context[step_type.title()] = run_context[step_type] = step_decorator


class LocalRegistry(StepRegistry):
    _matcher = None
    def __init__(self, matcher=None):
        if matcher:
            self._matcher = matcher
        super(LocalRegistry, self).__init__()

    @property
    def matcher(self):
        if self._matcher:
            return self._matcher
        else:
            return get_matcher

    def get_matcher(self, func, step_text, matcher=None):
        if matcher is None:
            matcher = self.matcher
        return matcher(func, step_text)

    def add_step_definition(self, keyword, step_text, func, matcher=None):
        step_type = keyword.lower()
        step_text = _text(step_text)
        self.steps[step_type].append(self.get_matcher(func, step_text, matcher))

    def make_decorator(self, step_type):
        @staticmethod
        def decorator(step_text, matcher=None):
            def wrapper(func):
                self.add_step_definition(step_type, step_text, func, matcher)
                return func
            return wrapper
        return decorator



def local_step_registry(default_matcher=None):
    class LocalStepRegistry(object):
        _registry = LocalRegistry(matcher=default_matcher)
        _context = None

        @property
        def context(self):
            return self._context

        def register(self):
            """
            adds contained definitions to the global registry

            This function also is responsible for updating functions in the registry with functions
            defined in subclasses
            """
            from behave.runner import the_step_registry  # make sure we use same registry as normal definitions
            for step_type, steps in self._registry.steps.items():
                for match_obj in steps:
                    if hasattr(self, match_obj.func.__name__):
                        method = getattr(self, match_obj.func.__name__)
                        match_obj.func = self._step_context(method)
                    the_step_registry.steps[step_type].append(match_obj)

        @classmethod
        def _step_context(cls, method):
            from behave.runner import Context
            @functools.wraps(method)
            def newmethod(*args, **kwargs):
                if args:
                    context = args[0]
                    other_args = args[1:]
                    if isinstance(context, Context):
                        cls._context = context
                        args = other_args
                return method(*args, **kwargs)
            return newmethod



    for step_type in ("given", "when", "then", "step"):
        step_decorator = LocalStepRegistry._registry.make_decorator(step_type)
        setattr(LocalStepRegistry, step_type, step_decorator)
        setattr(LocalStepRegistry, step_type.title(), step_decorator)
    return LocalStepRegistry

# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
setup_step_decorators()
