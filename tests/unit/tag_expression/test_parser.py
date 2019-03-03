# -*- coding: UTF-8 -*-
# pylint: disable=bad-whitespace
"""
Unit tests for tag-expression parser.
"""

from __future__ import absolute_import, print_function
from behave.tag_expression.parser import TagExpressionParser, TagExpressionError
from cucumber_tag_expressions.parser import \
    Token, Associative, TokenType
import pytest


# -----------------------------------------------------------------------------
# TEST SUITE: Grammar
# -----------------------------------------------------------------------------
# SAME-AS: cucumber/tag-expressions/python/tests/unit/test_parser:TestToken
class TestToken(object):

    @pytest.mark.parametrize("token, expected", [
        (Token.OR, Associative.LEFT),
        (Token.AND, Associative.LEFT),
        (Token.NOT, Associative.RIGHT),
        (Token.OPEN_PARENTHESIS, None),
        (Token.CLOSE_PARENTHESIS, None),
    ])
    def test_assoc(self, token, expected):
        assert token.assoc is expected

    @pytest.mark.parametrize("token, expected", [
        (Token.OR,  TokenType.OPERATOR),
        (Token.AND, TokenType.OPERATOR),
        (Token.NOT, TokenType.OPERATOR),
        (Token.OPEN_PARENTHESIS,  TokenType.OPERAND),
        (Token.CLOSE_PARENTHESIS, TokenType.OPERAND),
    ])
    def test_token_type(self, token, expected):
        assert token.token_type == expected

    @pytest.mark.parametrize("token, expected", [
        (Token.OR,  True),
        (Token.AND, True),
        (Token.NOT, True),
        (Token.OPEN_PARENTHESIS,  False),
        (Token.CLOSE_PARENTHESIS, False),
    ])
    def test_is_operation(self, token, expected):
        assert token.is_operation == expected

    @pytest.mark.parametrize("token, expected", [
        (Token.OR,  True),
        (Token.AND, True),
        (Token.NOT, False),
        (Token.OPEN_PARENTHESIS,  False),
        (Token.CLOSE_PARENTHESIS, False),
    ])
    def test_is_binary(self, token, expected):
        assert token.is_binary == expected

    @pytest.mark.parametrize("token, expected", [
        (Token.OR,  False),
        (Token.AND, False),
        (Token.NOT, True),
        (Token.OPEN_PARENTHESIS,  False),
        (Token.CLOSE_PARENTHESIS, False),
    ])
    def test_is_unary(self, token, expected):
        assert token.is_unary == expected

    # or_  = ("or",   0, Associative.left)
    # and_ = ("and",  1, Associative.left)
    # not_ = ("not",  2, Associative.right)
    @pytest.mark.parametrize("token1, token2, expected", [
        (Token.OR,  Token.OR,  True),
        (Token.OR,  Token.AND, True),
        (Token.OR,  Token.NOT, True),
        (Token.AND, Token.AND, True),
        (Token.AND, Token.OR,  False),
        (Token.AND, Token.NOT, True),
        (Token.NOT, Token.NOT, False),
        (Token.NOT, Token.OR,  False),
        (Token.NOT, Token.AND, False),
    ])
    def test_has_lower_precedence_than(self, token1, token2, expected):
        assert token1.has_lower_precedence_than(token2) == expected

    @pytest.mark.parametrize("token1, token2, expected", [
        (Token.OR,  Token.OPEN_PARENTHESIS,  False),
        (Token.OR,  Token.CLOSE_PARENTHESIS, False),
        (Token.AND, Token.OPEN_PARENTHESIS,  False),
        (Token.AND, Token.CLOSE_PARENTHESIS, False),
        (Token.NOT, Token.OPEN_PARENTHESIS,  False),
        (Token.NOT, Token.CLOSE_PARENTHESIS, False),
    ])
    def test_has_lower_precedence_than__with_parens(self, token1, token2, expected):
        assert token1.has_lower_precedence_than(token2) == expected


# -----------------------------------------------------------------------------
# TEST SUITE: Parser
# -----------------------------------------------------------------------------
class TagExpressionParserTestBase(object):
    @staticmethod
    def assert_parse_expression_equals_expression_string(text, expected):
        parser = TagExpressionParser()
        expression = parser.parse(text)
        expression_text = str(expression)
        assert expected == expression_text

    @staticmethod
    def assert_parse_expression_equals_expression_repr(text, expected):
        parser = TagExpressionParser()
        expression = parser.parse(text)
        expression_text = repr(expression)
        assert expected == expression_text

    @staticmethod
    def assert_parse_with_error_contains_message(text, error_message):
        parser = TagExpressionParser()
        with pytest.raises(TagExpressionError) as exc_info:
            parser.parse(text)

        exc_text = exc_info.exconly()
        print(exc_text)
        assert error_message in exc_text


# SAME-AS: cucumber/tag-expressions/python/tests/unit/test_parser:TestTagExpressionParser
# HINT: Refactoring into TagExpressionParserTestBase is only done here.
class TestTagExpressionParser(TagExpressionParserTestBase):

    # -- TESTS FOR: TagExpressionParser.parse()
    correct_test_data = [
        ("a and b",     "( a and b )"),
        ("a or (b)",    "( a or b )"),
        ("not   a",     "not ( a )"),
        ("( a and b ) or ( c and d )", "( ( a and b ) or ( c and d ) )"),
        ("not a or b and not c or not d or e and f",
            "( ( ( not ( a ) or ( b and not ( c ) ) ) or not ( d ) ) or ( e and f ) )"),
    ]

    @pytest.mark.parametrize("text, expected", correct_test_data)
    def test_parse(self, text, expected):
        self.assert_parse_expression_equals_expression_string(text, expected)

    @pytest.mark.parametrize("text, expected", [
        ("(a)",         "a"),
        ("b",           "b"),
        ("(((((c)))))", "c"),
    ])
    def test_parse__with_one_literal(self, text, expected):
        self.assert_parse_expression_equals_expression_string(text, expected)

    @pytest.mark.parametrize("text", ["", "  ",])
    def test_parse__empty_is_always_true(self, text):
        self.assert_parse_expression_equals_expression_repr(text, "True_()")

    @pytest.mark.parametrize("text, expected", [
        ("a and b or c", "( ( a and b ) or c )"),
        ("a or b and c", "( a or ( b and c ) )"),
        ("a and b and c", "( ( a and b ) and c )"),
        ("a or b or c", "( ( a or b ) or c )"),
        ("a and not b", "( a and not ( b ) )"),
        ("a or not b",  "( a or not ( b ) )"),
        ("not a and b", "( not ( a ) and b )"),
        ("not a or b",  "( not ( a ) or b )"),
        ("not (a and b) or c", "( not ( ( a and b ) ) or c )"),
    ])
    def test_parse__ensure_precedence(self, text, expected):
        """Ensures that the operation precedence is parsed correctly."""
        self.assert_parse_expression_equals_expression_string(text, expected)

    @pytest.mark.parametrize("text, expected", [
        ("not not a",       "not ( not ( a ) )"),
        ("not not a and b", "( not ( not ( a ) ) and b )"),
    ])
    def test_parse__with_not_not(self, text, expected):
        self.assert_parse_expression_equals_expression_string(text, expected)

    # -- BAD CASES:
    @pytest.mark.parametrize("text, error_message", [
        ("( a and b ))",    "Missing '(': Too few open-parens"),
        ("( ( a and b )",   "Unclosed '(': Too many open-parens"),
    ])
    def test_parse__fails_with_unbalanced_parens(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, error_message", [
        ("a not ( and )", "Syntax error. Expected operator after a"),
    ])
    def test_parse__fails_with_missing_operation_args(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, error_message", [
        ("or or",  "Syntax error. Expected operand after BEGIN"),
    ])
    def test_parse__fails_with_only_operations(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, error_message", [
        ("a b", "Syntax error. Expected operator after a"),
    ])
    def test_parse__fails_for_args_without_operation(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, error_message", [
        ("(())",    "Syntax error. Expected operand after ("),
        ("(() ())", "Syntax error. Expected operand after ("),
    ])
    def test_parse__fails_for_empty_parens_groups(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, expected", [
        ("a b or",        "Syntax error. Expected operator after a"),
        ("a and (b not)", "Syntax error. Expected operator after b"),
        ("a and (b c) or", "Syntax error. Expected operator after b"),
    ])
    def test_parse__fails_with_rpn_notation(self, text, expected):
        # -- NOTE: RPN parsebility due to Shunting-yard algorithm (stack-based).
        self.assert_parse_with_error_contains_message(text, expected)


    # -- BAD CASES: Too few operands
    @pytest.mark.parametrize("text, error_message", [
        ("a and ",  "and: Too few operands"),
        ("  and b", "Syntax error. Expected operand after BEGIN"),
    ])
    def test_parse__fails_and_operation_with_too_few_args(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, error_message", [
        ("a or ",  "or: Too few operands"),
        ("  or b", "Syntax error. Expected operand after BEGIN"),
        ("a and b or ", "or: Too few operands"),
    ])
    def test_parse__fails_or_operation_with_too_few_args(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)

    @pytest.mark.parametrize("text, error_message", [
        ("not ",   "not: Too few operands"),
        ("not ()",       "Syntax error. Expected operand after ("),
        ("not () and b", "Syntax error. Expected operand after ("),
        ("not () or b",  "Syntax error. Expected operand after ("),
    ])
    def test_parse__fails_not_operation_with_too_few_args(self, text, error_message):
        self.assert_parse_with_error_contains_message(text, error_message)


    # -- OTHER TESTS:
    @pytest.mark.parametrize("text, expected", [
        ("or", Token.OR),
        ("and", Token.AND),
        ("not", Token.NOT),
        ("(", Token.OPEN_PARENTHESIS),
        (")", Token.CLOSE_PARENTHESIS),
        ("UNKNOWN", None),  # CASE: Literal
    ])
    def test_select_token(self, text, expected):
        token = TagExpressionParser.select_token(text)
        assert token is expected


# -----------------------------------------------------------------------------
# TEST SUITE: Parser Extension
# -----------------------------------------------------------------------------
class TestTagExpressionParserExt(TagExpressionParserTestBase):

    @pytest.mark.parametrize("text, expected", [
        ("a.*",             "Matcher('a.*')"),
        ("a.* or *.b ",     "Or(Matcher('a.*'), Matcher('*.b'))"),
        ("not a.* or b",    "Or(Not(Matcher('a.*')), Literal('b'))"),
        ("a or *.b",        "Or(Literal('a'), Matcher('*.b'))"),
    ])
    def test_parse__with_matcher(self, text, expected):
        """Ensures that the Matcher expressions are parsed correctly."""
        self.assert_parse_expression_equals_expression_repr(text, expected)

