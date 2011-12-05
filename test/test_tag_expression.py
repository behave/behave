from nose import tools

from behave.tag_expression import TagExpression

class TestTagExpressionNoTags(object):
    def setUp(self):
        self.e = TagExpression([])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_empty_tags(self):
        assert self.e.check([])

class TestTagExpressionFoo(object):
    def setUp(self):
        self.e = TagExpression(['foo'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_bar(self):
        assert not self.e.check(['bar'])

    def test_should_not_match_no_tags(self):
        assert not self.e.check([])

class TestTagExpressionNotFoo(object):
    def setUp(self):
        self.e = TagExpression(['-foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_not_match_foo(self):
        assert not self.e.check(['foo'])

class TestTagExpressionFooOrBar(object):
    def setUp(self):
        self.e = TagExpression(['foo,bar'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_match_bar(self):
        assert self.e.check(['bar'])

    def test_should_not_match_zap(self):
        assert not self.e.check(['zap'])

class TestTagExpressionFooOrBarAndNotZap(object):
    def setUp(self):
        self.e = TagExpression(['foo,bar', '-zap'])

    def test_should_match_foo(self):
        assert self.e.check(['foo'])

    def test_should_not_match_foo_zap(self):
        assert not self.e.check(['foo', 'zap'])

class TestTagExpressionFoo3OrNotBar4AndZap5(object):
    def setUp(self):
        self.e = TagExpression(['foo:3,-bar', 'zap:5'])

    def test_should_count_tags_for_positive_tags(self):
        tools.eq_(self.e.limits, {'foo': 3, 'zap': 5})

    def test_should_match_foo_zap(self):
        assert self.e.check(['foo', 'zap'])

class TestTagExpressionParsing(object):
    def setUp(self):
        self.e = TagExpression([' foo:3 , -bar ', ' zap:5 '])

    def test_should_have_limits(self):
        tools.eq_(self.e.limits, {'zap': 5, 'foo': 3})

class TestTagExpressionTagLimits(object):
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

