# -*- coding: UTF-8 -*-
from __future__ import absolute_import, with_statement
from mock import Mock, patch
from nose.tools import *  # pylint: disable=wildcard-import, unused-wildcard-import
import parse
from behave.matchers import Match, Matcher, ParseMatcher, RegexMatcher, \
    SimplifiedRegexMatcher, CucumberRegexMatcher
from behave import matchers, runner


class DummyMatcher(Matcher):
    desired_result = None

    def check_match(self, step):
        return DummyMatcher.desired_result

class TestMatcher(object):
    # pylint: disable=invalid-name, no-self-use

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
        assert isinstance(match, Match)
        assert match.func is func
        assert match.arguments == arguments

class TestParseMatcher(object):
    # pylint: disable=invalid-name, no-self-use

    def setUp(self):
        self.recorded_args = None

    def record_args(self, *args, **kwargs):
        self.recorded_args = (args, kwargs)

    def test_returns_none_if_parser_does_not_match(self):
        # pylint: disable=redefined-outer-name
        # REASON: parse
        matcher = ParseMatcher(None, 'a string')
        with patch.object(matcher.parser, 'parse') as parse:
            parse.return_value = None
            assert matcher.match('just a random step') is None

    def test_returns_arguments_based_on_matches(self):
        func = lambda x: -x
        matcher = ParseMatcher(func, 'foo')

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
        matcher = ParseMatcher(self.record_args, text)
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
        matcher = ParseMatcher(self.record_args, text)
        context = runner.Context(Mock())

        m = matcher.match("has a foo, an 11 and a 3.14159")
        m.run(context)
        eq_(self.recorded_args, ((context, 'foo', 11, 3.14159), {}))

class TestRegexMatcher(object):
    # pylint: disable=invalid-name, no-self-use
    MATCHER_CLASS = RegexMatcher

    def test_returns_none_if_regex_does_not_match(self):
        RegexMatcher = self.MATCHER_CLASS
        matcher = RegexMatcher(None, 'a string')
        regex = Mock()
        regex.match.return_value = None
        matcher.regex = regex
        assert matcher.match('just a random step') is None

    def test_returns_arguments_based_on_groups(self):
        RegexMatcher = self.MATCHER_CLASS
        func = lambda x: -x
        matcher = RegexMatcher(func, 'foo')

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



class TestSimplifiedRegexMatcher(TestRegexMatcher):
    MATCHER_CLASS = SimplifiedRegexMatcher

    def test_steps_with_same_prefix_are_not_ordering_sensitive(self):
        # -- RELATED-TO: issue #280
        # pylint: disable=unused-argument
        def step_func1(context): pass   # pylint: disable=multiple-statements
        def step_func2(context): pass   # pylint: disable=multiple-statements
        # pylint: enable=unused-argument
        matcher1 = SimplifiedRegexMatcher(step_func1, "I do something")
        matcher2 = SimplifiedRegexMatcher(step_func2, "I do something more")

        # -- CHECK: ORDERING SENSITIVITY
        matched1 = matcher1.match(matcher2.string)
        matched2 = matcher2.match(matcher1.string)
        assert matched1 is None
        assert matched2 is None

        # -- CHECK: Can match itself (if step text is simple)
        matched1 = matcher1.match(matcher1.string)
        matched2 = matcher2.match(matcher2.string)
        assert isinstance(matched1, Match)
        assert isinstance(matched2, Match)

    @raises(AssertionError)
    def test_step_should_not_use_regex_begin_marker(self):
        SimplifiedRegexMatcher(None, "^I do something")

    @raises(AssertionError)
    def test_step_should_not_use_regex_end_marker(self):
        SimplifiedRegexMatcher(None, "I do something$")

    @raises(AssertionError)
    def test_step_should_not_use_regex_begin_and_end_marker(self):
        SimplifiedRegexMatcher(None, "^I do something$")


class TestCucumberRegexMatcher(TestRegexMatcher):
    MATCHER_CLASS = CucumberRegexMatcher

    def test_steps_with_same_prefix_are_not_ordering_sensitive(self):
        # -- RELATED-TO: issue #280
        # pylint: disable=unused-argument
        def step_func1(context): pass   # pylint: disable=multiple-statements
        def step_func2(context): pass   # pylint: disable=multiple-statements
        # pylint: enable=unused-argument
        matcher1 = CucumberRegexMatcher(step_func1, "^I do something$")
        matcher2 = CucumberRegexMatcher(step_func2, "^I do something more$")

        # -- CHECK: ORDERING SENSITIVITY
        matched1 = matcher1.match(matcher2.string[1:-1])
        matched2 = matcher2.match(matcher1.string[1:-1])
        assert matched1 is None
        assert matched2 is None

        # -- CHECK: Can match itself (if step text is simple)
        matched1 = matcher1.match(matcher1.string[1:-1])
        matched2 = matcher2.match(matcher2.string[1:-1])
        assert isinstance(matched1, Match)
        assert isinstance(matched2, Match)

    def test_step_should_use_regex_begin_marker(self):
        CucumberRegexMatcher(None, "^I do something")

    def test_step_should_use_regex_end_marker(self):
        CucumberRegexMatcher(None, "I do something$")

    def test_step_should_use_regex_begin_and_end_marker(self):
        CucumberRegexMatcher(None, "^I do something$")


def test_step_matcher_current_matcher():
    current_matcher = matchers.current_matcher
    for name, klass in list(matchers.matcher_mapping.items()):
        matchers.use_step_matcher(name)
        matcher = matchers.get_matcher(lambda x: -x, 'foo')
        assert isinstance(matcher, klass)

    matchers.current_matcher = current_matcher
