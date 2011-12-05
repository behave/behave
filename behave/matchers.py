from __future__ import with_statement

import re

import parse

from behave import model


class Matcher(object):
    '''Pull parameters out of step names.

    .. attribute:: string

       The match pattern attached to the step function.

    .. attribute:: func

       The step function the pattern is being attached to.
    '''
    def __init__(self, func, string):
        self.func = func
        self.string = string

    def check_match(self, step):
        '''Match me against the "step" name supplied.

        Return None if I don't match otherwise return a list of matches as
        :class:`behave.model.Argument` instances.

        The return value from this function will be converted into a
        :class:`behave.model.Match` instance by *behave*.
        '''
        raise NotImplementedError

    def match(self, step):
        result = self.check_match(step)
        if result is None:
            return None
        return model.Match(self.func, result)


class ParseMatcher(Matcher):
    custom_types = {}

    def __init__(self, func, string):
        super(ParseMatcher, self).__init__(func, string)
        self.parser = parse.compile(self.string, self.custom_types)

    def check_match(self, step):
        result = self.parser.parse(step)
        if not result:
            return None

        args = []
        for index, arg in enumerate(result.fixed):
            start, end = result.spans[index]
            args.append(model.Argument(start, end, step[start:end], arg))
        for name, arg in result.named.items():
            start, end = result.spans[name]
            args.append(model.Argument(start, end, step[start:end], arg, name))
        args.sort(key=lambda x: x.start)
        return args


def register_type(**kw):
    '''Register a custom type that will be available to "parse" for type
    conversion during matching.

    Converters should be supplied as name=callable arguments to
    ``register_type()``.

    The callable should accept a single string argument and return the
    type-converted value.
    '''
    ParseMatcher.custom_types.update(kw)


class RegexMatcher(Matcher):
    def __init__(self, func, string):
        super(RegexMatcher, self).__init__(func, string)
        self.regex = re.compile(self.string)

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
    'parse': ParseMatcher,
    're': RegexMatcher,
}

current_matcher = ParseMatcher


def step_matcher(name):
    '''Change the parameter matcher used in parsing step text.

    The change is immediate and may be performed between step definitions in
    your step implementation modules - allowing adjacent steps to use different
    matchers if necessary.

    There's two parsers available by default in *behave*:

    **parse** (the default)
       This is a `simple parser`_ that uses a format very much like the Python
       builtin ``format()``. You must use named fields which are then matched to
       your ``step()`` function arguments.
    **re**
       This uses full regular expressions to parse the clause text. You will
       need to use named groups "(?P<name>...)" to define the variables pulled
       from the text and passed to your ``step()`` function.

    You may `define your own matcher`_.

    .. _`define your own matcher`: api.html#step-parameters
    '''
    global current_matcher
    current_matcher = matcher_mapping[name]


def get_matcher(func, string):
    return current_matcher(func, string)
