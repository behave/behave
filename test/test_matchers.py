from __future__ import with_statement

from mock import Mock, patch
from nose.tools import *
import parse

from behave import matchers, model, runner

class DummyMatcher(matchers.Matcher):
    desired_result = None

    def check_match(self, step):
        return DummyMatcher.desired_result

class TestMatcher(object):
    def setUp(self):
        DummyMatcher.desired_result = None

    def test_returns_none_if_check_match_returns_none(self):
        matcher = DummyMatcher(None, None)
        assert matcher.match('just a random step') is None

    def test_returns_match_object_if_check_match_returns_arguments(self):
        arguments = ['some', 'random', 'objects']
        func = lambda x: -x

        DummyMatcher.desired_result = arguments
        matcher = DummyMatcher(func, None)

        match = matcher.match('just a random step')
        assert isinstance(match, model.Match)
        assert match.func is func
        assert match.arguments == arguments

class TestParseMatcher(object):
    def setUp(self):
        self.recorded_args = None

    def record_args(self, *args, **kwargs):
        self.recorded_args = (args, kwargs)

    def test_returns_none_if_parser_does_not_match(self):
        matcher = matchers.ParseMatcher(None, 'a string')
        with patch.object(matcher.parser, 'parse') as parse:
            parse.return_value = None
            assert matcher.match('just a random step') is None

    def test_returns_arguments_based_on_matches(self):
        func = lambda x: -x
        matcher = matchers.ParseMatcher(func, 'foo')

        results = parse.Result([1, 2, 3], {'foo': 'bar', 'baz': -45.3},
                               {
                                   0: (13, 14),
                                   1: (16, 17),
                                   2: (22, 23),
                                   'foo': (32, 35),
                                   'baz': (39, 44),
                               })

        expected = [
            (13, 14, '1', 1, None),
            (16, 17, '2', 2, None),
            (22, 23, '3', 3, None),
            (32, 35, 'bar', 'bar', 'foo'),
            (39, 44, '-45.3', -45.3, 'baz'),
        ]

        with patch.object(matcher.parser, 'parse') as p:
            p.return_value = results
            m = matcher.match('some numbers 1, 2 and 3 and the bar is -45.3')
            assert m.func is func
            args = m.arguments
            have = [(a.start, a.end, a.original, a.value, a.name) for a in args]
            eq_(have, expected)

    def test_named_arguments(self):
        text = "has a {string}, an {integer:d} and a {decimal:f}"
        matcher = matchers.ParseMatcher(self.record_args, text)
        context = runner.Context(Mock())

        m = matcher.match("has a foo, an 11 and a 3.14159")
        m.run(context)
        eq_(self.recorded_args, ((context,), {
            'string': 'foo',
            'integer': 11,
            'decimal': 3.14159
        }))

    def test_positional_arguments(self):
        text = "has a {}, an {:d} and a {:f}"
        matcher = matchers.ParseMatcher(self.record_args, text)
        context = runner.Context(Mock())

        m = matcher.match("has a foo, an 11 and a 3.14159")
        m.run(context)
        eq_(self.recorded_args, ((context, 'foo', 11, 3.14159), {}))

class TestRegexMatcher(object):
    def test_returns_none_if_regex_does_not_match(self):
        matcher = matchers.RegexMatcher(None, 'a string')
        regex = Mock()
        regex.match.return_value = None
        matcher.regex = regex
        assert matcher.match('just a random step') is None

    def test_returns_arguments_based_on_groups(self):
        func = lambda x: -x
        matcher = matchers.RegexMatcher(func, 'foo')

        regex = Mock()
        regex.groupindex = {'foo': 4, 'baz': 5}

        match = Mock()
        match.groups.return_value = ('1', '2', '3', 'bar', '-45.3')
        positions = {
            1: (13, 14),
            2: (16, 17),
            3: (22, 23),
            4: (32, 35),
            5: (39, 44),
        }
        match.start.side_effect = lambda idx: positions[idx][0]
        match.end.side_effect = lambda idx: positions[idx][1]

        regex.match.return_value = match
        matcher.regex = regex

        expected = [
            (13, 14, '1', '1', None),
            (16, 17, '2', '2', None),
            (22, 23, '3', '3', None),
            (32, 35, 'bar', 'bar', 'foo'),
            (39, 44, '-45.3', '-45.3', 'baz'),
        ]

        m = matcher.match('some numbers 1, 2 and 3 and the bar is -45.3')
        assert m.func is func
        args = m.arguments
        have = [(a.start, a.end, a.original, a.value, a.name) for a in args]
        eq_(have, expected)

def test_step_matcher_current_matcher():
    current_matcher = matchers.current_matcher

    for name, klass in matchers.matcher_mapping.items():
        matchers.step_matcher(name)
        matcher = matchers.get_matcher(lambda x: -x, 'foo')
        assert isinstance(matcher, klass)

    matchers.current_matcher = current_matcher
