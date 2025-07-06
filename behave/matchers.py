# -*- coding: UTF-8 -*-
# pylint: disable=redundant-u-string-prefix
# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
# pylint: disable=useless-object-inheritance
"""
This module provides the step matchers functionality that matches a
step definition (as text) with step-functions that implement this step.
"""

from __future__ import absolute_import, print_function, with_statement
import copy
import inspect
import re
import warnings

import six
import parse
from parse_type import cfparse

from behave.exception_util import ExceptionUtil, ChainedExceptionUtil
from behave.exception import NotSupportedWarning, ResourceExistsError
from behave.model_core import Replayable
from behave.model_type import FileLocation, Argument


# -----------------------------------------------------------------------------
# SECTION: Exceptions
# -----------------------------------------------------------------------------
class StepParseError(ValueError):
    """Exception class, used when step matching fails before a step is run.
    This is normally the case when an error occurs during the type conversion
    of step parameters.
    """

    def __init__(self, text=None, exc_cause=None):
        if not text and exc_cause:
            text = six.text_type(exc_cause)
        if exc_cause and six.PY2:
            # -- NOTE: Python2 does not show chained-exception causes.
            #    Therefore, provide some hint (see also: PEP-3134).
            cause_text = ExceptionUtil.describe(exc_cause,
                                                use_traceback=True,
                                                prefix="CAUSED-BY: ")
            text += u"\n" + cause_text

        ValueError.__init__(self, text)
        if exc_cause:
            # -- CHAINED EXCEPTION (see: PEP 3134)
            ChainedExceptionUtil.set_cause(self, exc_cause)


# -----------------------------------------------------------------------------
# SECTION: Model Elements
# -----------------------------------------------------------------------------
class Match(Replayable):
    """An parameter-matched step name extracted from a *feature file*.

    .. attribute:: func

       The step function that this match will be applied to.

    .. attribute:: arguments

       A list of :class:`~behave.model_core.Argument` instances containing the
       matched parameters from the step name.
    """
    type = "match"

    def __init__(self, func, arguments=None):
        super(Match, self).__init__()
        self.func = func
        self.arguments = arguments
        self.location = None
        if func:
            self.location = self.make_location(func)

    def __repr__(self):
        if self.func:
            func_name = self.func.__name__
        else:
            func_name = '<no function>'
        return '<Match %s, %s>' % (func_name, self.location)

    def __eq__(self, other):
        if not isinstance(other, Match):
            return False
        return (self.func, self.location) == (other.func, other.location)

    def with_arguments(self, arguments):
        match = copy.copy(self)
        match.arguments = arguments
        return match

    def run(self, context):
        args = []
        kwargs = {}
        for arg in self.arguments:
            if arg.name is not None:
                kwargs[arg.name] = arg.value
            else:
                args.append(arg.value)

        with context.use_with_user_mode():
            self.func(context, *args, **kwargs)

    @staticmethod
    def make_location(step_function):
        """Extracts the location information from the step function and
        builds a FileLocation object with (filename, line_number) info.

        :param step_function: Function whose location should be determined.
        :return: FileLocation object for step function.
        """
        return FileLocation.for_function(step_function)


class NoMatch(Match):
    """Used for an "undefined step" when it can not be matched with a
    step definition.
    """

    def __init__(self):
        Match.__init__(self, func=None)
        self.func = None
        self.arguments = []
        self.location = None


class MatchWithError(Match):
    """Match class when error occur during step-matching

    REASON:
      * Type conversion error occurred.
      * ...
    """
    def __init__(self, func, error):
        if not ExceptionUtil.has_traceback(error):
            ExceptionUtil.set_traceback(error)
        Match.__init__(self, func=func)
        self.stored_error = error

    def run(self, context):
        """Raises stored error from step matching phase (type conversion)."""
        raise StepParseError(exc_cause=self.stored_error)


# -----------------------------------------------------------------------------
# SECTION: TypeRegistry for Step Matchers (provide: TypeRegistry protocol)
# -----------------------------------------------------------------------------
# from typing import Protocol, ParamSpec
# from abc import abstractmethod
# P = ParamSpec("P")
#
# class TypeRegistryProtocol(Protocol):
#     @abstractmethod
#     def register_type(self, **kwargs: P.kwargs) -> None:
#         ...
#
#     @abstractmethod
#     def has_type(self, name: str) -> bool:
#         return False
#
#     def clear(self) -> None:
#         ...
#
#
class TypeRegistry(dict):
    # -- IMPLEMENTS: TypeRegistryProtocol and dict-Protocol

    def register_type(self, **kwargs):
        """
        Register one (or more) user-defined types used for matching types
        in step patterns of this matcher.
        """
        self.update(**kwargs)

    def has_type(self, name):
        return name in self


class TypeRegistryNotSupported():
    """
    Placeholder class for a type-registry if custom types are not supported.
    """
    # -- IMPLEMENTS: TypeRegistryProtocol
    def register_type(self, **kwargs):
        raise NotSupportedWarning("register_type")

    def has_type(self, name):
        return False

    def clear(self):
        pass


# -----------------------------------------------------------------------------
# SECTION: Step Matchers
# -----------------------------------------------------------------------------
class Matcher(object):
    """
    Provides an abstract base class for step-matcher classes.

    Matches steps from ``*.feature`` files (Gherkin files)
    and extracts step-parameters for these steps.

    RESPONSIBILITIES:

    * Matches steps from ``*.feature`` files (or not)
    * Returns :class:`Match` objects if this step-matcher matches
      that is used to run the step-definition function w/ its parameters.
    * Compile parse-expression/regular-expression to detect
      BAD STEP-DEFINITION(s) early.

    .. attribute:: pattern

        The match pattern attached to the step function.

    .. attribute:: func

        The associated step-definition function to use for this pattern.

    .. attribute:: location

        File location of the step-definition function.
    """
    NAME = None  # -- HINT: Must be specified by derived class.
    TYPE_REGISTRY = TypeRegistryNotSupported()

    # -- DESCRIBE-SCHEMA FOR STEP-DEFINITIONS (step-matchers):
    SCHEMA = u"@{this.step_type}('{this.pattern}')"
    SCHEMA_AT_LOCATION = SCHEMA + u" at {this.location}"
    SCHEMA_WITH_LOCATION = SCHEMA + u"  # {this.location}"
    SCHEMA_AS_STEP = u"{this.step_type} {this.pattern}"

    # -- IMPLEMENT ADAPTER FOR: TypeRegistry protocol
    @classmethod
    def register_type(cls, **kwargs):
        """Register one (or more) user-defined types used for matching types
        in step patterns of this matcher.
        """
        try:
            cls.TYPE_REGISTRY.register_type(**kwargs)
        except NotSupportedWarning:
            # -- HINT: Provide DERIVED_CLASS name as failure context.
            message = "{cls.__name__}.register_type".format(cls=cls)
            raise NotSupportedWarning(message)

    @classmethod
    def has_registered_type(cls, name):
        return cls.TYPE_REGISTRY.has_type(name)

    @classmethod
    def clear_registered_types(cls):
        cls.TYPE_REGISTRY.clear()
    # -- END-OF: TypeRegistry protocol

    def __init__(self, func, pattern, step_type=None):
        self.func = func
        self.pattern = pattern
        self.step_type = step_type or "step"
        self._location = None

    # -- BACKWARD-COMPATIBILITY:
    @property
    def string(self):
        warnings.warn("deprecated: Use 'pattern' instead", DeprecationWarning)
        return self.pattern

    @property
    def location(self):
        if self._location is None:
            self._location = Match.make_location(self.func)
        return self._location

    @property
    def regex_pattern(self):
        """Return the used textual regex pattern."""
        # -- ASSUMPTION: pattern attribute provides regex-pattern
        # NOTE: Method must be overridden if assumption is not met.
        return self.pattern

    def describe(self, schema=None):
        """Provide a textual description of the step function/matcher object.

        :param schema:  Text schema to use.
        :return: Textual description of this step definition (matcher).
        """
        if not schema:
            schema = self.SCHEMA

        # -- SUPPORT: schema = "{this.step_type} {this.pattern}"
        return schema.format(this=self)

    def compile(self):
        """
        Compiles the regular-expression pattern (if necessary).

        NOTES:
        - This allows to detect some errors with BAD regular expressions early.
        - Must be implemneted by derived classes.

        :return: Self (to support daisy-chaining)
        """
        raise NotImplementedError()

    def check_match(self, step_text):
        """
        Match me against the supplied "step_text".

        Return None, if I don't match otherwise return a list of matches as
        :class:`~behave.model_core.Argument` instances.

        The return value from this function will be converted into a
        :class:`~behave.matchers.Match` instance by *behave*.

        :param step_text: Step text that should be matched (as string).
        :return: A list of matched-arguments (on match). None, on mismatch.
        :raises: ValueError, re.error, ...
        """
        raise NotImplementedError()

    def match(self, step_text):
        # -- PROTECT AGAINST: Type conversion errors (with ParseMatcher).
        try:
            matched_args = self.check_match(step_text)
        # MAYBE: except (StepParseError, ValueError, TypeError) as e:
        except NotImplementedError:
            # -- CASES:
            # - check_match() is not implemented
            # - check_match() raises NotImplementedError (on: re.error)
            raise
        except Exception as e:
            # -- TYPE-CONVERTER ERROR occurred.
            return MatchWithError(self.func, e)

        if matched_args is None:
            return None     # -- NO-MATCH
        return Match(self.func, matched_args)

    def matches(self, step_text):
        """
        Checks if ``step_text`` parameter matches this step-definition (step-matcher).

        :param step_text: Step text to check.
        :return: True, if step is matched. False, otherwise.
        """
        if self.pattern == step_text:
            # -- SIMPLISTIC CASE: No step-parameters.
            return True

        # -- HINT: Ignore MatchWithError here.
        matched = self.match(step_text)
        return (matched and isinstance(matched, Match) and
                not isinstance(matched, MatchWithError))

    def __repr__(self):
        return u"<%s: %r>" % (self.__class__.__name__, self.pattern)


class ParseMatcher(Matcher):
    r"""
    Provides a step-matcher that uses parse-expressions.
    Parse-expressions provide a simpler syntax compared to regular expressions.
    Parse-expressions are :func:`string.format()` expressions but for parsing.

    RESPONSIBILITIES:

    * Provides parse-expressions, like: "a positive number {number:PositiveNumber}"
    * Support for custom type-converter functions

    COLLABORATORS:

    * :class:`~parse.Parser` to support parse-expressions.

    EXAMPLE:

    .. code-block:: python

        from behave import register_type, given, use_step_matcher
        import parse

        # -- TYPE CONVERTER: For a simple, positive integer number.
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        register_type(Number=parse_number)

        @given('{amount:Number} vehicles')
        def step_given_amount_vehicles(ctx, amount):
            assert isinstance(amount, int)
            print("{amount} vehicles".format(amount=amount))}
    """
    NAME = "parse"
    PARSER_CLASS = parse.Parser
    CASE_SENSITIVE = True
    TYPE_REGISTRY = TypeRegistry()

    def __init__(self, func, pattern, step_type=None, custom_types=None):
        if custom_types is None:
            custom_types = self.TYPE_REGISTRY
        super(ParseMatcher, self).__init__(func, pattern, step_type)
        self.parser = self.PARSER_CLASS(pattern, extra_types=custom_types,
                                        case_sensitive=self.CASE_SENSITIVE)

    @property
    def regex_pattern(self):
        # -- OVERWRITTEN: Pattern as regex text.
        return self.parser._expression  # pylint: disable=protected-access

    def compile(self):
        """
        Compiles internal regular-expression.

        Compiles "parser._match_re" which may lead to error (always)
        if a BAD regular expression is used (or: BAD TYPE-CONVERTER).
        """
        # -- HINT: Triggers implicit compile of "self.parser._match_re"
        _ = self.parser.parse("")
        return self

    def check_match(self, step_text):
        """
        Checks if the ``step_text`` parameter is matched (or not).

        :param step_text: Step text to check.
        :return: step-args if step was matched, None otherwise.
        :raises ValueError: If type-converter functions fails.
        """
        # -- FAILURE-POINT: Type conversion of parameters may fail here.
        #    NOTE: Type converter should raise ValueError in case of PARSE ERRORS.
        matched = self.parser.parse(step_text)
        if not matched:
            return None

        args = []
        for index, value in enumerate(matched.fixed):
            start, end = matched.spans[index]
            args.append(Argument(start, end, step_text[start:end], value))
        for name, value in matched.named.items():
            start, end = matched.spans[name]
            args.append(Argument(start, end, step_text[start:end], value, name))
        args.sort(key=lambda x: x.start)
        return args


class CFParseMatcher(ParseMatcher):
    """
    Provides a step-matcher that uses parse-expressions with cardinality-fields.
    Parse-expressions use simpler syntax compared to normal regular expressions.

    Cardinality-fields provide a compact syntax for cardinalities:

    * many:  "+" (cardinality: ``1..N``)
    * many0: "*" (cardinality: ``0..N``)
    * optional: "?" (cardinality: ``0..1``)

    Regular expressions and type-converters for cardinality-fields are
    generated by the parser if a type-converter for the cardinality=1 is registered.

    COLLABORATORS:

    * :class:`~parse_type.cfparse.Parser` is used to support parse-expressions
      with cardinality-field support.

    EXAMPLE:

    .. code-block:: python

        from behave import register_type, given, use_step_matcher
        use_step_matcher("cfparse")
        # ... -- OMITTED: Provide type-converter function for Number

        @given(u'{amount:Number+} as numbers')  # CARDINALITY-FIELD: Many-Numbers
        def step_many_numbers(ctx, numbers):
            assert isinstance(numbers, list)
            assert isinstance(numbers[0], int)
            print("numbers = %r" % numbers)

        step_matcher = CFParseMatcher(step_many_numbers, "{amount:Number+} as numbers")
        matched = step_matcher.matches("1, 2, 3 as numbers")
        assert matched is True
        # -- STEP MATCHES: numbers = [1, 2, 3]
    """
    NAME = "cfparse"
    PARSER_CLASS = cfparse.Parser


class RegexMatcher(Matcher):
    """
    Provides a step-matcher that uses regular-expressions

    RESPONSIBILITIES:

    * Custom type-converters are NOT SUPPORTED.
    """
    NAME = "re0"
    TYPE_REGISTRY = TypeRegistryNotSupported()

    def __init__(self, func, pattern, step_type=None):
        super(RegexMatcher, self).__init__(func, pattern, step_type)
        self._regex = None  # -- HINT: Defer re.compile(self.pattern)

    @property
    def regex(self):
        if self._regex is None:
            # self._regex = re.compile(self.pattern)
            self._regex = re.compile(self.pattern, re.UNICODE)
        return self._regex

    @regex.setter
    def regex(self, value):
        self._regex = value

    @property
    def regex_pattern(self):
        """Return the regex pattern that is used for matching steps."""
        return self.regex.pattern

    def compile(self):
        # -- HINT: Compiles "parser._match_re" which may lead to error (always).
        _ = self.regex  # -- HINT: IMPLICIT-COMPILE
        return self

    def check_match(self, step_text):
        matched = self.regex.match(step_text)
        if not matched:
            return None

        group_index = dict((y, x) for x, y in self.regex.groupindex.items())
        args = []
        for index, group in enumerate(matched.groups()):
            index += 1
            name = group_index.get(index, None)
            args.append(Argument(matched.start(index), matched.end(index),
                                 group, group, name))

        return args


class SimplifiedRegexMatcher(RegexMatcher):
    """
    Simplified regular expression step-matcher that automatically adds
    START_OF_LINE/END_OF_LINE regular-expression markers to the string.

    EXAMPLE:

    .. code-block:: python

        from behave import when, use_step_matcher
        use_step_matcher("re")

        @when(u'a step passes')  # re.pattern = "^a step passes$"
        def step_impl(context):
            pass
    """
    NAME = "re"

    def __init__(self, func, pattern, step_type=None):
        if pattern.startswith("^") or pattern.endswith("$"):
            msg = "Regular expression should not use begin/end-markers: " + pattern
            raise ValueError(msg)

        expression = r"^%s$" % pattern
        super(SimplifiedRegexMatcher, self).__init__(func, expression, step_type)


class CucumberRegexMatcher(RegexMatcher):
    """
    Compatible to (old) Cucumber style regular expressions.
    Step-text must contain START_OF_LINE/END_OF_LINE markers.

    EXAMPLE:

    .. code-block:: python

        from behave import when, use_step_matcher
        use_step_matcher("re0")

        @when(u'^a step passes$')   # re.pattern = "^a step passes$"
        def step_impl(context): pass
    """
    NAME = "re0"


# -----------------------------------------------------------------------------
# STEP MATCHER FACTORY (for public API)
# -----------------------------------------------------------------------------
class StepMatcherFactory(object):
    """
    This class provides functionality for the public API of step-matchers.

    It allows to  change the step-matcher class in use
    while parsing step definitions.
    This allows to use multiple step-matcher classes:

    * in the same steps module
    * in different step modules

    There are several step-matcher classes available in **behave**:

    * **parse** (the default, based on: :pypi:`parse`):
    * **cfparse** (extends: :pypi:`parse`, requires: :pypi:`parse_type`)
    * **re** (using regular expressions)

    You may `define your own step-matcher class`_.

    .. _`define your own step-matcher class`: api.html#step-parameters

    parse
    ------

    Provides a simple parser that replaces regular expressions for
    step parameters with a readable syntax like ``{param:Type}``.
    The syntax is inspired by the Python builtin ``string.format()`` function.
    Step parameters must use the named fields syntax of :pypi:`parse`
    in step definitions. The named fields are extracted,
    optionally type converted and then used as step function arguments.

    Supports type conversions by using type converters
    (see :func:`~behave.register_type()`).

    cfparse
    -------

    Provides an extended parser with "Cardinality Field" (CF) support.
    Automatically creates missing type converters for related cardinality
    as long as a type converter for cardinality=1 is provided.
    Supports parse expressions like:

    * ``{values:Type+}`` (cardinality=1..N, many)
    * ``{values:Type*}`` (cardinality=0..N, many0)
    * ``{value:Type?}``  (cardinality=0..1, optional)

    Supports type conversions (as above).

    re (regex based parser)
    -----------------------

    This uses full regular expressions to parse the clause text. You will
    need to use named groups "(?P<name>...)" to define the variables pulled
    from the text and passed to your ``step()`` function.

    Type conversion is **not supported**.
    A step function writer may implement type conversion
    inside the step function (implementation).
    """
    STEP_MATCHER_CLASSES = [
        ParseMatcher,
        CFParseMatcher,
        SimplifiedRegexMatcher,
        CucumberRegexMatcher,  # -- SAME AS: RegexMatcher
    ]
    DEFAULT_MATCHER_NAME = "parse"

    @classmethod
    def make_step_matcher_class_mapping(cls, step_matcher_classes=None):
        if step_matcher_classes is None:
            step_matcher_classes = cls.STEP_MATCHER_CLASSES
        # -- USING: dict-comprehension
        return {step_matcher_class.NAME: step_matcher_class
                for step_matcher_class in step_matcher_classes}

    def __init__(self, step_matcher_class_mapping=None, default_matcher_name=None):
        if step_matcher_class_mapping is None:
            step_matcher_class_mapping = self.make_step_matcher_class_mapping()
        if default_matcher_name is None:
            default_matcher_name = self.DEFAULT_MATCHER_NAME

        assert default_matcher_name in step_matcher_class_mapping
        self.step_matcher_class_mapping = step_matcher_class_mapping
        self.initial_matcher_name = default_matcher_name
        self.default_matcher_name = default_matcher_name
        self.default_matcher = self.step_matcher_class_mapping[default_matcher_name]
        self._current_matcher = self.default_matcher
        assert self.default_matcher in self.step_matcher_class_mapping.values()

    def reset(self):
        self.use_default_step_matcher(self.initial_matcher_name)
        self.clear_registered_types()

    @property
    def current_matcher(self):
        # -- ENSURE: READ-ONLY access
        return self._current_matcher

    def register_type(self, **kwargs):
        """
        Registers one (or more) custom type that will be available
        by some matcher classes, like the :class:`ParseMatcher` and its
        derived classes, for type conversion during step matching.

        Converters should be supplied as ``name=callable`` arguments (or as dict).
        A type converter should follow the rules of its :class:`Matcher` class.
        """
        self.current_matcher.register_type(**kwargs)

    def has_registered_type(self, name):
        return self.current_matcher.has_registered_type(name)

    def clear_registered_types(self):
        for step_matcher_class in self.step_matcher_class_mapping.values():
            step_matcher_class.clear_registered_types()

    def register_step_matcher_class(self, name, step_matcher_class,
                                    override=False):
        """Register a new step-matcher class to use.

        :param name:  Name of the step-matcher to use.
        :param step_matcher_class:  Step-matcher class.
        :param override:  Use ``True`` to override any existing step-matcher class.
        """
        if not inspect.isclass(step_matcher_class):
            raise TypeError("%r is not a class" % step_matcher_class)
        if not issubclass(step_matcher_class, Matcher):
            raise TypeError("%r is not subclass-of:Matcher" % step_matcher_class)

        known_class = self.step_matcher_class_mapping.get(name, None)
        if (not override and
            known_class is not None and known_class is not step_matcher_class):
            message = "ALREADY REGISTERED: {name}={class_name}".format(
                name=name, class_name=known_class.__name__)
            raise ResourceExistsError(message)

        self.step_matcher_class_mapping[name] = step_matcher_class

    def use_step_matcher(self, name):
        """
        Changes the step-matcher class to use while parsing step definitions.
        This allows to use multiple step-matcher classes:

        * in the same steps module
        * in different step modules

        There are several step-matcher classes available in **behave**:

        * **parse** (the default, based on: :pypi:`parse`):
        * **cfparse** (extends: :pypi:`parse`, requires: :pypi:`parse_type`)
        * **re** (using regular expressions)

        :param name:  Name of the step-matcher class.
        :return: Current step-matcher class that is now in use.
        """
        self._current_matcher = self.step_matcher_class_mapping[name]
        return self._current_matcher

    def use_default_step_matcher(self, name=None):
        """Use the default step-matcher.

        If ``name`` argument is provided, this name is used to define this
        step-matcher as the new default step-matcher.

        :param name:    Optional, use it to specify the default step-matcher.
        :return: Current step-matcher class (or object).
        """
        if name:
            self.default_matcher = self.step_matcher_class_mapping[name]
            self.default_matcher_name = name
        self._current_matcher = self.default_matcher
        return self._current_matcher

    def use_current_step_matcher_as_default(self):
        self.default_matcher = self._current_matcher

    def make_step_matcher(self, func, step_text, step_type=None):
        return self.current_matcher(func, step_text, step_type=step_type)

    # -- BACKWARD-COMPATIBILITY:
    def make_matcher(self, func, step_text, step_type=None):
        warnings.warn("DEPRECATED: Use make_step_matchers() instead.", DeprecationWarning)
        return self.make_step_matcher(func, step_text, step_type=step_type)


# -- MODULE INSTANCE:
_the_step_matcher_factory = StepMatcherFactory()


# -----------------------------------------------------------------------------
# API FUNCTIONS:
# -----------------------------------------------------------------------------
def get_step_matcher_factory():
    return _the_step_matcher_factory


def make_step_matcher(func, step_text, step_type=None):
    return _the_step_matcher_factory.make_step_matcher(func, step_text,
                                                       step_type=step_type)


def use_current_step_matcher_as_default():
    return _the_step_matcher_factory.use_current_step_matcher_as_default()


# -----------------------------------------------------------------------------
# PUBLIC API FOR: step-writers
# -----------------------------------------------------------------------------
def use_step_matcher(name):
    return _the_step_matcher_factory.use_step_matcher(name)


def use_default_step_matcher(name=None):
    return _the_step_matcher_factory.use_default_step_matcher(name=name)


def register_type(**kwargs):
    _the_step_matcher_factory.register_type(**kwargs)


# -- REUSE DOCSTRINGS:
register_type.__doc__ = StepMatcherFactory.register_type.__doc__
use_step_matcher.__doc__ = StepMatcherFactory.use_step_matcher.__doc__
use_default_step_matcher.__doc__ = (
    StepMatcherFactory.use_default_step_matcher.__doc__)


# -----------------------------------------------------------------------------
# BEHAVE EXTENSION-POINT: Add your own step-matcher class(es)
# -----------------------------------------------------------------------------
def register_step_matcher_class(name, step_matcher_class, override=False):
    _the_step_matcher_factory.register_step_matcher_class(name, step_matcher_class,
                                                          override=override)


def has_registered_step_matcher_class(name_or_class):
    """
    Indicates if a ``step_matcher_class`` is already registered or not.

    This supports to auto-register a ``step_matcher_class`` when it is first used.

    EXAMPLE::

        # -- FILE: cuke4behave/__init__.py
        from behave.matchers import (Matcher,
            has_registered_step_matcher_class,
            register_step_matcher_class,
            use_step_matcher
        )

        class CucumberExpressionsStepMatcher(Matcher):
            NAME = "cucumber_expressions"
            ...

        def use_step_matcher_for_cucumber_expressions():
            this_class = CucumberExpressionsStepMatcher
            if not has_registered_step_matcher_class(this_class.NAME):
                # -- AUTO-REGISTER: On first use of this step-matcher-class
                register_step_matcher_class(this_class.NAME, the_class)
            use_step_matcher(this_class.NAME)

        # -- FILE: features/steps/example_steps.py
        from behave import given, when then
        from cuke4behave import use_step_matcher_for_cucumber_expressions

        use_step_matcher_for_cucumber_expressions()

        @given('a person named {string}')
        def step_given_a_person_named(ctx, name):
            pass
    """
    step_matcher_class_mapping = _the_step_matcher_factory.step_matcher_class_mapping
    if isinstance(name_or_class, six.string_types):
        name = name_or_class
        return name in step_matcher_class_mapping
    if not inspect.isclass(name_or_class):
        raise TypeError("%r (expected: string, class" % name_or_class)

    # -- CASE 2: Check if step_matcher_class is registered.
    step_matcher_class = name_or_class
    return step_matcher_class in step_matcher_class_mapping.values()


# -- REUSE DOCSTRINGS:
register_step_matcher_class.__doc__ = (
    StepMatcherFactory.register_step_matcher_class.__doc__)


# -----------------------------------------------------------------------------
# BACKWARD-COMPATIBILITY:
# -----------------------------------------------------------------------------
def get_matcher_factory():
    warnings.warn("DEPRECATED: Use get_step_matcher_factory() instead", DeprecationWarning)
    return get_step_matcher_factory()


def make_matcher(func, step_text, step_type=None):
    warnings.warn("DEPRECATED: Use make_step_matcher() instead", DeprecationWarning)
    return make_step_matcher(func, step_text, step_type=step_type)
