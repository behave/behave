# -*- coding: utf-8 -*-
"""
Provides a step registry and step decorators.
The step registry allows to match steps (model elements) with
step implementations (step definitions). This is necessary to execute steps.
"""


class AmbiguousStep(ValueError):
    pass


class StepRegistry(object):
    def __init__(self):
        self.steps = {
            'given': [],
            'when': [],
            'then': [],
            'step': [],
        }

    @staticmethod
    def same_step_definition(step, other_string, other_location):
        return (step.string == other_string and
                step.location == other_location and
                other_location.filename != "<string>")

    def add_step_definition(self, keyword, string, func):
        # TODO try to fix module dependencies to avoid this
        from behave import matchers, model
        step_location = model.Match.make_location(func)
        step_type = keyword.lower()
        step_definitions = self.steps[step_type]
        for existing in step_definitions:
            if self.same_step_definition(existing, string, step_location):
                # -- EXACT-STEP: Same step function is already registered.
                # This may occur when a step module imports another one.
                return
            elif existing.match(string):
                message = '%s has already been defined in\n  existing step %s'
                new_step = u"@%s('%s')" % (step_type, string)
                existing.step_type = step_type
                existing_step = existing.describe()
                existing_step += " at %s" % existing.location
                raise AmbiguousStep(message % (new_step, existing_step))
        step_definitions.append(matchers.get_matcher(func, string))

    def find_step_definition(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps['step']
        if step.step_type != 'step' and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for step_definition in candidates:
            if step_definition.match(step.name):
                return step_definition
        return None

    def find_match(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps['step']
        if step.step_type != 'step' and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for step_definition in candidates:
            result = step_definition.match(step.name)
            if result:
                return result

        return None

    def make_decorator(self, step_type):
        # pylint: disable=W0621
        #   W0621: 44,29:StepRegistry.make_decorator: Redefining 'step_type' ..
        def decorator(string):
            def wrapper(func):
                self.add_step_definition(step_type, string, func)
                return func
            return wrapper
        return decorator


registry = StepRegistry()

# -- Create the decorators
def setup_step_decorators(context=None, registry=registry):
    if context is None:
        context = globals()
    for step_type in ('given', 'when', 'then', 'step'):
        step_decorator = registry.make_decorator(step_type)
        context[step_type.title()] = context[step_type] = step_decorator

# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
# limit import * to just the decorators
names = 'given when then step'
names = names + ' ' + names.title()
__all__ = names.split()

setup_step_decorators()
