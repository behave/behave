# -*- coding: utf-8 -*-
# pylint: disable=C0103,R0201,W0401,W0614,W0621
#   C0103   Invalid name (setUp(), ...)
#   R0201   Method could be a function
#   W0401   Wildcard import
#   W0614   Unused import ... from wildcard import
#   W0621   Redefining name ... from outer scope

from nose import tools
from behave.tag_expression import TagExpression
import unittest

class TestTagExpressionNoTags(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_empty_tags(self):
        assert self.e.check([])

class TestTagExpressionFoo(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])

    def test_should_not_match_no_tags(self):
        assert not self.e.check([])

class TestTagExpressionNotFoo(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['-foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_not_match_foo(self):
        assert not self.e.check(['foo'])

class TestTagExpressionFooOrBar(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo,bar'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_not_match_zap(self):
        assert not self.e.check(['zap'])

class TestTagExpressionFooOrBarAndNotZap(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['foo,bar', '-zap'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_foo_zap(self):
        assert not self.e.check(['foo', 'zap'])

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
        # pylint: disable=E1101
        #   E1101   Module nose.tools has no assert_raises member
        #           => But it works.
        tools.assert_raises(Exception, TagExpression, ['todo:3', '-todo:4'])

    def test_should_allow_duplicate_consistent_limits(self):
        e = TagExpression(['todo:3', '-todo:3'])
        tools.eq_(e.limits, {'todo': 3})

