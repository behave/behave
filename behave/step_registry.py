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

    def add_definition(self, keyword, string, func):
        # TODO try to fix module dependencies to avoid this
        from behave import matchers
        keyword = self.steps[keyword.lower()]
        for existing in keyword:
            if existing.match(string):
                message = '"%s" has already been defined in\n  existing %s'
                raise AmbiguousStep(message % (string, existing.describe()))
        keyword.append(matchers.get_matcher(func, string))

    def find_match(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps['step']
        if step.step_type != 'step' and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for matcher in candidates:
            result = matcher.match(step.name)
            if result:
                return result

        return None

    def make_decorator(self, step_type):
        # pylint: disable=W0621
        #   W0621: 44,29:StepRegistry.make_decorator: Redefining 'step_type' ..
        def decorator(string):
            def wrapper(func):
                self.add_definition(step_type, string, func)
                return func
            return wrapper
        return decorator


registry = StepRegistry()

# -- Create the decorators
g = globals()
for step_type in ('given', 'when', 'then', 'step'):
    g[step_type.title()] = g[step_type] = registry.make_decorator(step_type)


# limit import * to just the decorators
names = 'given when then step'
names = names + ' ' + names.title()
__all__ = names.split()
