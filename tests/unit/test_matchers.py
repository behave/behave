# -*- coding: UTF-8 -*-
# ruff: noqa: E731
from __future__ import absolute_import, with_statement
import pytest
from mock import Mock, patch
import parse
from behave.exception import NotSupportedWarning
from behave.matchers import (
    Match, Matcher,
    ParseMatcher, CFParseMatcher,
    RegexMatcher, SimplifiedRegexMatcher, CucumberRegexMatcher)
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
    STEP_MATCHER_CLASS = ParseMatcher

    def setUp(self):
        self.recorded_args = None

    def record_args(self, *args, **kwargs):
        self.recorded_args = (args, kwargs)

    def test_register_type__can_register_own_type_converters(self):
        def parse_number(text):
            return int(text)

        # -- EXPECT:
        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.clear_registered_types()
        this_matcher_class.register_type(Number=parse_number)
        assert this_matcher_class.has_registered_type("Number")

    def test_returns_none_if_parser_does_not_match(self):
        # pylint: disable=redefined-outer-name
        # REASON: parse
        this_matcher_class = self.STEP_MATCHER_CLASS
        matcher = this_matcher_class(None, 'a string')
        with patch.object(matcher.parser, 'parse') as parse:
            parse.return_value = None
            assert matcher.match('just a random step') is None

    def test_returns_arguments_based_on_matches(self):
        this_matcher_class = self.STEP_MATCHER_CLASS
        func = lambda x: -x
        matcher = this_matcher_class(func, 'foo')

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
            assert have == expected

    def test_named_arguments(self):
        this_matcher_class = self.STEP_MATCHER_CLASS
        text = "has a {string}, an {integer:d} and a {decimal:f}"
        matcher = this_matcher_class(self.record_args, text)
        context = runner.Context(Mock())

        m = matcher.match("has a foo, an 11 and a 3.14159")
        m.run(context)
        assert self.recorded_args, ((context,) == {
            'string': 'foo',
            'integer': 11,
            'decimal': 3.14159
        })

    def test_named_arguments_with_own_types(self):
        @parse.with_pattern(r"[A-Za-z][A-Za-z0-9_\-]*")
        def parse_word(text):
            return text.strip()

        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.register_type(Number=parse_number,
                                         Word=parse_word)

        pattern = "has a {word:Word}, a {number:Number}"
        matcher = this_matcher_class(self.record_args, pattern)
        context = runner.Context(Mock())

        m = matcher.match("has a foo, a 42")
        m.run(context)
        expected = {
            "word": "foo",
            "number": 42,
        }
        assert self.recorded_args, ((context,) == expected)


    def test_positional_arguments(self):
        this_matcher_class = self.STEP_MATCHER_CLASS
        text = "has a {}, an {:d} and a {:f}"
        matcher = this_matcher_class(self.record_args, text)
        context = runner.Context(Mock())

        m = matcher.match("has a foo, an 11 and a 3.14159")
        m.run(context)
        assert self.recorded_args == ((context, 'foo', 11, 3.14159), {})


class TestCFParseMatcher(TestParseMatcher):
    STEP_MATCHER_CLASS = CFParseMatcher

    # def test_
    def test_named_optional__without_value(self):
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.register_type(Number=parse_number)

        pattern = "has an optional number={number:Number?}."
        matcher = this_matcher_class(self.record_args, pattern)
        context = runner.Context(Mock())

        m = matcher.match("has an optional number=.")
        m.run(context)
        expected = {
            "number": None,
        }
        assert self.recorded_args, ((context,) == expected)


    def test_named_optional__with_value(self):
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.register_type(Number=parse_number)

        pattern = "has an optional number={number:Number?}."
        matcher = this_matcher_class(self.record_args, pattern)
        context = runner.Context(Mock())

        m = matcher.match("has an optional number=42.")
        m.run(context)
        expected = {
            "number": 42,
        }
        assert self.recorded_args, ((context,) == expected)

    def test_named_many__with_values(self):
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.register_type(Number=parse_number)

        pattern = "has numbers={number:Number+};"
        matcher = this_matcher_class(self.record_args, pattern)
        context = runner.Context(Mock())

        m = matcher.match("has numbers=1, 2, 3;")
        m.run(context)
        expected = {
            "numbers": [1, 2, 3],
        }
        assert self.recorded_args, ((context,) == expected)

    def test_named_many0__with_empty_list(self):
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.register_type(Number=parse_number)

        pattern = "has numbers={number:Number*};"
        matcher = this_matcher_class(self.record_args, pattern)
        context = runner.Context(Mock())

        m = matcher.match("has numbers=;")
        m.run(context)
        expected = {
            "numbers": [],
        }
        assert self.recorded_args, ((context,) == expected)


    def test_named_many0__with_values(self):
        @parse.with_pattern(r"\d+")
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        this_matcher_class.register_type(Number=parse_number)

        pattern = "has numbers={number:Number+};"
        matcher = this_matcher_class(self.record_args, pattern)
        context = runner.Context(Mock())

        m = matcher.match("has numbers=1, 2, 3;")
        m.run(context)
        expected = {
            "numbers": [1, 2, 3],
        }
        assert self.recorded_args, ((context,) == expected)


class TestRegexMatcher(object):
    # pylint: disable=invalid-name, no-self-use
    STEP_MATCHER_CLASS = RegexMatcher

    def test_register_type__is_not_supported(self):
        def parse_number(text):
            return int(text)

        this_matcher_class = self.STEP_MATCHER_CLASS
        with pytest.raises(NotSupportedWarning) as exc_info:
            this_matcher_class.register_type(Number=parse_number)

        excecption_text = exc_info.exconly()
        class_name = this_matcher_class.__name__
        expected = "NotSupportedWarning: {0}.register_type".format(class_name)
        assert expected in excecption_text

    def test_returns_none_if_regex_does_not_match(self):
        this_matcher_class = self.STEP_MATCHER_CLASS
        matcher = this_matcher_class(None, 'a string')
        regex = Mock()
        regex.match.return_value = None
        matcher.regex = regex
        assert matcher.match('just a random step') is None

    def test_returns_arguments_based_on_groups(self):
        this_matcher_class = self.STEP_MATCHER_CLASS
        func = lambda x: -x
        matcher = this_matcher_class(func, 'foo')

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
        assert have == expected



class TestSimplifiedRegexMatcher(TestRegexMatcher):
    STEP_MATCHER_CLASS = SimplifiedRegexMatcher

    def test_steps_with_same_prefix_are_not_ordering_sensitive(self):
        # -- RELATED-TO: issue #280
        # pylint: disable=unused-argument
        def step_func1(context): pass   # pylint: disable=multiple-statements
        def step_func2(context): pass   # pylint: disable=multiple-statements
        # pylint: enable=unused-argument
        text1 = u"I do something"
        text2 = u"I do something more"
        matcher1 = SimplifiedRegexMatcher(step_func1, text1)
        matcher2 = SimplifiedRegexMatcher(step_func2, text2)

        # -- CHECK: ORDERING SENSITIVITY
        matched1 = matcher1.match(text2)
        matched2 = matcher2.match(text1)
        assert matched1 is None
        assert matched2 is None

        # -- CHECK: Can match itself (if step text is simple)
        matched1 = matcher1.match(text1)
        matched2 = matcher2.match(text2)
        assert isinstance(matched1, Match)
        assert isinstance(matched2, Match)

    def test_step_should_not_use_regex_begin_marker(self):
        with pytest.raises(ValueError):
            SimplifiedRegexMatcher(None, "^I do something")

    def test_step_should_not_use_regex_end_marker(self):
        with pytest.raises(ValueError):
            SimplifiedRegexMatcher(None, "I do something$")

    def test_step_should_not_use_regex_begin_and_end_marker(self):
        with pytest.raises(ValueError):
            SimplifiedRegexMatcher(None, "^I do something$")


class TestCucumberRegexMatcher(TestRegexMatcher):
    STEP_MATCHER_CLASS = CucumberRegexMatcher

    def test_steps_with_same_prefix_are_not_ordering_sensitive(self):
        # -- RELATED-TO: issue #280
        # pylint: disable=unused-argument
        def step_func1(context): pass   # pylint: disable=multiple-statements
        def step_func2(context): pass   # pylint: disable=multiple-statements
        # pylint: enable=unused-argument
        matcher1 = CucumberRegexMatcher(step_func1, "^I do something$")
        matcher2 = CucumberRegexMatcher(step_func2, "^I do something more$")
        text1 = matcher1.pattern[1:-1]
        text2 = matcher2.pattern[1:-1]

        # -- CHECK: ORDERING SENSITIVITY
        matched1 = matcher1.match(text2)
        matched2 = matcher2.match(text1)
        assert matched1 is None
        assert matched2 is None

        # -- CHECK: Can match itself (if step text is simple)
        matched1 = matcher1.match(text1)
        matched2 = matcher2.match(text2)
        assert isinstance(matched1, Match)
        assert isinstance(matched2, Match)

    def test_step_should_use_regex_begin_marker(self):
        CucumberRegexMatcher(None, "^I do something")

    def test_step_should_use_regex_end_marker(self):
        CucumberRegexMatcher(None, "I do something$")

    def test_step_should_use_regex_begin_and_end_marker(self):
        CucumberRegexMatcher(None, "^I do something$")


def test_step_matcher_current_matcher():
    step_matcher_factory = matchers.get_step_matcher_factory()
    for name, klass in list(step_matcher_factory.step_matcher_class_mapping.items()):
        current_matcher1 = matchers.use_step_matcher(name)
        current_matcher2 = step_matcher_factory.current_matcher
        matcher = matchers.make_step_matcher(lambda x: -x, "foo")
        assert isinstance(matcher, klass)
        assert current_matcher1 is klass
        assert current_matcher2 is klass

    # -- CLEANUP: Revert to default matcher
    step_matcher_factory.use_default_step_matcher()
