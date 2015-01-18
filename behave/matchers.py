from __future__ import absolute_import, with_statement

import re
import parse
from parse_type import cfparse
from behave import model


class Matcher(object):
    """Pull parameters out of step names.

    .. attribute:: string

       The match pattern attached to the step function.

    .. attribute:: func

       The step function the pattern is being attached to.
    """
    schema = u"@%s('%s')"   # Schema used to describe step definition (matcher)

    def __init__(self, func, string, step_type=None):
        self.func = func
        self.string = string
        self.step_type = step_type
        self._location = None

    @property
    def location(self):
        if self._location is None:
            self._location = model.Match.make_location(self.func)
        return self._location

    def describe(self, schema=None):
        """Provide a textual description of the step function/matcher object.

        :param schema:  Text schema to use.
        :return: Textual description of this step definition (matcher).
        """
        step_type = self.step_type or 'step'
        if not schema:
            schema = self.schema
        return schema % (step_type, self.string)


    def check_match(self, step):
        """Match me against the "step" name supplied.

        Return None if I don't match otherwise return a list of matches as
        :class:`behave.model.Argument` instances.

        The return value from this function will be converted into a
        :class:`behave.model.Match` instance by *behave*.
        """
        raise NotImplementedError

    def match(self, step):
        result = self.check_match(step)
        if result is None:
            return None
        return model.Match(self.func, result)

    def __repr__(self):
        return u"<%s: %r>" % (self.__class__.__name__, self.string)


class ParseMatcher(Matcher):
    custom_types = {}

    def __init__(self, func, string, step_type=None):
        super(ParseMatcher, self).__init__(func, string, step_type)
        self.parser = parse.compile(self.string, self.custom_types)

    def check_match(self, step):
        result = self.parser.parse(step)
        if not result:
            return None

        args = []
        for index, value in enumerate(result.fixed):
            start, end = result.spans[index]
            args.append(model.Argument(start, end, step[start:end], value))
        for name, value in result.named.items():
            start, end = result.spans[name]
            args.append(model.Argument(start, end, step[start:end], value, name))
        args.sort(key=lambda x: x.start)
        return args

class CFParseMatcher(ParseMatcher):
    """
    Uses :class:`parse_type.cfparse.Parser` instead of "parse.Parser".
    Provides support for automatic generation of type variants
    for fields with CardinalityField part.
    """
    def __init__(self, func, string, step_type=None):
        super(ParseMatcher, self).__init__(func, string, step_type)
        self.parser = cfparse.Parser(self.string, self.custom_types)


def register_type(**kw):
    """Registers a custom type that will be available to "parse"
    for type conversion during step matching.

    Converters should be supplied as ``name=callable`` arguments (or as dict).

    A type converter should follow :pypi:`parse` module rules.
    In general, a type converter is a function that converts text (as string)
    into a value-type (type converted value).

    EXAMPLE:

    .. code-block:: python

        from behave import register_type, given
        import parse

        # -- TYPE CONVERTER: For a simple, positive integer number.
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        # -- REGISTER TYPE-CONVERTER: With behave
        register_type(Number=parse_number)

        # -- STEP DEFINITIONS: Use type converter.
        @given('{amount:Number} vehicles')
        def step_impl(context, amount):
            assert isinstance(amount, int)
    """
    ParseMatcher.custom_types.update(kw)


class RegexMatcher(Matcher):
    def __init__(self, func, string, step_type=None):
        super(RegexMatcher, self).__init__(func, string, step_type)
        assert not (string.startswith("^") or string.endswith("$")), \
            "Regular expression should not use begin/end-markers: "+ string
        expression = "^%s$" % self.string
        self.regex = re.compile(expression)

    def check_match(self, step):
        m = self.regex.match(step)
        if not m:
            return None

        groupindex = dict((y, x) for x, y in self.regex.groupindex.items())
        args = []
        for index, group in enumerate(m.groups()):
            index += 1
            name = groupindex.get(index, None)
            args.append(model.Argument(m.start(index), m.end(index), group,
                                       group, name))

        return args


matcher_mapping = {
    "parse": ParseMatcher,
    "cfparse": CFParseMatcher,
    "re": RegexMatcher,
}
current_matcher = ParseMatcher


def use_step_matcher(name):
    """Change the parameter matcher used in parsing step text.

    The change is immediate and may be performed between step definitions in
    your step implementation modules - allowing adjacent steps to use different
    matchers if necessary.

    There are several parsers available in *behave* (by default):

    **parse** (the default, based on: :pypi:`parse`)
        Provides a simple parser that replaces regular expressions for
        step parameters with a readable syntax like ``{param:Type}``.
        The syntax is inspired by the Python builtin ``string.format()``
        function.
        Step parameters must use the named fields syntax of :pypi:`parse`
        in step definitions. The named fields are extracted,
        optionally type converted and then used as step function arguments.

        Supports type conversions by using type converters
        (see :func:`~behave.register_type()`).

    **cfparse** (extends: :pypi:`parse`, requires: :pypi:`parse_type`)
        Provides an extended parser with "Cardinality Field" (CF) support.
        Automatically creates missing type converters for related cardinality
        as long as a type converter for cardinality=1 is provided.
        Supports parse expressions like:

            * ``{values:Type+}`` (cardinality=1..N, many)
            * ``{values:Type*}`` (cardinality=0..N, many0)
            * ``{value:Type?}``  (cardinality=0..1, optional)

        Supports type conversions (as above).

    **re**
        This uses full regular expressions to parse the clause text. You will
        need to use named groups "(?P<name>...)" to define the variables pulled
        from the text and passed to your ``step()`` function.

        Type conversion is **not supported**.
        A step function writer may implement type conversion
        inside the step function (implementation).

    You may `define your own matcher`_.

    .. _`define your own matcher`: api.html#step-parameters
    """
    global current_matcher
    current_matcher = matcher_mapping[name]

def step_matcher(name):
    """
    DEPRECATED, use :func:`use_step_matcher()` instead.
    """
    # -- BACKWARD-COMPATIBLE NAME: Mark as deprecated.
    import warnings
    warnings.warn("Use 'use_step_matcher()' instead",
                  PendingDeprecationWarning, stacklevel=2)
    use_step_matcher(name)

def get_matcher(func, string):
    return current_matcher(func, string)


