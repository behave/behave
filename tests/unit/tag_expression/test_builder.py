"""
Test if TagExpression protocol/version is detected correctly.
"""

import pytest
from behave.tag_expression.builder import TagExpressionProtocol, make_tag_expression
from behave.tag_expression.model import Expression as TagExpressionV2


# -----------------------------------------------------------------------------
# TEST DATA
# -----------------------------------------------------------------------------
# -- USED FOR: TagExpressionProtocol.AUTO_DETECT
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

# -- USED FOR: TagExpressionProtocol.V2
TAG_EXPRESSION_V2_GOOD_EXAMPLES = TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT


# -----------------------------------------------------------------------------
# TEST SUPPORT
# -----------------------------------------------------------------------------
def assert_is_tag_expression_v2(tag_expression):
    assert isinstance(tag_expression, TagExpressionV2), "%r" % tag_expression


# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
class TestTagExpressionProtocol:
    """
    Test TagExpressionProtocol class.
    """

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_parse_using_protocol_auto_detect_builds_v2(self, text):
        this_protocol = TagExpressionProtocol.AUTO_DETECT
        tag_expression = this_protocol.parse(text)
        assert_is_tag_expression_v2(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES)
    def test_parse_using_protocol_v2_builds_v2(self,  text):
        print("tag_expression: %s" % text)
        this_protocol = TagExpressionProtocol.V2
        tag_expression = this_protocol.parse(text)
        assert_is_tag_expression_v2(tag_expression)


# -----------------------------------------------------------------------------
# TEST SUITE FOR: make_tag_expression()
# -----------------------------------------------------------------------------
class TestMakeTagExpression:
    """Test :func:`make_tag_expression()`."""

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES)
    def test_with_protocol_v2(self,  text):
        tag_expression = make_tag_expression(text, TagExpressionProtocol.V2)
        assert_is_tag_expression_v2(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_protocol_auto_detect_for_v2(self,  text):
        tag_expression = make_tag_expression(text, TagExpressionProtocol.AUTO_DETECT)
        assert_is_tag_expression_v2(tag_expression)

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES)
    def test_with_default_protocol_v2(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.V2)
        tag_expression = make_tag_expression(text)
        assert_is_tag_expression_v2(tag_expression)
        assert TagExpressionProtocol.current() == TagExpressionProtocol.V2

    @pytest.mark.parametrize("text", TAG_EXPRESSION_V2_GOOD_EXAMPLES_FOR_AUTO_DETECT)
    def test_with_default_protocol_auto_and_tag_expression_v2(self,  text):
        TagExpressionProtocol.use(TagExpressionProtocol.AUTO_DETECT)
        tag_expression = make_tag_expression(text)
        assert_is_tag_expression_v2(tag_expression)
        assert TagExpressionProtocol.current() == TagExpressionProtocol.AUTO_DETECT
