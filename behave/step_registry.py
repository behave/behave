# -*- coding: UTF-8 -*-
"""
Provides a step registry and step decorators.
The step registry allows to match steps (model elements) with
step implementations (step definitions). This is necessary to execute steps.
"""

from __future__ import absolute_import
from behave.matchers import Match, get_matcher
from behave.textutil import text as _text


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
        self.scenarios = {}

    @staticmethod
    def same_step_definition(step, other_string, other_location):
        return (step.string == other_string and
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
            elif existing.match(step_text):
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

        if step.step_type == 'given':
            # lookup scenario named with this step name
            from behave import model
            if step.name in self.scenarios:
                scenario = self.scenarios[step.name]
                to_exec = ['{step_type} {name}'.format(
                    step_type=s.step_type,
                    name=s.name)
                           for s in scenario.steps]
                def new_given_step(context):
                    context.execute_steps(u'\n'.join(to_exec))
                return model.Match(new_given_step, [])
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

# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
setup_step_decorators()

# limit import * to just the decorators
# pylint: disable=undefined-all-variable
# names = "given when then step"
# names = names + " " + names.title()
# __all__ = names.split()
__all__ = [
    "given", "when", "then", "step",    # PREFERRED.
    "Given", "When", "Then", "Step"     # Also possible.
]

