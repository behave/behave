"""
Test if TagExpression protocol/version is detected correctly.
"""

from __future__ import absolute_import, print_function
import pytest
from behave.tag_expression.builder import TagExpressionProtocol, make_tag_expression
from behave.tag_expression.v1 import TagExpression as TagExpressionV1
from behave.tag_expression.model import Expression as TagExpressionV2
from behave.tag_expression.parser import TagExpressionError as TagExpressionError


# -----------------------------------------------------------------------------
# TEST DATA
# -----------------------------------------------------------------------------
# -- USED FOR: TagExpressionProtocol.AUTO_DETECT
TAG_EXPRESSION_V1_GOOD_EXAMPLES_FOR_AUTO_DETECT = [
    "@a,@b",
    "@a @b",
    "-@a",
    "~@a",
]
TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT = [
    "@a",
    "@a.*",
    "@dashed-tag",
    "@a and @b",
    "@a or @b",
    "@a or (@b and @c)",
    "not @a",
]
# -- CHECK-SOME: Mixtures of TagExpression v1 and v2
TAG_EXPRESSION_V2_BAD_EXAMPLES_FOR_AUTO_DETECT = [
    "-@a and @b",
    "@a and -@b",
    "~@a or @b",
    "@a or ~@b",
    "@a and not -@b",
]

# -- USED FOR: TagExpressionProtocol.V1
TAG_EXPRESSION_V1_GOOD_EXAMPLES = [
    "@a",
    "@one-and-more",
] + TAG_EXPRESSION_V1_GOOD_EXAMPLES_FOR_AUTO_DETECT

# -- USED FOR: TagExpressionProtocol.V2
TAG_EXPRESSION_V2_GOOD_EXAMPLES = TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def assert_is_tag_expression_v1(tag_expression):
    assert isinstance(tag_expression, TagExpressionV1), "%r" % tag_expression


def assert_is_tag_expression_v2(tag_expression):
    assert isinstance(tag_expression, TagExpressionV2), "%r" % tag_expression


def assert_is_tag_expression_for_protocol(tag_expression, expected_tag_expression_protocol):
    # -- STEP 1: Select assert-function
    def assert_false(tag_expression):
        assert False, "UNEXPECTED: %r (for: %s)" % \
                      (expected_tag_expression_protocol, tag_expression)

    assert_func = assert_false
    if expected_tag_expression_protocol is TagExpressionProtocol.V1:
        assert_func = assert_is_tag_expression_v1
    elif expected_tag_expression_protocol is TagExpressionProtocol.V2:
        assert_func = assert_is_tag_expression_v2

    # -- STEP 2: Apply assert-function
    assert_func(tag_expression)


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestTagExpressionProtocol(object):
    """
    Test TagExpressionProtocol class.
    """

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V1_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_parse_using_protocol_auto_detect_builds_v1(self, text):
        this_protocol = TagExpressionProtocol.AUTO_DETECT
        tag_expression = this_protocol.parse(text)
        assert_is_tag_expression_v1(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_parse_using_protocol_auto_detect_builds_v2(self, text):
        this_protocol = TagExpressionProtocol.AUTO_DETECT
        tag_expression = this_protocol.parse(text)
        assert_is_tag_expression_v2(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_BAD_EXAMPLES_FOR_AUTO_DETECT)
    def test_parse_using_protocol_auto_detect_raises_error_if_v1_and_v2_are_used(self, text):
        this_protocol = TagExpressionProtocol.AUTO_DETECT
        with pytest.raises(TagExpressionError) as e:
            _tag_expression = this_protocol.parse(text)

        print("CAUGHT-EXCEPTION: %s" % e.value)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V1_GOOD_EXAMPLES)
    def test_parse_using_protocol_v1_builds_v1(self,  text):
        print("tag_expression: %s" % text)
        this_protocol = TagExpressionProtocol.V1
        tag_expression = this_protocol.parse(text)
        assert_is_tag_expression_v1(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES)
    def test_parse_using_protocol_v2_builds_v2(self,  text):
        print("tag_expression: %s" % text)
        this_protocol = TagExpressionProtocol.V2
        tag_expression = this_protocol.parse(text)
        assert_is_tag_expression_v2(tag_expression)


# -----------------------------------------------------------------------------
# TEST SUITE FOR: make_tag_expression()
# -----------------------------------------------------------------------------
class TestMakeTagExpression(object):
    """Test :func:`make_tag_expression()`."""

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V1_GOOD_EXAMPLES)
    def test_with_protocol_v1(self,  text):
        tag_expression = make_tag_expression(text, TagExpressionProtocol.V1)
        assert_is_tag_expression_v1(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES)
    def test_with_protocol_v2(self,  text):
        tag_expression = make_tag_expression(text, TagExpressionProtocol.V2)
        assert_is_tag_expression_v2(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V1_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_protocol_auto_detect_for_v1(self,  text):
        tag_expression = make_tag_expression(text, TagExpressionProtocol.AUTO_DETECT)
        assert_is_tag_expression_v1(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_protocol_auto_detect_for_v2(self,  text):
        tag_expression = make_tag_expression(text, TagExpressionProtocol.AUTO_DETECT)
        assert_is_tag_expression_v2(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V1_GOOD_EXAMPLES)
    def test_with_default_protocol_v1(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.V1)
        tag_expression = make_tag_expression(text)
        assert_is_tag_expression_v1(tag_expression)
        assert TagExpressionProtocol.current() == TagExpressionProtocol.V1

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES)
    def test_with_default_protocol_v2(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.V2)
        tag_expression = make_tag_expression(text)
        assert_is_tag_expression_v2(tag_expression)
        assert TagExpressionProtocol.current() == TagExpressionProtocol.V2

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V1_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_default_protocol_auto_and_tag_expression_v1(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.AUTO_DETECT)
        tag_expression = make_tag_expression(text)
        assert_is_tag_expression_for_protocol(tag_expression, TagExpressionProtocol.V1)
        assert TagExpressionProtocol.current() == TagExpressionProtocol.AUTO_DETECT

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_default_protocol_auto_and_tag_expression_v2(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.AUTO_DETECT)
        tag_expression = make_tag_expression(text)
        assert_is_tag_expression_for_protocol(tag_expression, TagExpressionProtocol.V2)
        assert TagExpressionProtocol.current() == TagExpressionProtocol.AUTO_DETECT

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_BAD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_default_protocol_auto_and_bad_tag_expression_with_v1_and_v2(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.AUTO_DETECT)
        with pytest.raises(TagExpressionError) as e:
            _tag_expression = make_tag_expression(text)

        print("CAUGHT-EXCEPTION: %s" % e.value)
