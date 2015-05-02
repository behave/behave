# -*- coding: utf-8 -*-

from __future__ import absolute_import
from behave.tag_expression import TagExpression
from nose import tools
import unittest


# ----------------------------------------------------------------------------
# BASIC TESTS: 0..1 tags, not @tag
# ----------------------------------------------------------------------------
class TestTagExpressionNoTags(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression([])

    def test_should_match_empty_tags(self):
        assert self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])


class TestTagExpressionFoo(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo'])

    def test_should_not_match_no_tags(self):
        assert not self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])


class TestTagExpressionNotFoo(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['-foo'])

    def test_should_match_no_tags(self):
        assert self.e.check([])

    def test_should_not_match_foo(self):
        assert not self.e.check(['foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])


# ----------------------------------------------------------------------------
# LOGICAL-AND TESTS: With @foo, @bar (2 tags)
# ----------------------------------------------------------------------------
class TestTagExpressionFooAndBar(unittest.TestCase):
    # -- LOGIC: @foo and @bar

    def setUp(self):
        self.e = TagExpression(['foo', 'bar'])

    def test_should_not_match_no_tags(self):
        assert not self.e.check([])

    def test_should_not_match_foo(self):
        assert not self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])

    def test_should_not_match_other(self):
        assert not self.e.check(['other'])

    def test_should_match_foo_bar(self):
        assert self.e.check(['foo', 'bar'])
        assert self.e.check(['bar', 'foo'])

    def test_should_not_match_foo_other(self):
        assert not self.e.check(['foo', 'other'])
        assert not self.e.check(['other', 'foo'])

    def test_should_not_match_bar_other(self):
        assert not self.e.check(['bar', 'other'])
        assert not self.e.check(['other', 'bar'])

    def test_should_not_match_zap_other(self):
        assert not self.e.check(['zap', 'other'])
        assert not self.e.check(['other', 'zap'])

    def test_should_match_foo_bar_other(self):
        assert self.e.check(['foo', 'bar', 'other'])
        assert self.e.check(['bar', 'other', 'foo'])
        assert self.e.check(['other', 'bar', 'foo'])

    def test_should_not_match_foo_zap_other(self):
        assert not self.e.check(['foo', 'zap', 'other'])
        assert not self.e.check(['other', 'zap', 'foo'])

    def test_should_not_match_bar_zap_other(self):
        assert not self.e.check(['bar', 'zap', 'other'])
        assert not self.e.check(['other', 'bar', 'zap'])

    def test_should_not_match_zap_baz_other(self):
        assert not self.e.check(['zap', 'baz', 'other'])
        assert not self.e.check(['baz', 'other', 'baz'])
        assert not self.e.check(['other', 'baz', 'zap'])


class TestTagExpressionFooAndNotBar(unittest.TestCase):
    # -- LOGIC: @foo and not @bar

    def setUp(self):
        self.e = TagExpression(['foo', '-bar'])

    def test_should_not_match_no_tags(self):
        assert not self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])

    def test_should_not_match_other(self):
        assert not self.e.check(['other'])

    def test_should_not_match_foo_bar(self):
        assert not self.e.check(['foo', 'bar'])
        assert not self.e.check(['bar', 'foo'])

    def test_should_match_foo_other(self):
        assert self.e.check(['foo', 'other'])
        assert self.e.check(['other', 'foo'])

    def test_should_not_match_bar_other(self):
        assert not self.e.check(['bar', 'other'])
        assert not self.e.check(['other', 'bar'])

    def test_should_not_match_zap_other(self):
        assert not self.e.check(['bar', 'other'])
        assert not self.e.check(['other', 'bar'])

    def test_should_not_match_foo_bar_other(self):
        assert not self.e.check(['foo', 'bar', 'other'])
        assert not self.e.check(['bar', 'other', 'foo'])
        assert not self.e.check(['other', 'bar', 'foo'])

    def test_should_match_foo_zap_other(self):
        assert self.e.check(['foo', 'zap', 'other'])
        assert self.e.check(['other', 'zap', 'foo'])

    def test_should_not_match_bar_zap_other(self):
        assert not self.e.check(['bar', 'zap', 'other'])
        assert not self.e.check(['other', 'bar', 'zap'])

    def test_should_not_match_zap_baz_other(self):
        assert not self.e.check(['zap', 'baz', 'other'])
        assert not self.e.check(['baz', 'other', 'baz'])
        assert not self.e.check(['other', 'baz', 'zap'])


class TestTagExpressionNotBarAndFoo(TestTagExpressionFooAndNotBar):
    # -- REUSE: Test suite due to symmetry in reversed expression
    # LOGIC: not @bar and @foo == @foo and not @bar

    def setUp(self):
        self.e = TagExpression(['-bar', 'foo'])


class TestTagExpressionNotFooAndNotBar(unittest.TestCase):
    # -- LOGIC: not @bar and not @foo

    def setUp(self):
        self.e = TagExpression(['-foo', '-bar'])

    def test_should_match_no_tags(self):
        assert self.e.check([])

    def test_should_not_match_foo(self):
        assert not self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])

    def test_should_match_other(self):
        assert self.e.check(['other'])

    def test_should_not_match_foo_bar(self):
        assert not self.e.check(['foo', 'bar'])
        assert not self.e.check(['bar', 'foo'])

    def test_should_not_match_foo_other(self):
        assert not self.e.check(['foo', 'other'])
        assert not self.e.check(['other', 'foo'])

    def test_should_not_match_bar_other(self):
        assert not self.e.check(['bar', 'other'])
        assert not self.e.check(['other', 'bar'])

    def test_should_match_zap_other(self):
        assert self.e.check(['zap', 'other'])
        assert self.e.check(['other', 'zap'])

    def test_should_not_match_foo_bar_other(self):
        assert not self.e.check(['foo', 'bar', 'other'])
        assert not self.e.check(['bar', 'other', 'foo'])
        assert not self.e.check(['other', 'bar', 'foo'])

    def test_should_not_match_foo_zap_other(self):
        assert not self.e.check(['foo', 'zap', 'other'])
        assert not self.e.check(['other', 'zap', 'foo'])

    def test_should_not_match_bar_zap_other(self):
        assert not self.e.check(['bar', 'zap', 'other'])
        assert not self.e.check(['other', 'bar', 'zap'])

    def test_should_match_zap_baz_other(self):
        assert self.e.check(['zap', 'baz', 'other'])
        assert self.e.check(['baz', 'other', 'baz'])
        assert self.e.check(['other', 'baz', 'zap'])


class TestTagExpressionNotBarAndNotFoo(TestTagExpressionNotFooAndNotBar):
    # -- REUSE: Test suite due to symmetry in reversed expression
    # LOGIC: not @bar and not @foo == not @foo and not @bar

    def setUp(self):
        self.e = TagExpression(['-bar', '-foo'])


# ----------------------------------------------------------------------------
# LOGICAL-OR TESTS: With @foo, @bar (2 tags)
# ----------------------------------------------------------------------------
class TestTagExpressionFooOrBar(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo,bar'])

    def test_should_not_match_no_tags(self):
        assert not self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_not_match_other(self):
        assert not self.e.check(['other'])

    def test_should_match_foo_bar(self):
        assert self.e.check(['foo', 'bar'])
        assert self.e.check(['bar', 'foo'])

    def test_should_match_foo_other(self):
        assert self.e.check(['foo', 'other'])
        assert self.e.check(['other', 'foo'])

    def test_should_match_bar_other(self):
        assert self.e.check(['bar', 'other'])
        assert self.e.check(['other', 'bar'])

    def test_should_not_match_zap_other(self):
        assert not self.e.check(['zap', 'other'])
        assert not self.e.check(['other', 'zap'])

    def test_should_match_foo_bar_other(self):
        assert self.e.check(['foo', 'bar', 'other'])
        assert self.e.check(['bar', 'other', 'foo'])
        assert self.e.check(['other', 'bar', 'foo'])

    def test_should_match_foo_zap_other(self):
        assert self.e.check(['foo', 'zap', 'other'])
        assert self.e.check(['other', 'zap', 'foo'])

    def test_should_match_bar_zap_other(self):
        assert self.e.check(['bar', 'zap', 'other'])
        assert self.e.check(['other', 'bar', 'zap'])

    def test_should_not_match_zap_baz_other(self):
        assert not self.e.check(['zap', 'baz', 'other'])
        assert not self.e.check(['baz', 'other', 'baz'])
        assert not self.e.check(['other', 'baz', 'zap'])


class TestTagExpressionBarOrFoo(TestTagExpressionFooOrBar):
    # -- REUSE: Test suite due to symmetry in reversed expression
    # LOGIC: @bar or @foo == @foo or @bar
    def setUp(self):
        self.e = TagExpression(['bar,foo'])


class TestTagExpressionFooOrNotBar(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo,-bar'])

    def test_should_match_no_tags(self):
        assert self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])

    def test_should_match_other(self):
        assert self.e.check(['other'])

    def test_should_match_foo_bar(self):
        assert self.e.check(['foo', 'bar'])
        assert self.e.check(['bar', 'foo'])

    def test_should_match_foo_other(self):
        assert self.e.check(['foo', 'other'])
        assert self.e.check(['other', 'foo'])

    def test_should_not_match_bar_other(self):
        assert not self.e.check(['bar', 'other'])
        assert not self.e.check(['other', 'bar'])

    def test_should_match_zap_other(self):
        assert self.e.check(['zap', 'other'])
        assert self.e.check(['other', 'zap'])

    def test_should_match_foo_bar_other(self):
        assert self.e.check(['foo', 'bar', 'other'])
        assert self.e.check(['bar', 'other', 'foo'])
        assert self.e.check(['other', 'bar', 'foo'])

    def test_should_match_foo_zap_other(self):
        assert self.e.check(['foo', 'zap', 'other'])
        assert self.e.check(['other', 'zap', 'foo'])

    def test_should_not_match_bar_zap_other(self):
        assert not self.e.check(['bar', 'zap', 'other'])
        assert not self.e.check(['other', 'bar', 'zap'])

    def test_should_match_zap_baz_other(self):
        assert self.e.check(['zap', 'baz', 'other'])
        assert self.e.check(['baz', 'other', 'baz'])
        assert self.e.check(['other', 'baz', 'zap'])


class TestTagExpressionNotBarOrFoo(TestTagExpressionFooOrNotBar):
    # -- REUSE: Test suite due to symmetry in reversed expression
    # LOGIC: not @bar or @foo == @foo or not @bar
    def setUp(self):
        self.e = TagExpression(['-bar,foo'])


class TestTagExpressionNotFooOrNotBar(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['-foo,-bar'])

    def test_should_match_no_tags(self):
        assert self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_match_other(self):
        assert self.e.check(['other'])

    def test_should_not_match_foo_bar(self):
        assert not self.e.check(['foo', 'bar'])
        assert not self.e.check(['bar', 'foo'])

    def test_should_match_foo_other(self):
        assert self.e.check(['foo', 'other'])
        assert self.e.check(['other', 'foo'])

    def test_should_match_bar_other(self):
        assert self.e.check(['bar', 'other'])
        assert self.e.check(['other', 'bar'])

    def test_should_match_zap_other(self):
        assert self.e.check(['zap', 'other'])
        assert self.e.check(['other', 'zap'])

    def test_should_not_match_foo_bar_other(self):
        assert not self.e.check(['foo', 'bar', 'other'])
        assert not self.e.check(['bar', 'other', 'foo'])
        assert not self.e.check(['other', 'bar', 'foo'])

    def test_should_match_foo_zap_other(self):
        assert self.e.check(['foo', 'zap', 'other'])
        assert self.e.check(['other', 'zap', 'foo'])

    def test_should_match_bar_zap_other(self):
        assert self.e.check(['bar', 'zap', 'other'])
        assert self.e.check(['other', 'bar', 'zap'])

    def test_should_match_zap_baz_other(self):
        assert self.e.check(['zap', 'baz', 'other'])
        assert self.e.check(['baz', 'other', 'baz'])
        assert self.e.check(['other', 'baz', 'zap'])


class TestTagExpressionNotBarOrNotFoo(TestTagExpressionNotFooOrNotBar):
    # -- REUSE: Test suite due to symmetry in reversed expression
    # LOGIC: not @bar or @foo == @foo or not @bar
    def setUp(self):
        self.e = TagExpression(['-bar,-foo'])


# ----------------------------------------------------------------------------
# MORE TESTS: With 3 tags
# ----------------------------------------------------------------------------
class TestTagExpressionFooOrBarAndNotZap(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo,bar', '-zap'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_foo_zap(self):
        assert not self.e.check(['foo', 'zap'])

    def test_should_not_match_tags(self):
        assert not self.e.check([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_not_match_other(self):
        assert not self.e.check(['other'])

    def test_should_match_foo_bar(self):
        assert self.e.check(['foo', 'bar'])
        assert self.e.check(['bar', 'foo'])

    def test_should_match_foo_other(self):
        assert self.e.check(['foo', 'other'])
        assert self.e.check(['other', 'foo'])

    def test_should_match_bar_other(self):
        assert self.e.check(['bar', 'other'])
        assert self.e.check(['other', 'bar'])

    def test_should_not_match_zap_other(self):
        assert not self.e.check(['zap', 'other'])
        assert not self.e.check(['other', 'zap'])

    def test_should_match_foo_bar_other(self):
        assert self.e.check(['foo', 'bar', 'other'])
        assert self.e.check(['bar', 'other', 'foo'])
        assert self.e.check(['other', 'bar', 'foo'])

    def test_should_not_match_foo_bar_zap(self):
        assert not self.e.check(['foo', 'bar', 'zap'])
        assert not self.e.check(['bar', 'zap', 'foo'])
        assert not self.e.check(['zap', 'bar', 'foo'])

    def test_should_not_match_foo_zap_other(self):
        assert not self.e.check(['foo', 'zap', 'other'])
        assert not self.e.check(['other', 'zap', 'foo'])

    def test_should_not_match_bar_zap_other(self):
        assert not self.e.check(['bar', 'zap', 'other'])
        assert not self.e.check(['other', 'bar', 'zap'])

    def test_should_not_match_zap_baz_other(self):
        assert not self.e.check(['zap', 'baz', 'other'])
        assert not self.e.check(['baz', 'other', 'baz'])
        assert not self.e.check(['other', 'baz', 'zap'])


# ----------------------------------------------------------------------------
# TESTS WITH LIMIT
# ----------------------------------------------------------------------------
class TestTagExpressionFoo3OrNotBar4AndZap5(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo:3,-bar', 'zap:5'])

    def test_should_count_tags_for_positive_tags(self):
        tools.eq_(self.e.limits, {'foo': 3, 'zap': 5})

    def test_should_match_foo_zap(self):
        assert self.e.check(['foo', 'zap'])

class TestTagExpressionParsing(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression([' foo:3 , -bar ', ' zap:5 '])

    def test_should_have_limits(self):
        tools.eq_(self.e.limits, {'zap': 5, 'foo': 3})

class TestTagExpressionTagLimits(unittest.TestCase):
    def test_should_be_counted_for_negative_tags(self):
        e = TagExpression(['-todo:3'])
        tools.eq_(e.limits, {'todo': 3})

    def test_should_be_counted_for_positive_tags(self):
        e = TagExpression(['todo:3'])
        tools.eq_(e.limits, {'todo': 3})

    def test_should_raise_an_error_for_inconsistent_limits(self):
        tools.assert_raises(Exception, TagExpression, ['todo:3', '-todo:4'])

    def test_should_allow_duplicate_consistent_limits(self):
        e = TagExpression(['todo:3', '-todo:3'])
        tools.eq_(e.limits, {'todo': 3})

