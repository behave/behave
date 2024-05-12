"""
SEE: https://github.com/behave/behave/issues/1054
"""

from __future__ import absolute_import, print_function
from behave.__main__ import run_behave
from behave.configuration import Configuration
from behave.tag_expression.builder import make_tag_expression
import pytest
from assertpy import assert_that


def test_syndrome_with_core(capsys):
    """Verifies the problem with the core functionality."""
    cmdline_tags = ["fish or fries", "beer and water"]
    tag_expression = make_tag_expression(cmdline_tags)

    tag_expression_text1 = tag_expression.to_string()
    tag_expression_text2 = repr(tag_expression)
    expected1 = "((fish or fries) and (beer and water))"
    expected2 = "And(Or(Literal('fish'), Literal('fries')), And(Literal('beer'), Literal('water')))"
    assert tag_expression_text1 == expected1
    assert tag_expression_text2 == expected2


@pytest.mark.parametrize("tags_options", [
    ["--tags", "fish or fries", "--tags", "beer and water"],
    # ['--tags="fish or fries"', '--tags="beer and water"'],
    # ["--tags='fish or fries'", "--tags='beer and water'"],
])
def test_syndrome_functional(tags_options, capsys):
    """Verifies that the issue is fixed."""
    command_args = tags_options + ["--tags-help", "--verbose"]
    config = Configuration(command_args, load_config=False)
    run_behave(config)

    captured = capsys.readouterr()
    expected_part1 = "CURRENT TAG_EXPRESSION: ((fish or fries) and (beer and water))"
    expected_part2 = "means: And(Or(Tag('fish'), Tag('fries')), And(Tag('beer'), Tag('water')))"
    assert_that(captured.out).contains(expected_part1)
    assert_that(captured.out).contains(expected_part2)
