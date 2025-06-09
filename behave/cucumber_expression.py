"""
Provide a step-matcher with `cucumber-expressions`_ for :pypi:`behave`.

:STATUS: Experimental (incubating)

.. _cucumber-expressions: https://github.com/cucumber/cucumber-expressions
"""

from __future__ import absolute_import, print_function
from typing import Callable, List, Optional, Type

from behave.exception import NotSupportedWarning
from behave.matchers import (
    Matcher,
    has_registered_step_matcher_class,
    register_step_matcher_class,
    use_step_matcher
)
from behave.model_type import Argument

# -- REQUIRES: Python >= 3.8
from cucumber_expressions.expression import CucumberExpression
from cucumber_expressions.parameter_type import ParameterType
from cucumber_expressions.parameter_type_registry import ParameterTypeRegistry

from parse_type import TypeBuilder as _TypeBuilder


# -----------------------------------------------------------------------------
# STEP-MATCHER SUPPORT CLASSES FOR: CucumberExpressions
# -----------------------------------------------------------------------------
class TypeRegistry4ParameterType(object):
    """
    Provides adapter to :class:`ParameterTypeRegistry`.

    RESPONSIBILITIES:
    * Implements the "TypeRegistryProtocol"
      (used by: StepMatcherFactory/Matcher class)
    """
    REGISTRY_CLASS = ParameterTypeRegistry

    def __init__(self, parameter_types: Optional[ParameterTypeRegistry] = None):
        if parameter_types is None:
            parameter_types = self.REGISTRY_CLASS()
        self.parameter_types = parameter_types

    def define_parameter_type(self, parameter_type: ParameterType):
        self.parameter_types.define_parameter_type(parameter_type)

    def define_parameter_type_with(self, name: str, regexp: str, type: Type,
                                   transformer: Optional[Callable] = None,
                                   use_for_snippets: bool = True,
                                   prefer_for_regexp_match: bool = False):
        this_type = ParameterType(name, regexp=regexp, type=type,
                                  transformer=transformer,
                                  use_for_snippets=use_for_snippets,
                                  prefer_for_regexp_match=prefer_for_regexp_match)
        self.define_parameter_type(this_type)

    # -- IMPLEMENT: TypeRegistryProtocol
    def register_type(self, **kwargs):
        parameter_type = kwargs.pop("parameter_type", None)
        if parameter_type is None:
            raise NotSupportedWarning("Use define_parameter_type() instead")
        self.define_parameter_type(parameter_type)

    def has_registered_type(self, name):
        optional_parameter_type = self.parameter_types.lookup_by_type_name(name)
        return bool(optional_parameter_type)

    def clear(self):
        self.parameter_types = self.REGISTRY_CLASS()


class StepMatcher4CucumberExpressions(Matcher):
    """
    Provides a step-matcher class that supports `cucumber-expressions`_
    for step parameters.
    """
    NAME = "cucumber_expressions"
    TYPE_REGISTRY = TypeRegistry4ParameterType()

    def __init__(self, func: Callable, pattern: str,
                 step_type: Optional[str] = None,
                 parameter_types: Optional[ParameterTypeRegistry] = None):
        if parameter_types is None:
            parameter_types = self.TYPE_REGISTRY.parameter_types
        super(StepMatcher4CucumberExpressions, self).__init__(func, pattern,
                                                             step_type=step_type)
        self.cucumber_expression = CucumberExpression(pattern, parameter_types)

    # -- IMPLEMENT: MatcherProtocol
    @property
    def regex_pattern(self) -> str:
        return self.cucumber_expression.regexp

    def compile(self):
        # -- ENSURE: No BAD STEP-DEFINITION problem exists.
        pass

    def check_match(self, step_text: str) -> Optional[List[Argument]]:
        matched = self.cucumber_expression.match(step_text)
        if matched is None:
            # -- CASE: NO MATCH
            return None

        # -- CASE: MATCHED
        arguments = [self._make_argument(matched_item) for matched_item in matched]
        return arguments

    # -- CLASS METHODS:
    @staticmethod
    def _make_argument(matched) -> Argument:
        # -- HINT: CucumberExpressions arguments are NOT NAMED.
        return Argument(start=matched.group.start,
                        end=matched.group.end,
                        original=matched.group.value,
                        value=matched.value)


# -----------------------------------------------------------------------------
# REUSE:
# -----------------------------------------------------------------------------
class TypeBuilder(_TypeBuilder):
    """
    Provides :class:`TypeBuilder` for `CucumberExpressions`_.

    DEFINITION: parse-function (from: parse-expressions)
    * A function that converts text into a value of value-type (or raises error).
    * A "parse-function" has a pattern attribute that contains its regex pattern.

    RESPONSIBILITIES:
    * Creates a new "parse-function" and its regex pattern for a common use cases.
    * Composes a regular-expression pattern from parse-functions and their patterns.

    COLLABORATORS:
    * Uses :class:`parse_type.TypeBuilder` for "parse-expressions" for core functionality.
    """

    @staticmethod
    def _add_pattern_group_to(parse_func: Callable):
        # -- HINT: CucumberExpression needs additional grouping for regex pattern.
        new_pattern = r"(%s)" % parse_func.pattern
        parse_func.pattern = new_pattern
        return parse_func

    # -- OVERRIDE: Fix regex patterns for CucumberExpression
    @classmethod
    def make_variant(cls, converters: List[Callable], **kwargs):
        parse_variant = _TypeBuilder.make_variant(converters, **kwargs)
        return cls._add_pattern_group_to(parse_variant)

    @classmethod
    def with_many(cls, converter: Callable, pattern: Optional[str] = None,
                  listsep: str =","):
        """
        Builds parse-function for many items (cardinality: 1..N)
        based on parse-function for one item.

        :param converter:   Converter/parse-function for one item.
        :param pattern:     Regex pattern for one item (or converter.pattern).
        :param listsep:     List separator between items (as string).
        :return: Converter/parse-function with regex pattern for many items.
        """
        parse_many = _TypeBuilder.with_many(converter, pattern=pattern,
                                            listsep=listsep)
        return cls._add_pattern_group_to(parse_many)

    @classmethod
    def with_many0(cls, converter: Callable, pattern: Optional[str] = None,
                   listsep: str =","):
        """
        Builds parse-function for many items (cardinality: 0..N)
        based on parse-function for one item.

        :param converter:   Converter/parse-function for one item.
        :param pattern:     Regex pattern for one item (or converter.pattern).
        :param listsep:     List separator between items (as string).
        :return: Converter/parse-function with regex pattern for many items.
        """
        parse_many0 = _TypeBuilder.with_many0(converter, pattern=pattern,
                                              listsep=listsep)
        return cls._add_pattern_group_to(parse_many0)


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS:
# -----------------------------------------------------------------------------
def define_parameter_type(parameter_type: ParameterType) -> None:
    the_type_registry = StepMatcher4CucumberExpressions.TYPE_REGISTRY
    the_type_registry.define_parameter_type(parameter_type)


def define_parameter_type_with(name: str, regexp: str, type: Type,
                               transformer: Optional[Callable] = None,
                               use_for_snippets: bool = True,
                               prefer_for_regexp_match: bool = False):
    this_type = ParameterType(name, regexp=regexp, type=type,
                              transformer=transformer,
                              use_for_snippets=use_for_snippets,
                              prefer_for_regexp_match=prefer_for_regexp_match)
    define_parameter_type(this_type)


def use_step_matcher_for_cucumber_expressions():
    this_class = StepMatcher4CucumberExpressions
    if not has_registered_step_matcher_class(this_class.NAME):
        # -- LAZY AUTO REGISTER: On first use.
        register_step_matcher_class(this_class.NAME, this_class)

    use_step_matcher(this_class.NAME)


# -----------------------------------------------------------------------------
# MONKEY-PATCH:
# -----------------------------------------------------------------------------
def _ParameterType_repr(self):
    class_name = self.__class__.__name__
    return fr"<{class_name}: name={self.name}, pattern={self.regexp}, ...>"


# -- MONKEY-PATCH (and extend it):
ParameterType.__repr__ = _ParameterType_repr
