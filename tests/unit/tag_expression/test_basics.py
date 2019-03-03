# -*- coding: UTF-8 -*-

from behave.tag_expression import (
    make_tag_expression, select_tag_expression_parser,
    parse_tag_expression_v1, parse_tag_expression_v2
)
from behave.tag_expression.v1 import TagExpression as TagExpressionV1
from behave.tag_expression.model_ext import Expression as TagExpressionV2
import pytest

# -----------------------------------------------------------------------------
# TEST SUITE FOR: make_tag_expression()
# -----------------------------------------------------------------------------
def test_make_tag_expression__with_v1():
    pass

def test_make_tag_expression__with_v2():
    pass


# -----------------------------------------------------------------------------
# TEST SUITE FOR: select_tag_expression_parser()
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "@foo @bar",
    "foo bar",
    "-foo",
    "~foo",
    "-@foo",
    "~@foo",
    "@foo,@bar",
    "-@xfail -@not_implemented",
])
def test_select_tag_expression_parser__with_v1(text):
    parser = select_tag_expression_parser(text)
    assert parser is parse_tag_expression_v1, "tag_expression: %s" % text


@pytest.mark.parametrize("text", [
    "@foo",
    "foo",
    "not foo",
    "foo and bar",
    "@foo or @bar",
    "(@foo and @bar) or @baz",
    "not @xfail or not @not_implemented"
])
def test_select_tag_expression_parser__with_v2(text):
    parser = select_tag_expression_parser(text)
    assert parser is parse_tag_expression_v2, "tag_expression: %s" % text
