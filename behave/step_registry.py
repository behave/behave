# -*- coding: UTF-8 -*-
"""
Provides a step registry and step decorators.
The step registry allows to match steps (model elements) with
step implementations (step definitions). This is necessary to execute steps.
"""

from __future__ import absolute_import, print_function

import inspect
import sys

from behave.matchers import make_step_matcher
from behave.python_feature import PythonFeature
from behave.textutil import text as _text

_PYTHON_VERSION = sys.version_info[:2]
_FEATURE_ASYNC_FUNC = PythonFeature.has_async_function()
if _FEATURE_ASYNC_FUNC:
    from behave.async_step import AsyncStepFunction

# limit import * to just the decorators
# pylint: disable=undefined-all-variable
# names = "given when then step"
# names = names + " " + names.title()
# __all__ = names.split()
__all__ = [     # noqa: F822
    "given", "when", "then", "step",    # PREFERRED.
    "Given", "When", "Then", "Step"     # Also possible.
]


class AmbiguousStep(ValueError):
    pass


class BadStepDefinitionCollector(object):
    BAD_STEP_DEFINITION_MESSAGE = """\
BAD-STEP-DEFINITION: {step}
  LOCATION: {step_location}
""".strip()
    BAD_STEP_DEFINITION_MESSAGE_WITH_ERROR = BAD_STEP_DEFINITION_MESSAGE + """
  RAISED EXCEPTION: {error.__class__.__name__}:{error}"""

    def __init__(self, bad_step_definitions=None, file=None):
        self.bad_step_definitions = bad_step_definitions or []
        self.file = file or sys.stdout

    def clear(self):
        self.bad_step_definitions = []

    def print_all(self):
        print("BAD STEP-DEFINITIONS[%d]:" % len(self.bad_step_definitions),
              file=self.file)
        for bad_step_definition in self.bad_step_definitions:
            print("- ", end="")
            self.print(bad_step_definition, error=None, file=self.file)

    # -- CLASS METHODS:
    @classmethod
    def print(cls, step_matcher, error=None, file=None):
        message = cls.BAD_STEP_DEFINITION_MESSAGE_WITH_ERROR
        if error is None:
            message = cls.BAD_STEP_DEFINITION_MESSAGE

        print(message.format(step=step_matcher.describe(),
                             step_location=step_matcher.location,
                             error=error), file=file)


class BadStepDefinitionErrorHandler(BadStepDefinitionCollector):

    def on_error(self, step_matcher, error):
        self.bad_step_definitions.append(step_matcher)
        self.print(step_matcher, error, file=self.file)

    @classmethod
    def raise_error(cls, step_matcher, error):
        cls.print(step_matcher, error)
        raise error


class StepRegistry(object):
    BAD_STEP_DEFINITION_HANDLER_CLASS = BadStepDefinitionErrorHandler
    RAISE_ERROR_ON_BAD_STEP_DEFINITION = False

    def __init__(self):
        self.steps = dict(given=[], when=[], then=[], step=[])
        self.error_handler = self.BAD_STEP_DEFINITION_HANDLER_CLASS(file=sys.stderr)

    def clear(self):
        """
        Forget any step-definitions (step-matchers) and
        forget any bad step-definitions.
        """
        self.steps = dict(given=[], when=[], then=[], step=[])
        self.error_handler.clear()

    @staticmethod
    def same_step_definition(step, other_pattern, other_location):
        return (step.pattern == other_pattern and
                step.location == other_location and
                other_location.filename != "<string>")

    @classmethod
    def same_step_matcher(cls, step_matcher1, step_matcher2):
        return cls.same_step_definition(step_matcher1,
                                        step_matcher2.pattern,
                                        step_matcher2.location)
        # -- ALTERNATIVE:
        # return (step_matcher1.pattern == step_matcher2.pattern and
        #         step_matcher1.location == step_matcher2.location and
        #         step_matcher2.location.filename != "<string>")

    def on_bad_step_definition(self, step_matcher, error):
        # -- STEP: Select on_error() function
        on_error = self.error_handler.on_error
        if self.RAISE_ERROR_ON_BAD_STEP_DEFINITION:
            on_error = self.error_handler.raise_error

        on_error(step_matcher, error)

    def is_good_step_definition(self, step_matcher):
        """
        Check if a :param:`step_matcher` provides a good step definition.

        PROBLEM:
        * :func:`Parser.parse()` may always raise an exception
          (cases: :exc:`NotImplementedError` caused by :exc:`re.error`, ...).
        * regex errors (from :mod:`re`) are more enforced since Python >= 3.11

        :param step_matcher:  Step-matcher (step-definition) to check.
        :return: True, if step-matcher is good to use; False, otherwise.
        """
        try:
            step_matcher.compile()
            return True
        except Exception as error:
            self.on_bad_step_definition(step_matcher, error)
        return False

    def add_step_definition(self, keyword, step_text, func):
        new_step_type = keyword.lower()
        step_text = _text(step_text)
        new_step_matcher = make_step_matcher(func, step_text, new_step_type)
        if not self.is_good_step_definition(new_step_matcher):
            # -- CASE: BAD STEP-DEFINITION -- Ignore it.
            return

        # -- CURRENT:
        step_location = new_step_matcher.location
        step_definitions = self.steps[new_step_type]
        for existing in step_definitions:
            if self.same_step_matcher(existing, new_step_matcher):
                # -- EXACT-STEP: Same step function is already registered.
                # This may occur when a step module imports another one.
                return

            if existing.matches(step_text):
                # WHY: existing.step_type = new_step_type
                message = u"%s has already been defined in\n  existing step %s"
                new_step = new_step_matcher.describe()
                existing_step = existing.describe(existing.SCHEMA_AT_LOCATION)
                raise AmbiguousStep(message % (new_step, existing_step))
        step_definitions.append(new_step_matcher)

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
        """
        Creates a step decorator for this step type.

        .. versionchanged:: 1.2.7
            Support for async-step functions was added.
        """
        def decorator(step_text, **kwargs):
            def wrapper(func):
                if _FEATURE_ASYNC_FUNC and inspect.iscoroutinefunction(func):
                    func = AsyncStepFunction(func, **kwargs)
                self.add_step_definition(step_type, step_text, func)
                return func
            return wrapper
        return decorator


# -----------------------------------------------------------------------------
# MODULE DATA:
# -----------------------------------------------------------------------------
# -- STEP-DECORATOR PLACEHOLDERS (setup at end of this module):
class _StepDecorator:
    pass


registry = StepRegistry()

# -- LOWER-CASE STEP-DECORATORS:
given = _StepDecorator()
when = _StepDecorator()
then = _StepDecorator()
step = _StepDecorator()
# -- TITLE-CASE STEP-DECORATORS:
Given = _StepDecorator()
When = _StepDecorator()
Then = _StepDecorator()
Step = _StepDecorator()


# -----------------------------------------------------------------------------
# MODULE SETUP SUPPORT:
# -----------------------------------------------------------------------------
def setup_step_decorators(run_context=None, registry=registry):
    """
    Setup (and creates) the step-decorators used by step-writers.
    """
    # pylint: disable=redefined-outer-name
    if run_context is None:
        run_context = globals()
    for step_type in ("given", "when", "then", "step"):
        step_decorator = registry.make_decorator(step_type)
        run_context[step_type.title()] = run_context[step_type] = step_decorator


# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
setup_step_decorators()
